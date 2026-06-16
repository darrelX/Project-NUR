# Améliorations du système d'upload de fichiers

## 📋 Vue d'ensemble

Le système d'upload de fichiers a été amélioré pour permettre une gestion complète des fichiers Excel avec sélection de feuilles, compatible avec ApiService.ts.

## ✨ Nouvelles fonctionnalités

### 1. Upload de fichiers avec drag & drop dans ConfigForm

- **Interface visuelle moderne** avec zone de dépôt
- **Support drag & drop** pour une UX fluide
- **Validation des formats** : Excel (.xlsx, .xls) et CSV
- **Prévisualisation du fichier** uploadé avec nom et taille
- **Bouton de suppression** pour réinitialiser le fichier

### 2. Sélecteur automatique de feuilles Excel

- **Détection automatique** des feuilles Excel disponibles
- **Sélecteur déroulant** pour choisir la feuille à traiter
- **Sélection automatique** de la première feuille par défaut
- **Compteur de feuilles** détectées

### 3. Compatibilité complète avec ApiService.ts

- Signature mise à jour : `onSubmit(config: ConfigData, file: File)`
- Le fichier et la config sont passés ensemble au backend
- La feuille sélectionnée est automatiquement ajoutée à la config via `target_sheet_name`

## 🔧 Fichiers modifiés

### Frontend (TypeScript/React)

#### `ConfigForm.tsx` - Refonte complète
```typescript
// Nouvelles fonctionnalités
- useState pour uploadedFile, sheetNames, selectedSheet, isDragging
- handleFileSelect() : lecture du fichier et extraction des feuilles
- handleDrop(), handleDragOver(), handleDragLeave() : gestion drag & drop
- Interface d'upload visuelle avec feedback
- Sélecteur de feuille Excel dynamique
```

#### `apiService.ts` - Amélioration du type SaveStatus
```typescript
type SaveStatus = {
  success: boolean;
  file_exists: boolean;
  message: string;
  file_path?: string;  // ✅ Nouveau champ
};
```

#### `App.tsx` - Nettoyage
- Suppression de la variable inutilisée `mainFile`
- Correction des références à `localStorage`

### Backend (Python/Flask)

#### `app.py` - Endpoint amélioré
```python
@app.route("/api/get-data", methods=["GET"])
def get_data():
    # ✅ Ajout du champ file_path dans la réponse
    return jsonify({
        "success": file_exists,
        "file_exists": file_exists,
        "message": "...",
        "file_path": _main_file_path  # Nouveau
    })
```

## 🎯 Flux utilisateur

1. **Sélection de catégorie** → CategorySelector
2. **Upload du fichier** → ConfigForm avec drag & drop
3. **Sélection de feuille** → Sélecteur automatique (si Excel)
4. **Configuration optionnelle** → Champs selon la catégorie
5. **Validation** → Le fichier + config sont envoyés à ApiService
6. **Traitement backend** → CellDown, Xlookup ou Ticket
7. **Mise à jour de l'état** → Fichier ajouté à la liste

## 📦 Dépendances utilisées

- **xlsx** (`^0.18.5`) : Lecture des feuilles Excel côté client
- **react** (`^19.2.5`) : Framework UI
- **typescript** (`~6.0.2`) : Type safety

## 🚀 Utilisation

```tsx
// Le composant ConfigForm est automatiquement appelé après la sélection de catégorie
<ConfigForm
  category={selectedCategory}
  onSubmit={(config, file) => {
    // config contient tous les paramètres + target_sheet_name
    // file contient le fichier uploadé
    apiService.processCelldown(file, config)
  }}
  onCancel={() => setIsConfigFormOpen(false)}
/>
```

## 📝 Exemple de config générée

```json
{
  "target_sheet_name": "Feuil1",
  "source_sheet_path": "Sheet1",
  "date_str": "2024-01-15",
  "result_column_name": "Actions en cours"
}
```

## 🎨 Interface utilisateur

### Avant upload
- Zone de dépôt avec icône
- Instructions claires
- Formats acceptés affichés

### Après upload
- Carte verte avec icône de succès
- Nom du fichier
- Taille affichée
- Bouton de suppression

### Sélecteur de feuille
- Select dropdown avec toutes les feuilles
- Sélection automatique de la première
- Compteur de feuilles détectées

## ✅ Tests recommandés

1. **Test d'upload** : Vérifier que les fichiers Excel/CSV sont acceptés
2. **Test de lecture** : Vérifier que les feuilles sont correctement détectées
3. **Test de validation** : Vérifier que le bouton "Valider" est désactivé sans fichier
4. **Test de suppression** : Vérifier que le fichier peut être supprimé et re-uploadé
5. **Test backend** : Vérifier que le fichier + config arrivent correctement au backend

## 🔍 Points d'attention

- La bibliothèque `xlsx` lit les fichiers côté client (pas de roundtrip backend)
- Les fichiers CSV n'ont pas de notion de "feuille" (le sélecteur ne s'affiche pas)
- Le champ `target_sheet_name` est automatiquement ajouté à la config si une feuille est sélectionnée
- Les paramètres optionnels varient selon la catégorie (CellDown, OCM RAN, Ticket)

## 📊 Compatibilité

| Composant | Status |
|-----------|--------|
| ApiService.ts | ✅ Compatible |
| Backend Flask | ✅ Compatible |
| ConfigForm | ✅ Mis à jour |
| App.tsx | ✅ Compatible |
| CategorySelector | ✅ Compatible |

## 🎉 Résultat

Le système d'upload est maintenant :
- ✅ Plus intuitif avec drag & drop
- ✅ Plus puissant avec sélection de feuilles
- ✅ Mieux intégré avec ApiService.ts
- ✅ Plus robuste avec validation
- ✅ Plus moderne visuellement
