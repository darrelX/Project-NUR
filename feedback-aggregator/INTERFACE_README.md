# Interface de Configuration - Breakdown

Cette application React permet de configurer et exécuter des opérations Excel via les classes Python **CellDown** et **SuperXlookup**.

## 📁 Structure des fichiers

### Types et Configuration
- **[types/index.ts](src/types/index.ts)** - Définitions TypeScript pour les configurations CellDown et SuperXlookup
- **[constants/index.ts](src/constants/index.ts)** - Valeurs par défaut pour chaque type d'opération
- **[utils/fileHelpers.ts](src/utils/fileHelpers.ts)** - Fonctions utilitaires pour la gestion des fichiers

### Composants React
- **[components/Header.tsx](src/components/Header.tsx)** - En-tête avec bouton d'ajout de fichier
- **[components/FileList.tsx](src/components/FileList.tsx)** - Liste des fichiers sources avec statuts
- **[components/FileDetails.tsx](src/components/FileDetails.tsx)** - Panneau de détails du fichier sélectionné
- **[components/OperationConfig.tsx](src/components/OperationConfig.tsx)** - Configuration dynamique des opérations (CellDown/SuperXlookup)
- **[components/PreviewArea.tsx](src/components/PreviewArea.tsx)** - Zone d'aperçu global
- **[components/Footer.tsx](src/components/Footer.tsx)** - Barre de progression et compilation

### Services
- **[services/compilationService.ts](src/services/compilationService.ts)** - Communication avec le backend Python

### Fichier principal
- **[App.tsx](src/App.tsx)** - Gestion de l'état et coordination des composants

## 🔧 Fonctionnalités

### Configuration SuperXlookup
Permet de configurer tous les paramètres nécessaires :
- Feuille source et cible (sélection dynamique)
- Colonnes clés (source et cible)
- Colonne valeur à rapporter
- Position du résultat (colonnes A-Z ou "dernière libre")
- Nom personnalisé de la colonne résultat

### Configuration CellDown
Permet de configurer :
- Feuille source (sélection dynamique)
- Date au format DDMMYYYY
- Colonnes clés (source et cible)
- Colonne valeur
- Position du résultat
- Colonne de départ

### Sélection dynamique des feuilles
Les feuilles Excel disponibles dans chaque fichier sont listées automatiquement et peuvent être sélectionnées via des dropdowns.

### Gestion multi-fichiers
- Ajout/suppression de fichiers
- Configuration indépendante pour chaque fichier
- Statuts visuels (couleurs)
- Progression globale

## 🚀 Utilisation

1. **Ajouter un fichier** : Cliquez sur le bouton "Ajouter un fichier"
2. **Sélectionner le type d'opération** : SuperXlookup ou CellDown
3. **Configurer les paramètres** : Choisissez les feuilles et colonnes appropriées
4. **Sélectionner les éléments** : Cochez les éléments de breakdown à traiter
5. **Lancer la compilation** : Cliquez sur "Lancer la compilation"

## 🔌 Intégration Backend

Le service `compilationService.ts` fournit les fonctions pour :
- `runCompilation()` - Exécuter une opération
- `getAvailableSheets()` - Récupérer les feuilles d'un fichier Excel
- `getAvailableColumns()` - Récupérer les colonnes d'une feuille
- `uploadFile()` - Uploader un fichier Excel

## 📝 Prochaines étapes

- [ ] Implémenter l'upload de fichiers Excel
- [ ] Connecter le backend Python Flask
- [ ] Récupérer dynamiquement les feuilles disponibles
- [ ] Afficher les résultats de compilation
- [ ] Ajouter la validation des champs
- [ ] Implémenter la sauvegarde des configurations
