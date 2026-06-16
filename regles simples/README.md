# Module de Règles Simples - Architecture Flexible

## Vue d'ensemble

Ce module traite les données de breakdown en appliquant des règles métier pour enrichir automatiquement les colonnes SUB RCA, CATEGORY, CAUSE et OCM_NOMENCLATURE.

### Architecture Flexible

L'architecture a été conçue pour être **source-agnostique** : le traitement est indépendant de la provenance des données.

```
┌─────────────────┐
│  Sources de     │
│  données        │
│  - Excel        │
│  - CSV          │
│  - DataFrame    │
│  - API          │
│  - Base de      │
│    données      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Chargement     │
│  (Configurable) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Traitement     │
│  Principal      │
│  process_       │
│  breakdown_data │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Sauvegarde     │
│  (Configurable) │
└─────────────────┘
```

## Fonctions Principales

### 0. `create_dataframe_from_comments(comments, owners=None, topologies=None) -> pd.DataFrame`

**Fonction utilitaire** - Crée rapidement un DataFrame à partir d'une liste de commentaires.

```python
from rules import create_dataframe_from_comments

# Utilisation basique
comments = ["Grid outage", "Power cut", "ENEO failure"]
df = create_dataframe_from_comments(comments)

# Avec owners spécifiques
df = create_dataframe_from_comments(
    comments=["Grid outage", "Power cut"],
    owners=["IHS", "CAMUSAT"]
)

# Avec une valeur unique pour tous
df = create_dataframe_from_comments(
    comments=["Power failure", "GE issue"],
    owners="CAMUSAT",
    topologies="Solar Hybrid"
)
```

**Paramètres :**
- `comments` (list[str], obligatoire) : Liste de commentaires
- `owners` (None | str | list[str], optionnel) : Owner(s) - défaut: "IHS"
- `topologies` (None | str | list[str], optionnel) : Topologie(s) - défaut: "Grid Only"

**Note :** La complexité est automatiquement définie à "Cas Simple" pour tous.

### 1. `process_breakdown_data(df: pd.DataFrame) -> pd.DataFrame`

**Fonction cœur du traitement** - Prend un DataFrame en entrée et retourne un DataFrame enrichi.

```python
import pandas as pd
from rules import process_breakdown_data

# Créer ou charger vos données
df = pd.DataFrame({
    "COMMENTAIRE": ["Grid outage", "Power cut"],
    "Owner": ["IHS", "CAMUSAT"],
    "Topology": ["Grid Only", "Grid Only"],
    "Complexity": ["Cas Simple", "Cas Simple"]
})

# Traiter
df_enriched = process_breakdown_data(df)
```

**Colonnes requises en entrée :**
- `COMMENTAIRE` : Description du problème
- `Owner` : Propriétaire du site (IHS, CAMUSAT, ESCO, etc.)
- `Topology` ou `Topolopgy` : Type de topologie
- `Complexity` (ou variantes) : Complexité du cas

**Colonnes ajoutées en sortie :**
- `SUB RCA` : Sous-catégorie de cause racine
- `CATEGORY` : Catégorie du problème
- `CAUSE` : Cause du problème
- `OCM_NOMENCLATURE` : Nomenclature OCM

### 2. `load_data_from_config(config: dict) -> pd.DataFrame`

Charge les données selon la configuration spécifiée.

```python
from pathlib import Path
from rules import load_data_from_config

config = {
    "source_type": "excel",
    "input_file": Path("inputs/data.xlsx"),
    "sheet_name": "BREAKDOWN"
}

df = load_data_from_config(config)
```

### 3. `main(config: dict = None)`

Fonction orchestratrice complète : charge, traite et sauvegarde les données.

```python
from rules import main

# Utiliser la configuration par défaut
main()

# Ou avec une configuration personnalisée
custom_config = {
    "source_type": "csv",
    "input_file": Path("data/breakdown.csv"),
    "output_file": Path("output/result.csv"),
}
main(custom_config)
```

## Configuration

### Structure de Configuration

```python
CONFIG = {
    "source_type": "excel",      # Type de source: "excel", "csv", "dataframe"
    "input_file": Path("..."),   # Chemin du fichier d'entrée
    "output_file": Path("..."),  # Chemin du fichier de sortie
    "sheet_name": "BREAKDOWN",   # Nom de la feuille (pour Excel)
    "csv_encoding": "utf-8",     # Encodage (pour CSV)
    "csv_separator": ",",        # Séparateur (pour CSV)
}
```

### Types de Sources Supportés

#### Excel
```python
config = {
    "source_type": "excel",
    "input_file": Path("inputs/data.xlsx"),
    "output_file": Path("outputs/result.xlsx"),
    "sheet_name": "BREAKDOWN",
}
```

#### CSV
```python
config = {
    "source_type": "csv",
    "input_file": Path("inputs/data.csv"),
    "output_file": Path("outputs/result.csv"),
    "csv_encoding": "utf-8",
    "csv_separator": ",",
}
```

#### DataFrame Direct (API, Base de données, etc.)
```python
# Pas besoin de configuration de chargement
df = pd.DataFrame(...)  # Vos données
df_result = process_breakdown_data(df)
```

## Cas d'Usage

### Cas 1 : Utilisation Standard

```python
from rules import main

# Utilise la configuration par défaut définie dans le module
main()
```

### Cas 2 : Traitement par Lots

```python
from pathlib import Path
from rules import main

fichiers = [
    {"source_type": "excel", "input_file": Path("inputs/april.xlsx"), ...},
    {"source_type": "excel", "input_file": Path("inputs/may.xlsx"), ...},
    {"source_type": "excel", "input_file": Path("inputs/june.xlsx"), ...},
]

for config in fichiers:
    main(config)
```

### Cas 3 : Intégration API

```python
from flask import Flask, request, jsonify
import pandas as pd
from rules import process_breakdown_data

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_api():
    # Recevoir des données JSON
    data = request.get_json()
    
    # Créer DataFrame
    df = pd.DataFrame(data)
    
    # Traiter
    df_result = process_breakdown_data(df)
    
    # Retourner en JSON
    return jsonify(df_result.to_dict(orient='records'))
```

### Cas 4 : Pipeline Personnalisé

```python
from rules import load_data_from_config, process_breakdown_data, save_data
from pathlib import Path

# 1. Charger
config = {"source_type": "excel", "input_file": Path("data.xlsx"), "sheet_name": "Sheet1"}
df = load_data_from_config(config)

# 2. Pré-traitement personnalisé
df = df[df['Status'] == 'Active']

# 3. Traitement principal
df_enriched = process_breakdown_data(df)

# 4. Post-traitement
df_filtered = df_enriched[df_enriched['SUB RCA'].notna()]

# 5. Sauvegarde
save_data(df_filtered, Path("output.xlsx"))
```

### Cas 5 : Intégration Base de Données

```python
import pandas as pd
from sqlalchemy import create_engine
from rules import process_breakdown_data

# Lire depuis base de données
engine = create_engine('postgresql://user:pass@localhost/db')
df = pd.read_sql("SELECT * FROM breakdown_data", engine)

# Traiter
df_enriched = process_breakdown_data(df)

# Sauvegarder dans la base
df_enriched.to_sql('breakdown_enriched', engine, if_exists='replace')
```

## Logique Métier

### Détection de Problèmes de Power

Le module détecte automatiquement les problèmes liés au power en recherchant des mots-clés :
- power, grid outage, awaiting grid return
- ENEO, baisse de tension, coupure
- grid failure, power cut, electricity
- etc.

### Détermination du SUB RCA

Basé sur :
1. **Commentaire** : Détection de mots-clés
2. **Owner** : IHS, CAMUSAT, ESCO
3. **Topology** : Grid Only, Solar Hybrid, etc.

### Enrichissement Automatique

Une fois le SUB RCA déterminé, les colonnes suivantes sont automatiquement remplies via des mappings :
- `CATEGORY` : ACTIVE, PASSIVE, PLANNED WORKS, etc.
- `CAUSE` : TX ISSUE, RAN ISSUE, POWER ISSUE, etc.
- `OCM_NOMENCLATURE` : PDH, BSS, AKTIVCO, IHS, etc.

## Exemples Pratiques

Voir le fichier `example_usage.py` pour 7 exemples détaillés :

```bash
python "regles simples/example_usage.py"
```

## Extension Future

Pour ajouter de nouvelles sources de données :

```python
def load_data_from_nouvelle_source(params) -> pd.DataFrame:
    """Charge depuis une nouvelle source."""
    # Votre logique de chargement
    return df

# Modifier load_data_from_config pour l'inclure
def load_data_from_config(config: dict) -> pd.DataFrame:
    source_type = config.get("source_type")
    
    if source_type == "nouvelle_source":
        return load_data_from_nouvelle_source(config)
    # ... autres sources
```

## Avantages de l'Architecture

✅ **Flexibilité** : Supporte multiples sources de données  
✅ **Réutilisabilité** : Fonction de traitement indépendante  
✅ **Testabilité** : Facile à tester avec des DataFrames  
✅ **Évolutivité** : Ajout facile de nouvelles sources  
✅ **Intégration** : Utilisable dans APIs, pipelines, etc.  

## Support

Pour toute question ou amélioration, référez-vous au code source ou consultez les exemples.
