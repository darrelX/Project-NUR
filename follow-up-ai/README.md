# 🤖 Projet de Fine-Tuning : Analyse d'Incidents Réseau

Ce projet propose une architecture modulaire complète pour fine-tuner un modèle LLM (Qwen2.5-3B-Instruct) afin d'analyser et classifier automatiquement les incidents réseau télécom.

## 📁 Structure du Projet

```
follow-up-ai/
├── main.py                    # Point d'entrée principal
├── requirements.txt           # Dépendances Python
├── README.md                 # Ce fichier
│
├── config/                   # Configuration
│   ├── __init__.py
│   ├── config_manager.py    # Gestionnaire de configuration
│   ├── paths.yaml           # Chemins des fichiers
│   ├── lora_config.yaml     # Configuration LoRA
│   └── train_config.yaml    # Configuration entraînement
│
├── data/                     # Gestion des données
│   ├── __init__.py
│   ├── loader.py            # Chargeur de données JSONL
│   ├── preprocessing.py     # Prétraitement et formatage
│   └── tokenization.py      # Gestionnaire de tokenizer
│
├── models/                   # Gestion des modèles
│   ├── __init__.py
│   ├── model_loader.py      # Chargement des modèles
│   └── lora_manager.py      # Gestion de LoRA (merge, config)
│
├── training/                 # Entraînement
│   ├── __init__.py
│   └── trainer.py           # Gestionnaire d'entraînement
│
├── inference/                # Inférence et évaluation
│   ├── __init__.py
│   ├── predictor.py         # Prédictions
│   └── evaluator.py         # Évaluation de performance
│
└── utils/                    # Utilitaires
    ├── __init__.py
    ├── constants.py         # Constantes globales
    └── helpers.py           # Fonctions utilitaires
```

## 🔧 Installation

1. **Cloner le projet** (ou naviguer vers le dossier)

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer les chemins** :
   Éditer `config/paths.yaml` avec vos chemins locaux :
   ```yaml
   base_drive: "/votre/chemin/base"
   train_jsonl: "dataset/train1.jsonl"
   val_jsonl: "dataset/validation1.jsonl"
   # ... etc
   ```

## 🚀 Utilisation

### Pipeline Complet (Entraînement → Merge → Évaluation)

```bash
python main.py full
```

### Étapes Individuelles

#### 1. Entraînement seul
```bash
python main.py train
```

#### 2. Merge LoRA avec modèle de base
```bash
python main.py merge
```

#### 3. Évaluation
```bash
# Avec modèle mergé (recommandé)
python main.py evaluate --use-merged

# Avec base + LoRA
python main.py evaluate
```

#### 4. Prédiction simple
```bash
python main.py predict --commentaire "Votre commentaire d'incident ici"
```

### Options Avancées

```bash
# Spécifier un dossier de configuration personnalisé
python main.py train --config-dir /chemin/vers/config

# Utiliser le modèle mergé pour l'évaluation
python main.py evaluate --use-merged
```

## 📊 Architecture Modulaire

### Classes Principales

#### 1. **ConfigManager** (`config/config_manager.py`)
Gère toutes les configurations depuis les fichiers YAML.

```python
from config.config_manager import ConfigManager

config = ConfigManager()
train_path = config.get_path("train_jsonl")
lora_r = config.get_lora_r()
```

#### 2. **DataLoader** (`data/loader.py`)
Charge et analyse les données JSONL.

```python
from data.loader import DataLoader

loader = DataLoader()
loader.charger_train_val(train_path, val_path)
```

#### 3. **ModelLoader** (`models/model_loader.py`)
Gère le chargement des modèles (base, mergé, avec LoRA).

```python
from models.model_loader import ModelLoader

model_loader = ModelLoader("Qwen/Qwen2.5-3B-Instruct")
model = model_loader.charger_modele_base(use_quantization=True)
```

#### 4. **LoraManager** (`models/lora_manager.py`)
Configure et applique LoRA, gère le merge.

```python
from models.lora_manager import LoraManager

lora = LoraManager(r=32, lora_alpha=64)
model = lora.appliquer_lora(model)
```

#### 5. **ModelTrainer** (`training/trainer.py`)
Gère l'entraînement complet.

```python
from training.trainer import ModelTrainer

trainer = ModelTrainer(model, tokenizer, train_ds, val_ds, config)
trainer.creer_trainer(sft_config)
trainer.entrainer()
```

#### 6. **Predictor** (`inference/predictor.py`)
Effectue des prédictions.

```python
from inference.predictor import Predictor

predictor = Predictor(model, tokenizer)
analyse, cause, justif = predictor.predire(commentaire)
```

#### 7. **Evaluator** (`inference/evaluator.py`)
Évalue les performances et génère des rapports.

```python
from inference.evaluator import Evaluator

evaluator = Evaluator(predictor)
df_resultats = evaluator.evaluer_fichier_test(test_path)
metriques = evaluator.evaluer_avec_validation(df_resultats, valid_path)
```

## 🎯 Catégories Prédites

Le modèle classifie les incidents en 15 catégories :
- MPR issue
- BSS Hardware issue
- AKTIVCO Defaut GE & Power Cabinet
- AKTIVCO Coupure ENEO & Baisse de tension
- Coupure ENEO & Baisse de tension
- Defaut GE & Power Cabinet
- Sharing
- SPARE-ISSUE
- Fiber AOF
- Projet OCM (HUAWEI)
- ACCESS-ISSUE
- Projet OCM (ZTE, NOKIA, autres projets)
- ODU HS
- IP & VLAN
- Warehouse HUAWEI

## 📝 Format des Données

### Données d'Entraînement (JSONL)

```json
{
  "messages": [
    {"role": "system", "content": "Tu es un expert..."},
    {"role": "user", "content": "Commentaire : ..."},
    {"role": "assistant", "content": "Cause : MPR issue"}
  ]
}
```

### Fichier de Test (Excel)

| Codesite | Verifications | Owner | Topology | Vendors |
|----------|---------------|-------|----------|---------|
| LIT_123  | Commentaire... | MTN   | IHS      | HUAWEI  |

### Fichier de Validation (Excel)

| Codesite | Verifications | CAUSE | Owner | Topology | Vendors |
|----------|---------------|-------|-------|----------|---------|
| LIT_123  | Commentaire... | MPR issue | MTN | IHS | HUAWEI |

## 🔍 Fonctionnalités Avancées

### Détection de Sites Impactés
Le système détecte automatiquement les sites impactés par d'autres sites et hérite de leur cause.

### Gestion des Cas Spéciaux
- **NO_ROOT_CAUSE** : Pas de commentaire disponible
- **SITE_IMPACTANT_NON_RESOLU** : Site impactant non trouvé
- **ERREUR** : Erreur lors de la prédiction

### Rapports d'Évaluation
Génère des rapports Excel détaillés avec :
- Résumé global (accuracy, métriques)
- Performance par catégorie
- Détails ligne par ligne
- Analyse des confusions

## ⚙️ Configuration

### LoRA (`config/lora_config.yaml`)

```yaml
r: 32                      # Rang LoRA
lora_alpha: 64            # Alpha LoRA
lora_dropout: 0.05        # Dropout
target_modules:           # Modules ciblés
  - q_proj
  - v_proj
  - k_proj
  # ... etc
```

### Entraînement (`config/train_config.yaml`)

```yaml
num_train_epochs: 5
per_device_train_batch_size: 1
gradient_accumulation_steps: 8
learning_rate: 1e-4
max_seq_length: 768
# ... etc
```

## 🛠️ Développement

### Ajouter une Nouvelle Fonctionnalité

1. Créer une nouvelle classe dans le module approprié
2. Implémenter les méthodes nécessaires
3. Ajouter les imports dans `__init__.py`
4. Mettre à jour `main.py` si besoin

### Tests

```python
# Exemple de test simple
from data.loader import DataLoader

loader = DataLoader()
train_data = loader.charger_jsonl("chemin/vers/train.jsonl")
print(f"Chargé {len(train_data)} exemples")
```

## 📦 Exemple d'Utilisation Complète

```python
from follow_up_ai.main import FineTuningPipeline

# Créer le pipeline
pipeline = FineTuningPipeline()

# Entraîner
pipeline.entrainer()

# Merger
pipeline.merger()

# Évaluer
pipeline.evaluer(use_merged=True)

# Ou utiliser le pipeline complet en une commande
# python main.py full
```

## 📄 Licence

Ce projet est destiné à un usage interne.

## 👥 Contact

Pour toute question, contacter l'équipe de développement.
