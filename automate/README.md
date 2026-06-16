# Plateforme de Traitement Excel 🚀

Application Streamlit professionnelle pour exécuter trois moteurs de traitement Excel : **CellDown**, **Ticket** et **OCM RAN**.

## 🌟 Fonctionnalités

### 📂 Source principale
- Upload et analyse de fichiers Excel (.xlsx, .xls)
- Sélection de feuille avec détection automatique
- Prévisualisation des données (50 premières lignes)
- Statistiques en temps réel (lignes, colonnes, taille)

### 📱 CellDown
- Filtrage par date avec générateur automatique (DDMMYYYY)
- Configuration des colonnes clés (source et cible)
- Paramètres avancés personnalisables
- Génération automatique du nom de référence

### 🎫 Ticket
- Extraction automatique de codes sites (préfixes CTR_, SUO_, etc.)
- Concaténation multi-colonnes (TEXTJOIN)
- Gestion des filtres Excel automatique
- Configuration flexible des colonnes

### 📡 OCM RAN
- Recherche XLOOKUP entre fichiers
- Configuration de feuille cible
- Personnalisation des colonnes clés et valeurs

### 🔍 Prévisualisation
- Analyse des correspondances avant exécution
- Statistiques de matching
- Taux de couverture par catégorie

### ⚙️ Exécution
- Barre de progression en temps réel
- Logs détaillés avec timestamps
- Résultats colorés par catégorie
- Gestion d'erreurs robuste

### 👁️ Aperçu des résultats
- Visualisation du fichier enrichi
- Filtre par colonnes
- Recherche dans les données
- Statistiques de remplissage
- Export CSV
- Graphiques interactifs (avec plotly)

## 🎨 Design moderne

Interface inspirée de :
- Notion
- Airtable  
- Power BI
- Material Design 3

Avec :
- Cards élégantes avec ombres
- Icônes colorées par catégorie
- Animations fluides
- Responsive design
- Thème professionnel

## 📁 Structure du projet

```
automate/
├── app.py                      # Application principale Streamlit
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
│
├── celldown.py                 # Classe CellDown existante
├── ticket.py                   # Classe Ticket existante
├── super_xlookup.py           # Classe SuperXlookup existante
│
├── components/                 # Composants d'interface
│   ├── __init__.py
│   ├── source_panel.py        # Configuration source
│   ├── celldown_card.py       # Carte CellDown
│   ├── ticket_card.py         # Carte Ticket
│   ├── ocm_card.py            # Carte OCM RAN
│   ├── execution_panel.py     # Panneau d'exécution
│   └── preview_panel.py       # Prévisualisation
│
├── services/                   # Services de traitement
│   ├── __init__.py
│   ├── celldown_service.py    # Service CellDown
│   ├── ticket_service.py      # Service Ticket
│   └── ocm_service.py         # Service OCM RAN
│
└── utils/                      # Utilitaires
    ├── __init__.py
    ├── styles.py              # Styles CSS personnalisés
    ├── logger.py              # Système de logging
    └── excel_utils.py         # Utilitaires Excel
```

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes

1. **Cloner ou naviguer vers le dossier**
```powershell
cd "c:\Users\f50056342\Desktop\computer science\NUR Project Lyne\automate"
```

2. **Créer un environnement virtuel (recommandé)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Installer les dépendances**
```powershell
pip install -r requirements.txt
```

## 🎯 Utilisation

### Lancement de l'application

```powershell
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

### Workflow complet

1. **Configurer la source**
   - Uploadez votre fichier Excel principal
   - Sélectionnez la feuille à traiter
   - Prévisualisez les données (optionnel)

2. **Configurer les catégories**
   - **CellDown** : Uploadez le fichier + sélectionnez la date
   - **Ticket** : Uploadez le fichier
   - **OCM RAN** : Uploadez le fichier
   - Ajustez les paramètres avancés si nécessaire

3. **Prévisualiser** (optionnel)
   - Cliquez sur "🔍 Prévisualiser les résultats"
   - Consultez les statistiques de correspondances

4. **Exécuter**
   - Cliquez sur "▶ Exécuter les traitements"
   - Suivez la progression en temps réel
   - Consultez les logs détaillés

5. **Consulter les résultats**
   - Ouvrez l'aperçu des résultats
   - Filtrez et recherchez dans les données
   - Téléchargez en CSV si besoin

## ⚙️ Configuration des paramètres

### CellDown - Paramètres avancés

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `colown_key_path_source` | `Codesite` | Colonne clé dans le fichier source |
| `target_key_column` | `[Site Code, SITE_CODE, ...]` | Colonnes clés possibles (cible) |
| `target_value_column` | `[Comment, COMMENT, ...]` | Colonnes valeurs possibles |
| `result_position_column` | `last_column` | Position du résultat |
| `reference_name` | Auto | Nom de référence (auto-généré) |

### Ticket - Paramètres avancés

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `source_key_column` | `B` | Colonne clé source |
| `result_position_column` | `last_free` | Position du résultat |
| `result_column_name` | `Ticket` | Nom de la colonne résultat |
| `reference_name` | `Ticket` | Nom de référence |
| `target_join_columns` | `[L, W, X, Y, Z]` | Colonnes à concaténer |
| `join_separator` | `..` | Séparateur TEXTJOIN |
| `ignore_empty` | `True` | Ignorer les cellules vides |
| `extract_source_column` | `T` | Colonne d'extraction des codes |

### OCM RAN - Paramètres avancés

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `source_key_column` | `B` | Colonne clé source |
| `target_key_column` | `D` | Colonne clé cible |
| `target_value_column` | `J` | Colonne valeur cible |
| `result_position_column` | `last_column` | Position du résultat |
| `result_column_name` | `OCM RAN` | Nom de la colonne résultat |
| `target_sheet_name` | `ALL SITES DOWN` | Feuille cible |
| `reference_name` | `` | Nom de référence (optionnel) |

## 📊 Aperçu des résultats

L'application génère automatiquement :
- Statistiques de correspondances par catégorie
- Taux de remplissage des nouvelles colonnes
- Graphiques de répartition (si plotly installé)
- Export CSV des données enrichies

## 🔧 Personnalisation

### Modifier les styles

Éditez `utils/styles.py` pour personnaliser :
- Couleurs (variables CSS)
- Tailles de police
- Ombres et bordures
- Animations

### Ajouter une nouvelle catégorie

1. Créer un service dans `services/`
2. Créer un composant dans `components/`
3. Intégrer dans `app.py`

## 🐛 Dépannage

### Erreur d'import
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution** : `pip install -r requirements.txt`

### Fichier non trouvé
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Solution** : Vérifiez que les fichiers uploadés sont bien présents dans `temp_uploads/`

### Erreur de colonne
```
KeyError: 'Codesite'
```
**Solution** : Vérifiez les noms de colonnes dans les paramètres avancés

## 📝 Logs

Les logs sont affichés en temps réel avec :
- `[HH:MM:SS]` Timestamp
- `ℹ️` Info
- `✅` Succès
- `⚠️` Warning
- `❌` Erreur

## 🔐 Sécurité

- Les fichiers uploadés sont stockés temporairement dans `automate/temp_uploads/`
- Aucune donnée n'est envoyée à des serveurs externes
- Les fichiers sont traités localement

## 🚦 Performance

- Prévisualisation limitée à 50-100 lignes pour la rapidité
- Lecture optimisée avec pandas
- Gestion mémoire efficace avec openpyxl

## 📚 Ressources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Openpyxl Documentation](https://openpyxl.readthedocs.io/)

## 👨‍💻 Contribution

Pour toute amélioration ou bug, contactez l'équipe NUR Project Lyne.

## 📄 License

© 2026 NUR Project Lyne - Tous droits réservés

---

**Version** : 1.0  
**Dernière mise à jour** : 14 juin 2026  
**Auteur** : NUR Project Lyne
