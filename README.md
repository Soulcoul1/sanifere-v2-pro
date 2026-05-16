# 🏺 SANI-FÉRÉ PRO - Marketplace Malien Premium

**Marketplace de luxe célébrant l'artisanat et le patrimoine malien**

Design inspiré par l'élégance et la sophistication, SANI-FÉRÉ connecte artisans maliens et acheteurs du monde entier.

---

## ✨ Caractéristiques

### Frontend
- **Design Premium** : Palette terracotta/beige/crème, typographie élégante (Playfair Display + Montserrat)
- **Mobile-First** : Interface responsive optimisée pour tous les écrans
- **UX Raffinée** : Animations fluides, transitions soignées
- **Categories** : Mode Vintage, Art, Décoration, Textiles, Bijouterie, Maroquinerie

### Backend (FastAPI)
- **Architecture Moderne** : FastAPI + Motor (MongoDB async)
- **Authentification JWT** : Sécurisée avec bcrypt
- **API RESTful** : Endpoints complets et documentés
- **Chatbot IA** : Intégration Claude (Anthropic) pour assistance client
- **Performance** : Index MongoDB optimisés, pagination efficace

### Fonctionnalités
- ✅ Inscription/Connexion utilisateur
- ✅ Gestion de produits (CRUD complet)
- ✅ Recherche et filtres avancés
- ✅ Système de parrainage avec codes
- ✅ Chatbot IA conversationnel
- ✅ Statistiques en temps réel
- ✅ Gestion favoris
- ✅ Multi-modes de paiement (Orange Money, Wave, Moov, Cash)

---

## 🚀 Déploiement

### Backend sur Railway

1. **Créer un compte Railway** : https://railway.app

2. **Créer un nouveau projet** :
   ```
   New Project → Deploy from GitHub
   ```

3. **Variables d'environnement** (Settings → Variables) :
   ```
   SECRET_KEY=votre-cle-secrete-production
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
   ANTHROPIC_API_KEY=sk-ant-votre-cle
   DATABASE_NAME=sanifere_v2
   PORT=8000
   ```

4. **Déploiement automatique** :
   - Push sur GitHub → Déploiement automatique
   - URL générée : `https://votre-app.up.railway.app`

### MongoDB Atlas

1. **Créer cluster gratuit** : https://www.mongodb.com/cloud/atlas
2. **Network Access** : Autoriser `0.0.0.0/0` (toutes IPs)
3. **Database User** : Créer utilisateur avec droits lecture/écriture
4. **Connection String** : Copier l'URI dans MONGODB_URI

### Frontend sur Vercel

1. **Créer compte Vercel** : https://vercel.com
2. **Import GitHub repository**
3. **Settings** :
   - Root Directory: `.` (racine)
   - Build Command: (laisser vide)
   - Output Directory: `.`
4. **Deploy** !

---

## 💻 Développement Local

### Prérequis
- Python 3.11+
- MongoDB (local ou Atlas)
- Compte Anthropic (pour chatbot IA)

### Installation

```bash
# Cloner le repository
git clone https://github.com/votre-username/sanifere-v2.git
cd sanifere-v2

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Copier fichier environnement
cp .env.example .env
# Éditer .env avec vos vraies valeurs

# Lancer le serveur
uvicorn main:app --reload --port 8000
```

### Tester l'API
```bash
# Documentation interactive
http://localhost:8000/docs

# Health check
curl http://localhost:8000/

# Stats
curl http://localhost:8000/api/stats
```

---

## 📁 Structure du Projet

```
sanifere-v2/
├── main.py                 # Backend FastAPI
├── index.html              # Frontend
├── requirements.txt        # Dépendances Python
├── runtime.txt            # Version Python
├── railway.json           # Config Railway
├── .env.example           # Variables d'env exemple
└── README.md              # Ce fichier
```

---

## 🔗 API Endpoints

### Authentification
- `POST /api/auth/inscription` - Créer un compte
- `POST /api/auth/connexion` - Se connecter
- `GET /api/auth/profil` - Profil utilisateur (auth requise)

### Produits
- `GET /api/produits` - Liste des produits (avec filtres)
- `GET /api/produits/{id}` - Détail d'un produit
- `POST /api/produits` - Créer un produit (auth requise)
- `DELETE /api/produits/{id}` - Supprimer un produit (auth requise)

### Chatbot
- `POST /api/chatbot` - Conversation avec l'IA (auth requise)

### Utilitaires
- `GET /` - Info API
- `GET /api/stats` - Statistiques globales

---

## 🎨 Design System

### Couleurs
```css
--terracotta: #B85C50    /* Boutons, accents */
--dark-brown: #3D2817    /* Texte, footer */
--cream: #F5F1E8         /* Fond principal */
--beige: #E8DCC4         /* Fond secondaire */
--gold: #C4A052          /* Accents premium */
```

### Typographies
- **Titres** : Playfair Display (serif, élégant)
- **Corps** : Montserrat (sans-serif, moderne)

---

## 🔐 Sécurité

- ✅ JWT avec expiration 7 jours
- ✅ Mots de passe hashés (bcrypt)
- ✅ CORS configuré
- ✅ Validation Pydantic
- ✅ Rate limiting (à implémenter en production)

---

## 📱 Modes de Paiement (Mali)

1. **Orange Money** - Principal
2. **Wave** - Alternative populaire
3. **Moov Money** - Troisième opérateur
4. **Espèces** - Paiement en personne
5. **Virement bancaire** - Pour grosses transactions

---

## 🚧 Roadmap

### Phase 1 - MVP (Actuel) ✅
- Frontend design premium
- Backend API complet
- Auth & gestion produits
- Chatbot IA

### Phase 2 - Paiements
- [ ] Intégration Orange Money API
- [ ] Intégration Wave API
- [ ] Système de commandes
- [ ] Notifications SMS

### Phase 3 - Social
- [ ] Système de reviews
- [ ] Messagerie vendeur-acheteur
- [ ] Partage social
- [ ] Programme fidélité

### Phase 4 - Analytics
- [ ] Dashboard vendeur
- [ ] Statistiques ventes
- [ ] Recommandations IA
- [ ] SEO optimization

---

## 🤝 Contribution

Les contributions sont bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📞 Contact

**SANI-FÉRÉ Team**
- Email: contact@sanifere.ml
- Téléphone: +223 70 00 00 00
- Localisation: Bamako, Mali

---

## 📄 Licence

Projet propriétaire - Tous droits réservés © 2026 SANI-FÉRÉ

---

## 🙏 Remerciements

- Artisans maliens pour leur savoir-faire
- Communauté open-source
- Anthropic (Claude AI)
- FastAPI, MongoDB, Railway, Vercel

---

**Fait avec ❤️ à Bamako, Mali**
