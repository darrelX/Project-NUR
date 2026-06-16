# Tests TypeScript pour l'API Backend

Suite de tests complète en TypeScript pour toutes les routes de l'API Flask backend.

## 📦 Installation

```bash
cd test-api
npm install
```

## 🚀 Utilisation

### 1. Démarrer le serveur Flask
```bash
# Dans le répertoire backend/
python app.py
```

### 2. Exécuter les tests

#### Tous les tests
```bash
npm test
# ou en mode dev avec ts-node
npm run dev
```

#### Tests individuels
```bash
npm run test:health      # Test health check
npm run test:upload      # Test upload de fichier
npm run test:celldown    # Test process celldown
npm run test:xlookup     # Test process xlookup
npm run test:ticket      # Test process ticket
```

## 📁 Structure des fichiers

```
test-api/
├── src/
│   ├── api-client.ts           # Client API avec toutes les méthodes
│   ├── config.ts                # Configuration (URL, timeout, etc.)
│   ├── types.ts                 # Types TypeScript
│   ├── utils.ts                 # Fonctions utilitaires
│   └── test-all-routes.ts       # Script de test principal
├── dist/                        # Fichiers compilés
├── package.json
├── tsconfig.json
└── README.md
```

## 🧪 Routes testées

1. ✅ `GET /api/health` - Health check du serveur
2. ✅ `POST /api/upload-main-file` - Upload du fichier principal
3. ✅ `GET /api/get-data` - Récupération des données
4. ✅ `POST /api/process-celldown` - Traitement CellDown
5. ✅ `POST /api/process-xlookup` - Traitement SuperXlookup
6. ✅ `POST /api/process-ticket` - Traitement Ticket
7. ✅ `GET /api/export` - Export du fichier
8. ✅ `DELETE /api/clear-main-file` - Suppression du fichier principal

## 📋 Prérequis

Les fichiers de test suivants doivent exister dans `backend/test_files/` :
- `main_test.xlsx` - Fichier principal de test
- `target_ticket.xlsx` - Fichier cible pour CellDown et Ticket
- `target_xlookup.xlsx` - Fichier cible pour XLookup

## 🎯 Exemple de sortie

```
============================================================
TESTS DES ROUTES API BACKEND
============================================================

VÉRIFICATION DES PRÉREQUIS
✅ Fichier principal: backend/test_files/main_test.xlsx
✅ Fichier target (celldown): backend/test_files/target_ticket.xlsx
✅ Fichier target (xlookup): backend/test_files/target_xlookup.xlsx
✅ Fichier target (ticket): backend/test_files/target_ticket.xlsx

📋 Test 1/8: Health check...
✅ GET /api/health
   Status: 200
   Duration: 45ms
   Message: Backend is running

📋 Test 2/8: Upload main file...
✅ POST /api/upload-main-file
   Status: 200
   Duration: 312ms
   Message: Fichier uploadé: main_test.xlsx (5 lignes)

[...]

============================================================
RÉSUMÉ DES TESTS
============================================================

Total: 8 tests
✅ Réussis: 8
❌ Échoués: 0
⏱️  Durée totale: 2456ms

🎉 TOUS LES TESTS SONT PASSÉS !
============================================================
```

## 🛠️ Configuration

Modifiez `src/config.ts` pour ajuster :
- `baseUrl` - URL du serveur backend (défaut: `http://localhost:5000`)
- `timeout` - Timeout des requêtes (défaut: `60000ms`)
- `testFilesDir` - Répertoire des fichiers de test

## 📝 Notes

- Les tests s'exécutent séquentiellement avec des pauses entre certaines opérations
- Le serveur Flask doit être en mode debug pour un rechargement automatique
- Les fichiers uploadés sont sauvegardés dans `backend/uploads/`
- Le dernier test (clear-main-file) nettoie l'état du serveur

## 🐛 Dépannage

**Erreur "Serveur non accessible"**
- Vérifiez que le serveur Flask est démarré sur le port 5000
- Testez manuellement : `curl http://localhost:5000/api/health`

**Erreur "Fichiers de test manquants"**
- Créez les fichiers requis dans `backend/test_files/`
- Assurez-vous qu'ils sont au format Excel (.xlsx)

**Erreur de compilation TypeScript**
- Exécutez `npm run build` pour voir les erreurs détaillées
- Vérifiez que toutes les dépendances sont installées
