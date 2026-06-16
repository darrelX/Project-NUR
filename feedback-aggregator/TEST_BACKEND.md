# 🧪 Guide de test - Backend Communication

## Problèmes identifiés et corrigés

### 1. **Vérification de santé du backend**
**Problème** : L'application ne vérifiait pas si le backend était accessible avant d'essayer de communiquer.

**Solution** : Ajout d'un check de santé dans `getExcelDataForPreview()`
```typescript
const isHealthy = await apiService.checkHealth()
if (!isHealthy) {
  throw new Error('Backend non accessible...')
}
```

### 2. **Gestion des erreurs améliorée**
**Problème** : Les erreurs n'étaient pas bien capturées et les logs étaient insuffisants.

**Solution** : Ajout de try/catch avec logs détaillés à chaque étape

### 3. **Export depuis le backend**
**Problème** : La fonction `handleExport` utilisait le fichier local au lieu du fichier traité sur le backend.

**Solution** : Modification pour utiliser `apiService.exportFile()`

## Tests à effectuer

### Test 1: Vérifier que le backend est démarré

```powershell
# Terminal 1 - Démarrer le backend
cd backend
python app.py
```

Vous devriez voir :
```
🚀 Starting Flask backend on http://localhost:5000
```

### Test 2: Vérifier la santé du backend

Ouvrez http://localhost:5000/api/health dans votre navigateur

Réponse attendue :
```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

### Test 3: Démarrer le frontend

```powershell
# Terminal 2 - Depuis la racine du projet
npm run dev
```

Ouvrez http://localhost:5173

### Test 4: Upload du fichier principal

1. Cliquez sur "Importer le fichier principal"
2. Sélectionnez un fichier Excel
3. **Vérifiez les logs dans la console du navigateur** (F12)

Logs attendus :
```
🟢 [App] Fichier principal chargé: nom_fichier.xlsx
🔵 [Preview] Chargement aperçu du fichier
🔵 [Preview] Upload du fichier vers le backend...
✅ [Preview] Fichier uploadé: { ... }
🔵 [Preview] Récupération des données...
✅ [Preview] Données récupérées: XX lignes
```

### Test 5: Vérifier l'aperçu

Après l'upload, vous devriez voir :
- ✅ Message "Fichier principal chargé : XX lignes"
- ✅ Le tableau affiche les 5 premières lignes
- ✅ Le nombre de lignes est correct

### Test 6: Traiter un fichier

1. Cliquez sur "Importer un fichier"
2. Choisissez une catégorie (CellDown, Transmission, ou Sites)
3. Configurez les paramètres
4. Uploadez un fichier cible
5. Vérifiez les logs

Logs attendus :
```
🔵 [CellDown/Xlookup/Ticket] Envoi vers le backend
✅ Traitement terminé : XX lignes, YY colonnes
```

### Test 7: Export du fichier

1. Cliquez sur "Exporter Excel"
2. Le fichier devrait se télécharger automatiquement

Logs attendus :
```
🔵 [Export] Téléchargement depuis le backend...
🔵 [Export] Téléchargement du fichier consolidé...
✅ [Export] Fichier téléchargé avec succès
```

## Diagnostics d'erreurs courantes

### Erreur: "Backend non accessible"

**Cause** : Le backend Flask n'est pas démarré

**Solution** :
```powershell
cd backend
python app.py
```

### Erreur: "Failed to fetch"

**Cause** : CORS ou backend non accessible

**Vérifications** :
1. Backend démarré sur http://localhost:5000
2. Pas d'erreur dans les logs du backend
3. CORS activé dans `backend/app.py`

### Erreur: "No file provided"

**Cause** : Le fichier n'a pas été correctement envoyé au backend

**Vérifications** :
1. Regarder les logs du backend (terminal Python)
2. Vérifier que `FormData` est bien créé
3. Vérifier la console du navigateur

### Erreur: "Main file not uploaded"

**Cause** : Le fichier principal n'a pas été uploadé avant de traiter

**Solution** : Toujours uploader le fichier principal en premier

## Structure des appels API

### 1. Upload fichier principal
```
POST /api/upload-main-file
Body: FormData { file: File }
Response: { success, filename, lines, size }
```

### 2. Traitement CellDown
```
POST /api/process-celldown
Body: FormData { file: File, ...config }
Response: { success, lines, columns, data }
```

### 3. Récupération des données
```
GET /api/get-data
Response: { success, lines, columns, data }
```

### 4. Export
```
GET /api/export
Response: Blob (fichier Excel)
```

## Logs détaillés

### Frontend (Console du navigateur)
- 🟢 Vert : Actions principales
- 🔵 Bleu : Appels API
- ✅ Check : Succès
- 🔴 Rouge : Erreurs

### Backend (Terminal Python)
- 📁 Dossier : Chemins de fichiers
- 📄 Fichier : Noms de fichiers
- 🔄 Cycle : Traitement en cours
- ✅ Check : Succès
- ❌ X : Erreurs

## Fichiers modifiés

1. **src/services/excelService.ts**
   - ✅ Ajout de vérification de santé
   - ✅ Meilleure gestion des erreurs
   - ✅ Logs détaillés
   - ✅ Fonction `exportFile()`

2. **src/App.tsx**
   - ✅ `handleExport()` utilise le backend

3. **src/services/apiService.ts**
   - ✅ Méthode `downloadProcessedFile()`
   - ✅ Méthode `checkHealth()`

## Commandes rapides

```powershell
# Démarrer tout
# Terminal 1
cd backend; python app.py

# Terminal 2
npm run dev

# Vérifier la santé
curl http://localhost:5000/api/health

# Nettoyer les fichiers uploadés
cd backend/uploads; rm *.xlsx

# Voir les logs en temps réel
# Regarder les terminaux Python et Node
```

## Checklist avant de tester

- [ ] Backend démarré (port 5000)
- [ ] Frontend démarré (port 5173)
- [ ] Console du navigateur ouverte (F12)
- [ ] Terminal backend visible pour les logs
- [ ] Fichier Excel de test prêt
- [ ] Dossier `backend/uploads/` existe

## Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs du backend (terminal Python)
2. Vérifiez la console du navigateur (F12)
3. Vérifiez que les deux serveurs sont démarrés
4. Testez l'endpoint `/api/health` directement
