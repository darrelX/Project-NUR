# 🔗 Connexion Frontend ↔️ Backend Python

## Architecture de communication

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + TypeScript)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  App.tsx                                                         │
│  └─> handleMainFileSelect()                                     │
│  └─> handleConfigSubmit()                                       │
│       │                                                          │
│       v                                                          │
│  excelService.ts                                                 │
│  ├─> getExcelDataForPreview(file)                              │
│  ├─> processCellDown(null, file, config)                       │
│  ├─> processXlookup(null, file, config)                        │
│  ├─> processTicket(null, file, config)                         │
│  └─> getDataFromBackend()                                       │
│       │                                                          │
│       v                                                          │
│  apiService.ts                                                   │
│  ├─> uploadMainFile(file) ──────────────────┐                  │
│  ├─> processCelldown(file, config) ─────────┤                  │
│  ├─> processXlookup(file, config) ──────────┤                  │
│  ├─> processTicket(file, config) ───────────┤                  │
│  ├─> getData() ──────────────────────────────┤                  │
│  └─> downloadProcessedFile() ────────────────┤                  │
│                                               │                  │
└───────────────────────────────────────────────┼──────────────────┘
                                                │
                                    HTTP Requests (fetch)
                                    http://localhost:5000/api
                                                │
┌───────────────────────────────────────────────┼──────────────────┐
│                       BACKEND (Flask + Python)│                  │
├─────────────────────────────────────────────────────────────────┤
│  app.py                                       │                  │
│                                               v                  │
│  Endpoints:                                                      │
│  ├─> POST /api/upload-main-file              ✅ Upload         │
│  ├─> POST /api/process-celldown              ✅ CellDown        │
│  ├─> POST /api/process-xlookup               ✅ SuperXlookup    │
│  ├─> POST /api/process-ticket                ✅ Ticket          │
│  ├─> GET  /api/get-data                      ✅ Récupération    │
│  ├─> GET  /api/export                        ✅ Export          │
│  └─> GET  /api/health                        ✅ Santé           │
│                                                                  │
│  Classes Python (depuis /automate):                             │
│  ├─> CellDown                                                   │
│  ├─> SuperXlookup                                               │
│  └─> Ticket                                                     │
│                                                                  │
│  Storage:                                                        │
│  └─> backend/uploads/*.xlsx                                     │
│       └─> .main_file_path.txt (persistence)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Flux de traitement CellDown

### 1️⃣ Upload du fichier principal
```typescript
// Frontend: App.tsx
handleMainFileSelect(file) 
  └─> excelService.getExcelDataForPreview(file)
      ├─> apiService.checkHealth() ✅
      ├─> apiService.uploadMainFile(file)
      │   └─> POST /api/upload-main-file
      │       └─> Backend sauvegarde dans uploads/
      │           └─> Met à jour MAIN_FILE_PATH
      └─> apiService.getData()
          └─> GET /api/get-data
              └─> Retourne les données du fichier principal
```

**Logs Frontend** :
```
🟢 [App] Fichier principal chargé: fichier.xlsx
🔵 [Preview] Chargement aperçu du fichier
🔵 [Preview] Upload du fichier vers le backend...
🔵 [apiService] uploadMainFile appelé avec: fichier.xlsx 1048576
✅ [Preview] Fichier uploadé: { success: true, lines: 100, ... }
🔵 [Preview] Récupération des données...
✅ [Preview] Données récupérées: 100 lignes
```

**Logs Backend** :
```
🟣 [BACKEND] /api/upload-main-file appelé
🟣 [BACKEND] Fichier reçu: fichier.xlsx
✅ [BACKEND] Fichier sauvegardé avec succès
✅ [BACKEND] MAIN_FILE_PATH mis à jour et sauvegardé
```

### 2️⃣ Traitement avec CellDown
```typescript
// Frontend: App.tsx
handleConfigSubmit(config, file)
  └─> excelService.processCellDown(null, file, config)
      ├─> apiService.processCelldown(file, config)
      │   └─> POST /api/process-celldown
      │       ├─> Backend lit MAIN_FILE_PATH
      │       ├─> Sauvegarde le fichier target
      │       ├─> Crée une copie du main file
      │       ├─> Exécute CellDown.super_xlookup_par_date()
      │       └─> Met à jour MAIN_FILE_PATH avec le nouveau fichier
      └─> apiService.downloadProcessedFile()
          └─> GET /api/export
              └─> Retourne le fichier .xlsx traité
```

**Logs Frontend** :
```
🔵 [CellDown] Début du traitement
📋 Configuration: { reference_name: "CellDown", ... }
🔵 [CellDown] Envoi au backend Python...
🔵 [apiService] processCelldown appelé
📄 Fichier: target.xlsx (512.5 KB)
⚙️ Config: { reference_name: "CellDown", colown_key_path_source: "Codesite", ... }
   reference_name: CellDown
   colown_key_path_source: Codesite
   target_key_column: Site Code
   target_value_column: Alarm Name
   date_str: 2024-01
🔵 [apiService] Envoi vers: http://localhost:5000/api/process-celldown
🔵 [apiService] Status: 200
✅ [apiService] CellDown terminé: 100 lignes, 15 colonnes
✅ [CellDown] Traitement terminé par le backend
📊 Résultat: 100 lignes, 15 colonnes
🔵 [CellDown] Téléchargement du fichier traité...
✅ [CellDown] Fichier téléchargé: 523.7 KB
```

**Logs Backend** :
```
================================================================================
🔄 DEBUT TRAITEMENT CELLDOWN
================================================================================
📁 Main file: uploads/main_20240101_120000_fichier.xlsx
📄 Target file: target.xlsx
📋 Copie de uploads/main_20240101_120000_fichier.xlsx
   vers uploads/processed_celldown_20240101_120005_123456.xlsx
📊 Fichier source : 100 lignes, 14 colonnes
   Dernières colonnes: ['Col1', 'Col2', 'Col3', 'Col4', 'Col5']
✅ MAIN_FILE_PATH mis à jour: uploads/processed_celldown_20240101_120005_123456.xlsx
📊 Résultat: 100 lignes, 15 colonnes
================================================================================
```

### 3️⃣ Récupération de l'aperçu mis à jour
```typescript
// Frontend: App.tsx (après traitement)
excelService.getDataFromBackend()
  └─> apiService.getData()
      └─> GET /api/get-data
          └─> Backend lit le MAIN_FILE_PATH actuel
              └─> Retourne les données avec la nouvelle colonne
```

**Logs Frontend** :
```
🔵 [Preview] Récupération des données depuis le backend
✅ [Preview] Données récupérées: 100 lignes, 15 colonnes
```

### 4️⃣ Export final
```typescript
// Frontend: App.tsx
handleExport()
  └─> excelService.exportFile()
      └─> apiService.exportFile()
          └─> GET /api/export
              └─> Télécharge le fichier consolidé final
```

**Logs Frontend** :
```
🔵 [Export] Téléchargement depuis le backend...
🔵 [Export] Téléchargement du fichier consolidé...
✅ [Export] Fichier téléchargé avec succès
```

## Endpoints Backend détaillés

### POST `/api/upload-main-file`
**Requête** :
- `FormData` avec `file: File`

**Réponse** :
```json
{
  "success": true,
  "filename": "fichier.xlsx",
  "path": "uploads/main_20240101_120000_fichier.xlsx",
  "lines": 100,
  "size": 1048576
}
```

### POST `/api/process-celldown`
**Requête** :
- `FormData` avec :
  - `file: File` (fichier target)
  - `reference_name: string`
  - `colown_key_path_source: string`
  - `target_key_column: string`
  - `target_value_column: string`
  - `date_str: string`
  - `start_column: string` (optionnel)
  - `reference_date: string` (optionnel)
  - `source_sheet_path: string` (optionnel)

**Réponse** :
```json
{
  "success": true,
  "message": "CellDown processed successfully",
  "filename": "target.xlsx",
  "lines": 100,
  "columns": ["Col1", "Col2", ..., "CellDown 2024-01"],
  "data": [{ "Col1": "value1", ... }, ...]
}
```

### POST `/api/process-xlookup`
**Requête** :
- `FormData` avec :
  - `file: File`
  - `reference_name: string`
  - `source_key_column: string`
  - `target_key_column: string`
  - `target_value_column: string`
  - `result_column_name: string` (optionnel)
  - `reference_date: string` (optionnel)
  - `source_sheet_name: string` (optionnel)
  - `target_sheet_name: string` (optionnel)

**Réponse** : Similaire à `process-celldown`

### POST `/api/process-ticket`
**Requête** :
- `FormData` avec :
  - `file: File`
  - `reference_name: string`
  - `source_key_column: string`
  - `target_join_columns: string` (séparé par virgules)
  - `join_separator: string` (optionnel, défaut "..")
  - `ignore_empty: boolean` (optionnel, défaut true)
  - Autres paramètres...

**Réponse** : Similaire à `process-celldown`

### GET `/api/get-data`
**Réponse** :
```json
{
  "success": true,
  "lines": 100,
  "columns": ["Col1", "Col2", ...],
  "data": [{ "Col1": "value1", ... }, ...]
}
```

### GET `/api/export`
**Réponse** :
- Blob (fichier Excel)
- Headers: `Content-Disposition: attachment; filename="consolidated_YYYYMMDD_HHMMSS.xlsx"`

### GET `/api/health`
**Réponse** :
```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

## Gestion des erreurs

### Frontend
Toutes les fonctions ont maintenant des try/catch avec logs détaillés :
- 🔵 : En cours
- ✅ : Succès
- 🔴 : Erreur

### Backend
Les erreurs sont retournées au format JSON :
```json
{
  "error": "Message d'erreur détaillé",
  "trace": "Stack trace (en mode debug)"
}
```

## Variables d'état importantes

### Backend (`app.py`)
```python
MAIN_FILE_PATH = None  # Chemin du fichier principal actuel
UPLOAD_FOLDER = Path("uploads/")
PERSISTENCE_FILE = UPLOAD_FOLDER / ".main_file_path.txt"
```

### Frontend (`App.tsx`)
```typescript
mainFile: File | null  // Représentation locale (pas utilisée pour les traitements)
files: ProcessedFile[]  // Liste des fichiers importés
tableData: DataRow[]  // Données affichées dans le tableau
```

## Test rapide de connexion

```bash
# Terminal 1
cd backend
python app.py

# Terminal 2
npm run dev

# Terminal 3 - Test manuel
curl http://localhost:5000/api/health
# → {"status":"ok","message":"Backend is running"}
```

Ou utilisez `test-backend.html` pour une interface graphique de test !

## Dépannage

### ❌ "Backend non accessible"
- ✅ Vérifier que `python app.py` est lancé
- ✅ Vérifier http://localhost:5000/api/health
- ✅ Vérifier le pare-feu

### ❌ "Main file not uploaded"
- ✅ Uploader d'abord le fichier principal
- ✅ Vérifier que l'upload a réussi (logs)

### ❌ "Column not found"
- ✅ Vérifier les noms de colonnes dans la config
- ✅ Le backend supporte les listes : `"Site ID,SITE_ID,site id"`

### ❌ "Processing failed"
- ✅ Regarder les logs du backend (terminal Python)
- ✅ Vérifier les types de fichiers (Excel uniquement)
- ✅ Vérifier que les classes Python (CellDown, etc.) sont accessibles
