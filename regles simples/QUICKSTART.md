# Guide de Démarrage Rapide

## 🚀 Utilisation Simple

### Option 1 : Mode Configuration par Défaut
Le plus simple - utilise les paramètres définis dans `rules.py`:

```bash
python "regles simples/rules.py"
```

### Option 2 : Mode Configuration Nommée
Utilise les configurations définies dans `config.yaml`:

```bash
# Lister toutes les configurations disponibles
python "regles simples/config_loader.py" list

# Exécuter une configuration spécifique
python "regles simples/config_loader.py" default
python "regles simples/config_loader.py" csv_input
python "regles simples/config_loader.py" monthly_april
```

### Option 3 : Mode Batch
Traite plusieurs fichiers en une seule commande:

```bash
# Traiter tous les fichiers mensuels
python "regles simples/config_loader.py" batch batch_monthly

# Traiter toutes les sources configurées
python "regles simples/config_loader.py" batch batch_all_sources
```

### Option 4 : Mode Interactif
Interface interactive pour choisir la configuration:

```bash
python "regles simples/config_loader.py"
```

## 📝 Utilisation Programmatique

### ⭐ Utilisation avec Liste de Commentaires (NOUVEAU)

**La façon la plus simple** de créer des données à traiter :

```python
from rules import create_dataframe_from_comments, process_breakdown_data

# Créer un DataFrame depuis une liste de commentaires
comments = [
    "Grid outage at site",
    "Power cut ENEO",
    "GE failure"
]

df = create_dataframe_from_comments(comments)
result = process_breakdown_data(df)
print(result[['COMMENTAIRE', 'SUB RCA', 'CATEGORY']])
```

**Avec des paramètres personnalisés :**

```python
# Différents owners pour chaque commentaire
df = create_dataframe_from_comments(
    comments=["Grid outage", "Power failure", "GE issue"],
    owners=["IHS", "CAMUSAT", "ESCO"]
)

# Même owner et topologie pour tous
df = create_dataframe_from_comments(
    comments=["Grid outage", "Power failure"],
    owners="CAMUSAT",
    topologies="Solar Hybrid"
)

# Différentes topologies
df = create_dataframe_from_comments(
    comments=["Grid cut", "GE failure"],
    owners=["IHS", "IHS"],
    topologies=["Grid Only", "Solar Hybrid"]
)
```

**Voir la démonstration complète :**

```bash
python "regles simples/demo_comments.py"
```

### Utilisation Basique avec DataFrame

```python
from rules import process_breakdown_data
import pandas as pd

# Vos données (depuis n'importe où)
df = pd.DataFrame({
    "COMMENTAIRE": ["Grid outage at site"],
    "Owner": ["IHS"],
    "Topology": ["Grid Only"],
    "Complexity": ["Cas Simple"]
})

# Traiter
df_enriched = process_breakdown_data(df)

# Utiliser le résultat
print(df_enriched[["SUB RCA", "CATEGORY", "CAUSE"]])
```

### Avec Configuration Personnalisée

```python
from rules import main
from pathlib import Path

# Définir votre configuration
config = {
    "source_type": "excel",
    "input_file": Path("mes_donnees.xlsx"),
    "output_file": Path("resultat.xlsx"),
    "sheet_name": "BREAKDOWN"
}

# Exécuter
main(config)
```

### Pipeline Complet

```python
from rules import load_data_from_config, process_breakdown_data, save_data
from pathlib import Path

# 1. Charger
config = {
    "source_type": "csv",
    "input_file": Path("data.csv")
}
df = load_data_from_config(config)

# 2. Pré-traitement (optionnel)
df_filtered = df[df['Status'] == 'Active']

# 3. Traitement principal
df_enriched = process_breakdown_data(df_filtered)

# 4. Post-traitement (optionnel)
df_final = df_enriched[df_enriched['SUB RCA'].notna()]

# 5. Sauvegarder
save_data(df_final, Path("output.xlsx"))
```

## 🔧 Configuration

### Modifier config.yaml

Ajoutez vos propres configurations dans `config.yaml`:

```yaml
ma_config:
  source_type: "excel"
  input_file: "chemin/vers/fichier.xlsx"
  output_file: "chemin/vers/sortie.xlsx"
  sheet_name: "NOM_FEUILLE"
```

Puis utilisez-la:

```bash
python "regles simples/config_loader.py" ma_config
```

### Configuration Programmée

Directement dans votre code Python:

```python
from rules import CONFIG

# Modifier la configuration par défaut
CONFIG["input_file"] = Path("nouveau_fichier.xlsx")
CONFIG["sheet_name"] = "AUTRE_FEUILLE"

# Utiliser
from rules import main
main()
```

## 📊 Formats Supportés

### Excel
```python
config = {
    "source_type": "excel",
    "input_file": Path("data.xlsx"),
    "sheet_name": "Sheet1"
}
```

### CSV
```python
config = {
    "source_type": "csv",
    "input_file": Path("data.csv"),
    "csv_encoding": "utf-8",
    "csv_separator": ","
}
```

### DataFrame Direct
```python
import pandas as pd
from rules import process_breakdown_data

df = pd.read_sql("SELECT * FROM table", connection)
df_result = process_breakdown_data(df)
```

### Liste de Commentaires (NOUVEAU)
```python
from rules import create_dataframe_from_comments, process_breakdown_data

comments = ["Grid outage", "Power cut", "GE failure"]
df = create_dataframe_from_comments(comments)
df_result = process_breakdown_data(df)
```

## 🎯 Cas d'Usage Courants

### Traiter une liste de commentaires rapidement
```python
from rules import create_dataframe_from_comments, process_breakdown_data

comments = ["Grid down", "Power failure", "ENEO cut"]
df = create_dataframe_from_comments(comments, owners="IHS")
result = process_breakdown_data(df)
```

### Traiter un fichier mensuel
```bash
python "regles simples/config_loader.py" monthly_april
```

### Traiter plusieurs mois en une fois
```bash
python "regles simples/config_loader.py" batch batch_monthly
```

### Intégration dans un script
```python
from rules import process_breakdown_data

# Votre logique de chargement
df = votre_fonction_chargement()

# Traitement
df_enriched = process_breakdown_data(df)

# Suite de votre logique
votre_fonction_sauvegarde(df_enriched)
```

### API REST
```python
from flask import Flask, request, jsonify
from rules import create_dataframe_from_comments, process_breakdown_data

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    
    # Extraire les commentaires
    comments = [item['comment'] for item in data]
    owners = [item.get('owner', 'IHS') for item in data]
    
    # Créer DataFrame et traiter
    df = create_dataframe_from_comments(comments, owners=owners)
    result = process_breakdown_data(df)
    
    return jsonify(result.to_dict(orient='records'))
```

## 🧪 Tests & Démonstrations

### Exécuter les tests unitaires:
```bash
python "regles simples/test_rules.py"
```

### Voir la démonstration complète:
```bash
python "regles simples/demo_comments.py"
```

### Voir tous les exemples:
```bash
python "regles simples/example_usage.py"
```

## 📋 Colonnes Requises

Votre DataFrame doit contenir au minimum:
- `COMMENTAIRE` : Description du problème
- `Owner` : Propriétaire (IHS, CAMUSAT, ESCO, etc.)
- `Topology` ou `Topolopgy` : Type de topologie
- `Complexity` (ou variantes) : Complexité du cas

**💡 Astuce :** Utilisez `create_dataframe_from_comments()` pour créer automatiquement un DataFrame avec toutes les colonnes requises !

## ✨ Fonctionnalités

✅ **Création rapide depuis liste** (nouveau)  
✅ Détection automatique des problèmes de power  
✅ Classification par owner et topologie  
✅ Enrichissement automatique (SUB RCA, CATEGORY, CAUSE, OCM_NOMENCLATURE)  
✅ Support Excel et CSV  
✅ Traitement par lots  
✅ Mode interactif  
✅ Utilisation programmatique flexible  
✅ Tests unitaires complets  

## 🆘 Aide

Pour plus de détails, consultez:
- `README.md` : Documentation complète
- `demo_comments.py` : Démonstration de create_dataframe_from_comments
- `example_usage.py` : 7 exemples détaillés d'utilisation
- `test_rules.py` : Tests unitaires et cas d'usage

Pour obtenir de l'aide en ligne de commande:

```bash
python "regles simples/config_loader.py"
```

## 📞 Support

En cas de problème:
1. Utilisez `create_dataframe_from_comments()` pour créer rapidement des données valides
2. Vérifiez que les colonnes requises sont présentes
3. Vérifiez le format de votre configuration
4. Consultez les exemples dans `demo_comments.py` et `example_usage.py`
5. Exécutez les tests pour valider l'installation
