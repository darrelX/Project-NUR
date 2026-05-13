# 🔄 Architecture de l'Interface Streamlit

## Flux de Traitement Séquentiel

```
┌─────────────────────────────────────────────────────────┐
│          📁 FICHIER SOURCE COMMUN (Book1.xlsx)          │
│                                                          │
│  - Chargé une seule fois                                │
│  - Modifié séquentiellement par chaque opération        │
│  - Sauvegardé après chaque opération                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  ✅ CellDown activé ?  │
        └────────┬───────────────┘
                 │ OUI
                 ▼
┌────────────────────────────────────────────────────────┐
│                    🔽 CELLDOWN                         │
│                                                        │
│  1. Charge le fichier cible avec plusieurs feuilles   │
│  2. Filtre les feuilles par date (ex: 12052026)       │
│  3. Pour chaque feuille filtrée :                     │
│     - XLOOKUP entre source et feuille                 │
│     - Ajoute résultat dans colonnes C, D, E...        │
│     - Ajoute préfixe [NOM - date]                     │
│  4. Sauvegarde le fichier source modifié              │
│                                                        │
│  📊 Résultat : Plusieurs colonnes ajoutées            │
└────────────────────┬───────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ ✅ SuperXlookup activ? │
        └────────┬───────────────┘
                 │ OUI
                 ▼
┌────────────────────────────────────────────────────────┐
│                  🔍 SUPER XLOOKUP                      │
│                                                        │
│  1. Charge le fichier cible (une seule feuille)       │
│  2. XLOOKUP simple :                                   │
│     - Clé source ↔ Clé cible                          │
│     - Rapporte une colonne de valeurs                 │
│  3. Ajoute préfixe [NOM - date]                       │
│  4. Écrit dans la colonne spécifiée                   │
│     (ou "last_free" pour ajouter à la fin)            │
│  5. Sauvegarde le fichier source modifié              │
│                                                        │
│  📊 Résultat : Une colonne ajoutée                    │
└────────────────────┬───────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   ✅ Ticket activé ?   │
        └────────┬───────────────┘
                 │ OUI
                 ▼
┌────────────────────────────────────────────────────────┐
│                     🎫 TICKET                          │
│                                                        │
│  1. Charge le fichier cible                            │
│  2. Extrait automatiquement les codes sites :         │
│     - Recherche CTR_, SUO_, NRO_, etc.                │
│     - Crée une colonne de clés temporaire             │
│  3. Concatène plusieurs colonnes (TEXTJOIN) :         │
│     - Ex: L + W + X + Y + Z                           │
│     - Séparateur : ".."                               │
│  4. XLOOKUP entre source et cible                     │
│  5. Ajoute préfixe [NOM - date]                       │
│  6. Écrit dans la colonne spécifiée                   │
│  7. Sauvegarde le fichier source modifié              │
│                                                        │
│  📊 Résultat : Une colonne multi-valeurs ajoutée      │
└────────────────────┬───────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  💾 FICHIER FINAL      │
        │  (avec toutes les      │
        │   colonnes ajoutées)   │
        └────────────────────────┘
```

## 🎨 Interface Utilisateur

```
╔══════════════════════════════════════════════════════════╗
║            🔧 Suite d'Opérations Excel                   ║
╚══════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────┐
│ 📁 FICHIER SOURCE COMMUN                                 │
│                                                          │
│ Chemin : [C:\Users\...\Book1.xlsx    ] ✅ Fichier trouvé│
│ 👁️ Aperçu : [Expandeur]                                 │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ ⚙️ CONFIGURATION DES OPÉRATIONS                          │
│                                                          │
│  ┌─────────────┬──────────────────┬────────────────┐    │
│  │  🔽 CellDown│ 🔍 SuperXlookup  │  🎫 Ticket     │    │
│  ├─────────────┼──────────────────┼────────────────┤    │
│  │             │                  │                │    │
│  │ ✅ Activer  │  ✅ Activer      │  ✅ Activer    │    │
│  │             │                  │                │    │
│  │ [Params...] │  [Params...]     │  [Params...]   │    │
│  │             │                  │                │    │
│  └─────────────┴──────────────────┴────────────────┘    │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ ▶️ EXÉCUTION                                              │
│                                                          │
│ [🚀 Exécuter Toutes les Opérations]  [🗑️ Effacer le Log]│
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ 📋 JOURNAL D'EXÉCUTION                                   │
│                                                          │
│ ✅ CellDown - Terminé avec succès. 3 feuilles traitées  │
│ ✅ SuperXlookup - Terminé. Résultat dans "Commentaire"  │
│ ✅ Ticket - Terminé. TEXTJOIN sur 5 colonnes            │
│ ℹ️ RÉSUMÉ - ✅ 3 succès | ❌ 0 erreurs                   │
│                                                          │
│ 👁️ Aperçu du fichier après traitement : [Expandeur]    │
└──────────────────────────────────────────────────────────┘
```

## 📊 Structure des Données

### Avant Traitement
```
| Codesite | Nom Site | (autres colonnes...) |
|----------|----------|---------------------|
| CTR_001  | Site A   | ...                 |
| SUO_002  | Site B   | ...                 |
```

### Après CellDown (colonnes C, D, E ajoutées)
```
| Codesite | Nom Site | [CellDown - 12/05/2026] 04/05 | [CellDown - 12/05/2026] 05/05 | ... |
|----------|----------|-------------------------------|-------------------------------|-----|
| CTR_001  | Site A   | Down                          | Up                            | ... |
| SUO_002  | Site B   | Up                            | Down                          | ... |
```

### Après SuperXlookup (colonne "Commentaire" ajoutée)
```
| ... | Commentaire                                  |
|-----|----------------------------------------------|
| ... | [NOKIA - 12/05/2026] Incident réseau         |
| ... | [NOKIA - 12/05/2026] Maintenance programmée  |
```

### Après Ticket (colonne "Ticket" ajoutée)
```
| ... | Ticket                                               |
|-----|------------------------------------------------------|
| ... | [Ticket - 12/05/2026] INC001..Urgent..P1..John..RAN |
| ... | [Ticket - 12/05/2026] INC002..Normal..P3..Mary..TX  |
```

## 🔧 Technologies Utilisées

- **Streamlit** : Interface web interactive
- **Pandas** : Manipulation des données Excel
- **OpenPyXL** : Lecture/écriture de fichiers .xlsx
- **Python dataclasses** : Structure des classes métier

## 📦 Dépendances

```txt
streamlit>=1.30.0
pandas>=2.0.0
openpyxl>=3.1.0
```

Installation :
```bash
pip install streamlit pandas openpyxl
```

## 🚀 Avantages de cette Architecture

1. ✅ **Fichier source unique** : Pas de copie multiple, tout est centralisé
2. ✅ **Exécution séquentielle** : Les opérations s'enchaînent automatiquement
3. ✅ **Configuration flexible** : Activation/désactivation individuelle
4. ✅ **Traçabilité** : Journal d'exécution détaillé avec succès/erreurs
5. ✅ **Prévisualisation** : Aperçu avant et après traitement
6. ✅ **Préfixes automatiques** : [NOM - date] ajouté à chaque résultat
7. ✅ **Gestion des erreurs** : Chaque opération peut échouer indépendamment
8. ✅ **Interface intuitive** : Pas besoin de modifier le code Python
