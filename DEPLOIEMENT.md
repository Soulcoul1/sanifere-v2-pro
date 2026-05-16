# 🚀 GUIDE DE DÉPLOIEMENT SANI-FÉRÉ PRO

## Vue d'ensemble
- **Backend** : Railway (FastAPI + MongoDB)
- **Frontend** : Vercel (HTML/CSS/JS)
- **Database** : MongoDB Atlas (gratuit)
- **IA** : Anthropic Claude

---

## ÉTAPE 1 : MongoDB Atlas (Base de données)

### 1.1 Créer un compte
1. Aller sur https://www.mongodb.com/cloud/atlas/register
2. S'inscrire avec Google ou email
3. Choisir le plan **M0 (gratuit)**

### 1.2 Créer un cluster
1. **Create** → **Shared** (gratuit)
2. **Provider** : AWS
3. **Region** : eu-west-3 (Paris) - plus proche du Mali
4. **Cluster Name** : sanifere-cluster
5. Cliquer **Create Cluster** (prend 3-5 min)

### 1.3 Configurer l'accès
1. **Security** → **Network Access** → **Add IP Address**
2. Choisir **Allow Access from Anywhere** (0.0.0.0/0)
3. Confirmer

### 1.4 Créer un utilisateur
1. **Security** → **Database Access** → **Add New Database User**
2. **Username** : `sanifere_admin`
3. **Password** : Générer un mot de passe fort (noter quelque part!)
4. **Database User Privileges** : **Read and write to any database**
5. **Add User**

### 1.5 Obtenir la connection string
1. **Databases** → **Connect** → **Connect your application**
2. **Driver** : Python / 3.12 or later
3. Copier la connection string :
   ```
   mongodb+srv://sanifere_admin:<password>@sanifere-cluster.xxxxx.mongodb.net/
   ```
4. Remplacer `<password>` par votre mot de passe
5. **CONSERVER CETTE STRING EN SÉCURITÉ** ✅

---

## ÉTAPE 2 : Anthropic API (Chatbot IA)

### 2.1 Créer un compte
1. Aller sur https://console.anthropic.com/
2. S'inscrire avec email

### 2.2 Obtenir une API Key
1. **API Keys** → **Create Key**
2. Nom : `sanifere-production`
3. Copier la clé (commence par `sk-ant-...`)
4. **CONSERVER CETTE CLÉ EN SÉCURITÉ** ✅

### 2.3 Ajouter des crédits (optionnel)
- $5 offerts à l'inscription
- Ajouter $10-20 pour démarrer
- Settings → Billing

---

## ÉTAPE 3 : Railway (Backend API)

### 3.1 Créer un compte
1. Aller sur https://railway.app/
2. S'inscrire avec GitHub

### 3.2 Créer un nouveau projet
1. **New Project** → **Deploy from GitHub repo**
2. Sélectionner votre repo `sanifere-v2`
3. Railway détecte automatiquement Python

### 3.3 Configurer les variables d'environnement
1. Cliquer sur le service déployé
2. **Variables** → **+ New Variable**

Ajouter ces variables :

```bash
SECRET_KEY=votreclesecrete123456789CHANGEZ_MOI_PRODUCTION
MONGODB_URI=mongodb+srv://sanifere_admin:VOTRE_MOT_DE_PASSE@sanifere-cluster.xxxxx.mongodb.net/
ANTHROPIC_API_KEY=sk-ant-VOTRE_CLE_ANTHROPIC
DATABASE_NAME=sanifere_v2
PORT=8000
```

**Important** :
- `SECRET_KEY` : Générez une clé aléatoire de 50+ caractères
- `MONGODB_URI` : La connection string de l'étape 1.5
- `ANTHROPIC_API_KEY` : La clé de l'étape 2.2

### 3.4 Déployer
1. Railway déploie automatiquement
2. Attendre 2-3 minutes
3. Une fois déployé, copier l'URL (ex: `https://sanifere-production.up.railway.app`)

### 3.5 Tester l'API
Ouvrir dans le navigateur :
```
https://votre-url.up.railway.app/docs
```

Vous devriez voir la documentation Swagger de l'API ✅

---

## ÉTAPE 4 : Vercel (Frontend)

### 4.1 Créer un compte
1. Aller sur https://vercel.com/
2. S'inscrire avec GitHub

### 4.2 Importer le projet
1. **New Project** → **Import Git Repository**
2. Sélectionner votre repo `sanifere-v2`

### 4.3 Configurer le déploiement
1. **Framework Preset** : Other
2. **Root Directory** : `./` (racine)
3. **Build Command** : (laisser vide)
4. **Output Directory** : `./` (racine)
5. **Install Command** : (laisser vide)

### 4.4 Variables d'environnement (optionnel)
Si vous voulez stocker l'URL API côté build :
```
VITE_API_URL=https://votre-url.up.railway.app
```

### 4.5 Déployer
1. Cliquer **Deploy**
2. Attendre 1-2 minutes
3. Votre site est en ligne ! 🎉

---

## ÉTAPE 5 : Connecter Frontend ↔ Backend

### 5.1 Mettre à jour l'URL API dans app.js
1. Ouvrir `app.js`
2. Ligne 2, remplacer :
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://VOTRE-URL-RAILWAY.up.railway.app'; // ⬅️ Mettre votre URL Railway
```

### 5.2 Push vers GitHub
```bash
git add app.js
git commit -m "🔗 Connect frontend to Railway backend"
git push
```

Vercel redéploie automatiquement en 30 secondes ✅

---

## ÉTAPE 6 : Tester l'Application Complète

### 6.1 Créer un compte
1. Ouvrir votre site Vercel
2. Cliquer sur le menu hamburger (☰)
3. "Inscription"
4. Remplir le formulaire
5. **Noter votre code de parrainage** (affiché après inscription)

### 6.2 Publier un produit (API)
Via Swagger UI (`https://votre-railway.up.railway.app/docs`) :

1. **POST /api/auth/connexion** → Copier le token
2. **Authorize** (🔒 en haut) → Coller le token
3. **POST /api/produits** → Créer un produit test

### 6.3 Tester le chatbot
1. Cliquer sur le bouton 💬 en bas à droite
2. Poser une question : "Comment acheter sur SANI-FÉRÉ ?"
3. L'IA doit répondre

---

## 🎯 CHECKLIST FINALE

- [ ] MongoDB Atlas configuré et accessible
- [ ] Anthropic API key valide
- [ ] Backend déployé sur Railway
- [ ] Variables d'environnement Railway correctes
- [ ] Frontend déployé sur Vercel
- [ ] URL API mise à jour dans app.js
- [ ] Test inscription/connexion OK
- [ ] Test création produit OK
- [ ] Test chatbot IA OK
- [ ] Test affichage produits OK

---

## 🔧 DÉPANNAGE

### Backend ne démarre pas
```bash
# Vérifier les logs Railway
# Settings → Deployments → Cliquer sur le dernier déploiement → View Logs
```

Erreurs fréquentes :
- ❌ `ModuleNotFoundError` → Vérifier `requirements.txt`
- ❌ `Connection refused` → Vérifier `MONGODB_URI`
- ❌ `Invalid API key` → Vérifier `ANTHROPIC_API_KEY`

### Frontend ne charge pas les produits
1. Ouvrir Console (F12) dans le navigateur
2. Vérifier erreurs CORS
3. Solution : Ajouter votre domaine Vercel dans CORS backend :

Dans `main.py`, ligne ~25 :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votre-site.vercel.app"],  # Ajouter votre URL
    # ...
)
```

### Chatbot ne répond pas
- Vérifier crédit Anthropic : https://console.anthropic.com/settings/billing
- Vérifier API key dans Railway

---

## 📊 MONITORING

### Railway
- **Metrics** : CPU, RAM, Network
- **Logs** : Erreurs temps réel

### MongoDB Atlas
- **Metrics** : Connections, Operations, Storage
- **Charts** : Visualisation des données

### Vercel
- **Analytics** : Visiteurs, Performance
- **Logs** : Erreurs frontend

---

## 🚀 PROCHAINES ÉTAPES

1. **Personnaliser le design** :
   - Ajouter votre logo
   - Modifier les couleurs dans les CSS variables
   - Ajouter de vraies images produits

2. **Configurer un nom de domaine** :
   - Railway : Settings → Domains
   - Vercel : Settings → Domains

3. **Activer les paiements** :
   - Orange Money API
   - Wave API

4. **SEO** :
   - Ajouter meta tags
   - Créer sitemap.xml
   - Google Search Console

---

## 📞 SUPPORT

- **Railway** : https://railway.app/help
- **Vercel** : https://vercel.com/help
- **MongoDB** : https://www.mongodb.com/docs/atlas/
- **Anthropic** : https://docs.anthropic.com/

---

**Bon déploiement ! 🎉**

*Fait avec ❤️ pour SANI-FÉRÉ*
