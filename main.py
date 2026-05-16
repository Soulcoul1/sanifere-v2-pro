from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
import bcrypt
import os
from bson import ObjectId
import anthropic
import base64
from enum import Enum

# ==================== CONFIGURATION ====================
SECRET_KEY = os.getenv("SECRET_KEY", "votre-cle-secrete-production")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_NAME = "sanifere_v2"

app = FastAPI(
    title="SANI-FÉRÉ PRO API",
    description="Marketplace malien haute performance - Achat/Vente avec IA",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
db_client = None
db = None

security = HTTPBearer()

# ==================== ENUMS ====================
class CategorieType(str, Enum):
    ELECTRONIQUE = "Électronique"
    MODE = "Mode & Vêtements"
    MAISON = "Maison & Jardin"
    VEHICULES = "Véhicules"
    IMMOBILIER = "Immobilier"
    EMPLOI = "Emploi & Services"
    LOISIRS = "Loisirs & Divertissement"
    MATERIEL_PRO = "Matériel Professionnel"
    AUTRES = "Autres"

class StatutProduit(str, Enum):
    DISPONIBLE = "disponible"
    VENDU = "vendu"
    RESERVE = "réservé"
    SUPPRIME = "supprimé"

class ModePaiement(str, Enum):
    ORANGE_MONEY = "Orange Money"
    WAVE = "Wave"
    MOOV_MONEY = "Moov Money"
    CASH = "Espèces"
    VIREMENT = "Virement bancaire"

# ==================== MODELS ====================
class UtilisateurBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telephone: str = Field(..., pattern=r"^\+223[0-9]{8}$|^[0-9]{8}$")
    ville: str = Field(default="Bamako")
    quartier: Optional[str] = None

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str = Field(..., min_length=6)
    code_parrainage: Optional[str] = None

class UtilisateurLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str

class ProduitBase(BaseModel):
    titre: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    prix: int = Field(..., gt=0)  # Prix en FCFA
    categorie: CategorieType
    ville: str = Field(default="Bamako")
    quartier: Optional[str] = None
    negociable: bool = Field(default=True)
    etat: str = Field(default="Bon état")  # Neuf, Très bon état, Bon état, État correct

class ProduitCreate(ProduitBase):
    images_base64: List[str] = Field(default=[], max_items=8)

class MessageChatbot(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None

class ConversationChatbot(BaseModel):
    utilisateur_id: Optional[str] = None
    messages: List[dict] = []
    date_creation: datetime = Field(default_factory=datetime.utcnow)
    date_modification: datetime = Field(default_factory=datetime.utcnow)

# ==================== DATABASE HELPERS ====================
async def get_db():
    global db_client, db
    if db_client is None:
        db_client = AsyncIOMotorClient(MONGODB_URI)
        db = db_client[DATABASE_NAME]
        
        # Création des index pour performance
        await db.utilisateurs.create_index("email", unique=True)
        await db.utilisateurs.create_index("code_parrainage", unique=True, sparse=True)
        await db.produits.create_index([("titre", "text"), ("description", "text")])
        await db.produits.create_index("statut")
        await db.produits.create_index("categorie")
        await db.produits.create_index("date_creation", background=True)
        await db.conversations_chatbot.create_index("utilisateur_id")
        
    return db

def serialize_doc(doc):
    """Convertit ObjectId en string pour JSON"""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# ==================== AUTH HELPERS ====================
def create_jwt_token(user_id: str, email: str) -> str:
    """Crée un JWT token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt_token(token: str) -> dict:
    """Vérifie et décode le JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Récupère l'utilisateur actuel depuis le token"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    database = await get_db()
    
    user = await database.utilisateurs.find_one({"_id": ObjectId(payload["user_id"])})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return serialize_doc(user)

def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generer_code_parrainage(nom: str, email: str) -> str:
    """Génère un code de parrainage unique"""
    import hashlib
    base = f"{nom}{email}{datetime.utcnow().timestamp()}"
    return hashlib.sha256(base.encode()).hexdigest()[:8].upper()

# ==================== ROUTES AUTH ====================
@app.post("/api/auth/inscription", status_code=status.HTTP_201_CREATED)
async def inscription(user_data: UtilisateurCreate):
    """Inscription d'un nouveau utilisateur"""
    database = await get_db()
    
    # Vérifier si email existe
    existing = await database.utilisateurs.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    
    # Créer l'utilisateur
    user_dict = user_data.dict(exclude={"mot_de_passe", "code_parrainage"})
    user_dict["mot_de_passe_hash"] = hash_password(user_data.mot_de_passe)
    user_dict["code_parrainage"] = generer_code_parrainage(user_data.nom, user_data.email)
    user_dict["parrain_code"] = user_data.code_parrainage
    user_dict["date_creation"] = datetime.utcnow()
    user_dict["score_reputation"] = 0
    user_dict["produits_vendus"] = 0
    
    result = await database.utilisateurs.insert_one(user_dict)
    user_id = str(result.inserted_id)
    
    # Bonus parrainage si code fourni
    if user_data.code_parrainage:
        parrain = await database.utilisateurs.find_one({"code_parrainage": user_data.code_parrainage})
        if parrain:
            await database.utilisateurs.update_one(
                {"_id": parrain["_id"]},
                {"$inc": {"score_reputation": 10}}
            )
    
    token = create_jwt_token(user_id, user_data.email)
    
    return {
        "message": "Inscription réussie",
        "token": token,
        "utilisateur": {
            "id": user_id,
            "nom": user_data.nom,
            "email": user_data.email,
            "code_parrainage": user_dict["code_parrainage"]
        }
    }

@app.post("/api/auth/connexion")
async def connexion(login_data: UtilisateurLogin):
    """Connexion d'un utilisateur"""
    database = await get_db()
    
    user = await database.utilisateurs.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.mot_de_passe, user["mot_de_passe_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_jwt_token(str(user["_id"]), user["email"])
    
    return {
        "message": "Connexion réussie",
        "token": token,
        "utilisateur": serialize_doc({
            "_id": user["_id"],
            "nom": user["nom"],
            "email": user["email"],
            "telephone": user["telephone"],
            "code_parrainage": user.get("code_parrainage")
        })
    }

@app.get("/api/auth/profil")
async def get_profil(current_user: dict = Depends(get_current_user)):
    """Récupère le profil de l'utilisateur connecté"""
    database = await get_db()
    
    # Compter les produits de l'utilisateur
    nb_produits = await database.produits.count_documents({
        "vendeur_id": current_user["id"],
        "statut": {"$ne": StatutProduit.SUPPRIME}
    })
    
    current_user["nombre_produits"] = nb_produits
    return current_user

# ==================== ROUTES PRODUITS ====================
@app.post("/api/produits", status_code=status.HTTP_201_CREATED)
async def creer_produit(
    produit_data: ProduitCreate,
    current_user: dict = Depends(get_current_user)
):
    """Créer une nouvelle annonce"""
    database = await get_db()
    
    produit_dict = produit_data.dict(exclude={"images_base64"})
    produit_dict["vendeur_id"] = current_user["id"]
    produit_dict["vendeur_nom"] = current_user["nom"]
    produit_dict["vendeur_telephone"] = current_user["telephone"]
    produit_dict["statut"] = StatutProduit.DISPONIBLE
    produit_dict["date_creation"] = datetime.utcnow()
    produit_dict["vues"] = 0
    produit_dict["favoris"] = 0
    produit_dict["images"] = produit_data.images_base64[:8]  # Max 8 images
    
    result = await database.produits.insert_one(produit_dict)
    
    return {
        "message": "Produit créé avec succès",
        "produit_id": str(result.inserted_id)
    }

@app.get("/api/produits")
async def liste_produits(
    page: int = 1,
    limite: int = 20,
    categorie: Optional[CategorieType] = None,
    ville: Optional[str] = None,
    prix_min: Optional[int] = None,
    prix_max: Optional[int] = None,
    recherche: Optional[str] = None
):
    """Liste des produits avec filtres et pagination"""
    database = await get_db()
    
    # Construction du filtre
    filtre = {"statut": StatutProduit.DISPONIBLE}
    
    if categorie:
        filtre["categorie"] = categorie
    if ville:
        filtre["ville"] = ville
    if prix_min is not None:
        filtre["prix"] = {"$gte": prix_min}
    if prix_max is not None:
        filtre.setdefault("prix", {})["$lte"] = prix_max
    if recherche:
        filtre["$text"] = {"$search": recherche}
    
    # Pagination
    skip = (page - 1) * limite
    
    # Récupération des produits
    cursor = database.produits.find(filtre).sort("date_creation", -1).skip(skip).limit(limite)
    produits = await cursor.to_list(length=limite)
    
    # Total pour pagination
    total = await database.produits.count_documents(filtre)
    
    return {
        "produits": [serialize_doc(p) for p in produits],
        "total": total,
        "page": page,
        "pages_total": (total + limite - 1) // limite
    }

@app.get("/api/produits/{produit_id}")
async def detail_produit(produit_id: str):
    """Détail d'un produit"""
    database = await get_db()
    
    if not ObjectId.is_valid(produit_id):
        raise HTTPException(status_code=400, detail="ID produit invalide")
    
    produit = await database.produits.find_one({"_id": ObjectId(produit_id)})
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Incrémenter les vues
    await database.produits.update_one(
        {"_id": ObjectId(produit_id)},
        {"$inc": {"vues": 1}}
    )
    
    return serialize_doc(produit)

@app.delete("/api/produits/{produit_id}")
async def supprimer_produit(
    produit_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Supprimer un produit (soft delete)"""
    database = await get_db()
    
    if not ObjectId.is_valid(produit_id):
        raise HTTPException(status_code=400, detail="ID produit invalide")
    
    produit = await database.produits.find_one({"_id": ObjectId(produit_id)})
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    if produit["vendeur_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    await database.produits.update_one(
        {"_id": ObjectId(produit_id)},
        {"$set": {"statut": StatutProduit.SUPPRIME}}
    )
    
    return {"message": "Produit supprimé avec succès"}

# ==================== CHATBOT IA ====================
@app.post("/api/chatbot")
async def chatbot_conversation(
    message_data: MessageChatbot,
    current_user: dict = Depends(get_current_user)
):
    """Conversation avec le chatbot IA"""
    database = await get_db()
    
    # Récupérer ou créer une conversation
    if message_data.conversation_id:
        conversation = await database.conversations_chatbot.find_one({
            "_id": ObjectId(message_data.conversation_id)
        })
    else:
        conversation = None
    
    if not conversation:
        conversation = {
            "utilisateur_id": current_user["id"],
            "messages": [],
            "date_creation": datetime.utcnow()
        }
        result = await database.conversations_chatbot.insert_one(conversation)
        conversation["_id"] = result.inserted_id
    
    # Ajouter le message utilisateur
    conversation["messages"].append({
        "role": "user",
        "content": message_data.message,
        "timestamp": datetime.utcnow()
    })
    
    # Préparer le contexte pour Claude
    messages_claude = []
    for msg in conversation["messages"][-10:]:  # Garder les 10 derniers messages
        messages_claude.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Appel à l'API Anthropic
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system="""Tu es l'assistant virtuel de SANI-FÉRÉ, la marketplace malienne numéro 1.
            
            Tu aides les utilisateurs à:
            - Acheter et vendre des produits
            - Naviguer sur la plateforme
            - Comprendre les modes de paiement (Orange Money, Wave, Moov Money)
            - Résoudre leurs problèmes
            
            Réponds toujours en français, sois courtois et professionnel.
            Tu connais bien le Mali, Bamako et les habitudes locales.""",
            messages=messages_claude
        )
        
        reponse_ia = response.content[0].text
        
    except Exception as e:
        reponse_ia = "Désolé, je rencontre un problème technique. Veuillez réessayer."
    
    # Ajouter la réponse du bot
    conversation["messages"].append({
        "role": "assistant",
        "content": reponse_ia,
        "timestamp": datetime.utcnow()
    })
    
    # Sauvegarder la conversation
    await database.conversations_chatbot.update_one(
        {"_id": conversation["_id"]},
        {
            "$set": {
                "messages": conversation["messages"],
                "date_modification": datetime.utcnow()
            }
        }
    )
    
    return {
        "reponse": reponse_ia,
        "conversation_id": str(conversation["_id"])
    }

# ==================== ROUTES UTILITAIRES ====================
@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "nom": "SANI-FÉRÉ PRO API",
        "version": "2.0.0",
        "description": "Marketplace malien avec IA",
        "status": "online"
    }

@app.get("/api/stats")
async def statistiques_globales():
    """Statistiques de la plateforme"""
    database = await get_db()
    
    nb_utilisateurs = await database.utilisateurs.count_documents({})
    nb_produits = await database.produits.count_documents({"statut": StatutProduit.DISPONIBLE})
    nb_vendus = await database.produits.count_documents({"statut": StatutProduit.VENDU})
    
    return {
        "utilisateurs": nb_utilisateurs,
        "produits_actifs": nb_produits,
        "produits_vendus": nb_vendus
    }

# ==================== STARTUP / SHUTDOWN ====================
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    await get_db()
    print("✅ SANI-FÉRÉ PRO API démarrée")
    print(f"📊 Base de données: {DATABASE_NAME}")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    global db_client
    if db_client:
        db_client.close()
    print("👋 SANI-FÉRÉ PRO API arrêtée")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
