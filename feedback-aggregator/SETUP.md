# 🚀 Guide de démarrage - Feedback Aggregator

## Architecture

L'application est composée de deux parties :
- **Backend** : API Flask (Python) qui traite les fichiers Excel
- **Frontend** : Application React + TypeScript + Vite

## Prérequis

- Python 3.8+
- Node.js 16+
- npm ou yarn

## Installation

### 1. Backend (Flask)

```powershell
# Naviguer vers le dossier backend
cd backend

# Créer un environnement virtuel (optionnel mais recommandé)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Frontend (React)

```powershell
# Revenir au dossier racine
cd ..

# Installer les dépendances npm
npm install
```

## Démarrage

### 1. Démarrer le backend (Terminal 1)

```powershell
cd backend
python app.py
```

Le backend démarre sur : **http://localhost:5000**

Vous devriez voir :
```
🚀 Starting Flask backend on http://localhost:5000
```

### 2. Démarrer le frontend (Terminal 2)

```powershell
# Depuis la racine du projet feedback-aggregator
npm run dev
```

Le frontend démarre sur : **http://localhost:5173** (ou un autre port si occupé)

## Vérification

1. Ouvrez votre navigateur sur http://localhost:5173
2. L'application devrait se charger sans erreur
3. Vous devriez voir l'interface avec le bouton "Importer le fichier principal"

## Endpoints API disponibles

- `GET /api/health` - Vérifier l'état du backend
- `POST /api/upload-main-file` - Upload du fichier principal
- `POST /api/process-celldown` - Traiter avec CellDown
- `POST /api/process-xlookup` - Traiter avec SuperXlookup
- `POST /api/process-ticket` - Traiter avec Ticket
- `GET /api/get-data` - Récupérer les données actuelles
- `GET /api/export` - Télécharger le fichier consolidé

## Workflow de l'application

1. **Upload du fichier principal** : Le fichier est envoyé au backend et stocké
2. **Visualisation** : L'aperçu des données est affiché (5 premières lignes)
3. **Ajout de traitements** : 
   - Cliquer sur "Importer un fichier"
   - Choisir une catégorie (CellDown, Transmission, Sites)
   - Configurer les paramètres
   - Upload le fichier cible
4. **Traitement** : Le backend traite le fichier et met à jour le fichier principal
5. **Export** : Télécharger le fichier consolidé final

## Structure des fichiers

```
feedback-aggregator/
├── backend/
│   ├── app.py              # API Flask
│   ├── requirements.txt    # Dépendances Python
│   └── uploads/            # Fichiers uploadés
├── src/
│   ├── services/
│   │   ├── apiService.ts   # Communication avec l'API
│   │   └── excelService.ts # Logique Excel (utilise apiService)
│   ├── components/         # Composants React
│   └── App.tsx            # Application principale
└── SETUP.md               # Ce fichier
```

## Dépannage

### Le backend ne démarre pas
- Vérifier que Python est installé : `python --version`
- Vérifier que toutes les dépendances sont installées
- Vérifier que le port 5000 n'est pas déjà utilisé

### Le frontend ne se connecte pas au backend
- Vérifier que le backend est bien démarré sur http://localhost:5000
- Vérifier la console du navigateur pour les erreurs CORS
- L'URL de l'API est configurée dans `src/services/apiService.ts`

### Erreurs CORS
Le backend a déjà CORS activé avec `flask-cors`. Si des erreurs persistent :
```python
# Dans backend/app.py
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

## Technologies utilisées

### Backend
- Flask (API REST)
- pandas (Traitement Excel)
- openpyxl (Lecture/écriture Excel)

### Frontend
- React 18
- TypeScript
- Vite (Build tool)
- TailwindCSS (Styling)
- XLSX (Lecture Excel côté client - utilisé en fallback)

## Notes importantes

- Le fichier principal est stocké côté backend après l'upload
- Chaque traitement crée une nouvelle version du fichier
- Les fichiers sont sauvegardés dans `backend/uploads/`
- Le backend garde en mémoire le chemin du dernier fichier traité
