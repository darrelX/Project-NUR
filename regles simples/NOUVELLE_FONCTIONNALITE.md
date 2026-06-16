# 🎉 Nouvelle Fonctionnalité : create_dataframe_from_comments()

## 📌 Vue d'ensemble

Une nouvelle fonction a été ajoutée au module `rules.py` pour simplifier la création de DataFrames à partir de listes de commentaires. Cette fonction est parfaite pour :
- Créer rapidement des données de test
- Intégrer des données d'APIs
- Traiter des listes de commentaires de n'importe quelle source
- Prototyper rapidement

## 🔧 Signature

```python
def create_dataframe_from_comments(
    comments: list[str],
    owners: list[str] | str | None = None,
    topologies: list[str] | str | None = None,
) -> pd.DataFrame
```

## 📝 Paramètres

### `comments` (obligatoire)
Liste de commentaires à traiter.

### `owners` (optionnel)
Peut être :
- `None` → utilise "IHS" pour tous (défaut)
- `str` → même valeur pour tous les commentaires
- `list[str]` → une valeur par commentaire

### `topologies` (optionnel)
Peut être :
- `None` → utilise "Grid Only" pour tous (défaut)
- `str` → même valeur pour tous les commentaires
- `list[str]` → une valeur par commentaire

**Note :** La colonne `Complexity` est automatiquement définie à "Cas Simple" pour tous.

## 💡 Exemples d'Utilisation

### Exemple 1 : Utilisation basique
```python
from rules import create_dataframe_from_comments

comments = ["Grid outage", "Power cut", "ENEO failure"]
df = create_dataframe_from_comments(comments)
```

**Résultat :**
```
      COMMENTAIRE Owner   Topology  Complexity
0    Grid outage   IHS  Grid Only  Cas Simple
1      Power cut   IHS  Grid Only  Cas Simple
2   ENEO failure   IHS  Grid Only  Cas Simple
```

### Exemple 2 : Avec différents owners
```python
comments = ["Grid outage", "Power cut", "GE failure"]
owners = ["IHS", "CAMUSAT", "ESCO"]

df = create_dataframe_from_comments(comments, owners=owners)
```

**Résultat :**
```
   COMMENTAIRE    Owner   Topology  Complexity
0  Grid outage      IHS  Grid Only  Cas Simple
1    Power cut  CAMUSAT  Grid Only  Cas Simple
2   GE failure     ESCO  Grid Only  Cas Simple
```

### Exemple 3 : Avec valeur unique pour tous
```python
comments = ["Power failure", "GE issue"]

df = create_dataframe_from_comments(
    comments,
    owners="CAMUSAT",
    topologies="Solar Hybrid"
)
```

**Résultat :**
```
      COMMENTAIRE    Owner      Topology  Complexity
0  Power failure  CAMUSAT  Solar Hybrid  Cas Simple
1       GE issue  CAMUSAT  Solar Hybrid  Cas Simple
```

### Exemple 4 : Intégration complète
```python
from rules import create_dataframe_from_comments, process_breakdown_data

# 1. Créer le DataFrame
comments = ["Grid outage", "Power cut ENEO"]
df = create_dataframe_from_comments(comments, owners="IHS")

# 2. Traiter avec la logique métier
result = process_breakdown_data(df)

# 3. Afficher les résultats enrichis
print(result[['COMMENTAIRE', 'SUB RCA', 'CATEGORY', 'CAUSE']])
```

**Résultat :**
```
      COMMENTAIRE                           SUB RCA CATEGORY        CAUSE
0    Grid outage  Coupure ENEO & Baisse de tension  PASSIVE  POWER ISSUE
1  Power cut ENEO  Coupure ENEO & Baisse de tension  PASSIVE  POWER ISSUE
```

## 🚀 Cas d'Usage

### 1. Données de test
```python
test_comments = ["Grid down", "Power failure", "GE issue"]
test_df = create_dataframe_from_comments(test_comments)
```

### 2. Intégration API
```python
# Recevoir des données d'une API
api_response = [
    {"comment": "Grid outage", "owner": "IHS"},
    {"comment": "Power failure", "owner": "CAMUSAT"}
]

comments = [item["comment"] for item in api_response]
owners = [item["owner"] for item in api_response]

df = create_dataframe_from_comments(comments, owners=owners)
result = process_breakdown_data(df)
```

### 3. Traitement par lots
```python
batches = {
    "IHS Sites": ["Grid outage site A", "Power cut site B"],
    "CAMUSAT Sites": ["GE failure site C", "ENEO cut site D"]
}

for batch_name, batch_comments in batches.items():
    owner = batch_name.split()[0]
    df = create_dataframe_from_comments(batch_comments, owners=owner)
    result = process_breakdown_data(df)
    print(f"{batch_name}: {len(result)} incidents traités")
```

### 4. Lecture depuis fichier texte
```python
# Lire des commentaires depuis un fichier texte
with open("comments.txt", "r") as f:
    comments = [line.strip() for line in f if line.strip()]

df = create_dataframe_from_comments(comments)
result = process_breakdown_data(df)
```

## ✅ Avantages

1. **Simplicité** : Créez un DataFrame en une seule ligne
2. **Flexibilité** : Accepte différents formats de paramètres
3. **Validation** : Vérifie automatiquement la cohérence des données
4. **Intégration** : S'intègre parfaitement avec `process_breakdown_data()`
5. **Valeurs par défaut intelligentes** : Utilise des valeurs sensées par défaut

## 📚 Ressources

### Démonstrations
```bash
# Voir 6 exemples complets
python "regles simples/demo_comments.py"
```

### Tests
La fonction est testée dans `test_rules.py` avec plusieurs scénarios :
- Valeurs par défaut
- Différents owners
- Différentes topologies
- Valeurs uniques
- Validation d'erreurs

### Documentation
- `README.md` : Documentation complète
- `QUICKSTART.md` : Guide de démarrage rapide
- `demo_comments.py` : 6 exemples détaillés

## 🎓 Pour Aller Plus Loin

### Combinaison avec d'autres sources
```python
# Combiner avec un chargement depuis Excel
from rules import load_data_from_config, create_dataframe_from_comments, process_breakdown_data
import pandas as pd

# Charger depuis Excel
config = {"source_type": "excel", "input_file": Path("data.xlsx"), "sheet_name": "Sheet1"}
df_excel = load_data_from_config(config)

# Ajouter des commentaires supplémentaires
new_comments = ["Additional grid outage", "New power failure"]
df_new = create_dataframe_from_comments(new_comments)

# Combiner
df_combined = pd.concat([df_excel, df_new], ignore_index=True)

# Traiter le tout
result = process_breakdown_data(df_combined)
```

### API REST avec Flask
```python
from flask import Flask, request, jsonify
from rules import create_dataframe_from_comments, process_breakdown_data

app = Flask(__name__)

@app.route('/process-comments', methods=['POST'])
def process_comments():
    data = request.get_json()
    
    comments = data.get('comments', [])
    owners = data.get('owners', None)
    topologies = data.get('topologies', None)
    
    # Créer DataFrame
    df = create_dataframe_from_comments(comments, owners, topologies)
    
    # Traiter
    result = process_breakdown_data(df)
    
    # Retourner JSON
    return jsonify({
        'success': True,
        'processed': len(result),
        'data': result[['COMMENTAIRE', 'SUB RCA', 'CATEGORY']].to_dict(orient='records')
    })
```

## 🔍 Validation et Erreurs

La fonction valide automatiquement :
- Liste de commentaires non vide
- Cohérence des longueurs de listes
- Types de paramètres corrects

Exemples d'erreurs :
```python
# Erreur : liste vide
df = create_dataframe_from_comments([])
# ValueError: La liste de commentaires ne peut pas être vide

# Erreur : longueurs incohérentes
df = create_dataframe_from_comments(
    comments=["A", "B"],
    owners=["IHS"]  # Longueur 1, devrait être 2
)
# ValueError: La liste owners doit avoir la même longueur que comments
```

## 📊 Impact sur le Code

### Avant
```python
import pandas as pd

# Création manuelle fastidieuse
df = pd.DataFrame({
    "COMMENTAIRE": ["Grid outage", "Power cut"],
    "Owner": ["IHS", "CAMUSAT"],
    "Topology": ["Grid Only", "Grid Only"],
    "Complexity": ["Cas Simple", "Cas Simple"]
})
```

### Après
```python
from rules import create_dataframe_from_comments

# Une seule ligne !
df = create_dataframe_from_comments(
    comments=["Grid outage", "Power cut"],
    owners=["IHS", "CAMUSAT"]
)
```

## 🎯 Conclusion

La fonction `create_dataframe_from_comments()` rend le code beaucoup plus flexible et facile à utiliser. Elle est particulièrement utile pour :
- Prototypage rapide
- Tests
- Intégration avec APIs
- Scripts automatisés
- Traitement de données textuelles

**Utilisez-la pour simplifier votre code et gagner du temps !** 🚀
