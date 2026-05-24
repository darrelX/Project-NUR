# ⚡ Guide de Démarrage Rapide

Guide pour utiliser le projet de fine-tuning en 5 minutes.

## 📋 Prérequis

- Python 3.8+
- GPU avec CUDA (recommandé pour l'entraînement)
- ~10 GB VRAM pour l'entraînement avec quantization 4-bit
- Données d'entraînement au format JSONL
- Fichiers de test/validation au format Excel

## 🚀 Installation Rapide

### 1. Installer les dépendances

```bash
cd follow-up-ai
pip install -r requirements.txt
```

### 2. Configurer les chemins

Éditer `config/paths.yaml` :

```yaml
base_drive: "/votre/chemin/vers/donnees"
train_jsonl: "dataset/train1.jsonl"
val_jsonl: "dataset/validation1.jsonl"
test_daily: "test-daily.xlsx"
valid_daily: "valid-daily.xlsx"
lora_folder: "finetuned_lora"
merged_folder: "model_final"
result_test: "resultats_test.xlsx"
eval_report: "evaluation.xlsx"
```

## 🎯 Utilisation

### Option 1 : Pipeline Complet (Recommandé)

Entraîne, merge et évalue en une seule commande :

```bash
python main.py full
```

**Durée estimée** : 
- Entraînement : 2-4 heures (dépend du dataset)
- Merge : 5-10 minutes
- Évaluation : 10-30 minutes (dépend du fichier de test)

### Option 2 : Étape par Étape

#### Étape 1 : Entraînement

```bash
python main.py train
```

Cela va :
- ✅ Charger les données JSONL
- ✅ Charger le modèle Qwen2.5-3B-Instruct
- ✅ Appliquer LoRA
- ✅ Entraîner le modèle
- ✅ Sauvegarder les adaptateurs LoRA

**Sortie** : `finetuned_lora/` (adaptateurs LoRA)

#### Étape 2 : Merge

```bash
python main.py merge
```

Fusionne les adaptateurs LoRA avec le modèle de base.

**Sortie** : `model_final/` (modèle complet)

#### Étape 3 : Évaluation

```bash
python main.py evaluate --use-merged
```

Évalue le modèle sur vos données de test.

**Sortie** : 
- `resultats_test.xlsx` (prédictions détaillées)
- `evaluation.xlsx` (rapport de performance)

### Option 3 : Prédiction Simple

Pour tester rapidement le modèle :

```bash
python main.py predict --commentaire "Site down suite à coupure ENEO"
```

## 📊 Résultats Attendus

Après l'évaluation, vous obtiendrez :

### 1. Fichier de résultats (`resultats_test.xlsx`)

| Codesite | ANALYSE | CAUSE_PREDITE | JUSTIFICATION | TYPE_CAS | TEMPS_S |
|----------|---------|---------------|---------------|----------|---------|
| LIT_123 | Site down... | Coupure ENEO | Cause: ... | NORMAL | 0.5 |

### 2. Rapport d'évaluation (`evaluation.xlsx`)

**Feuille "Résumé global"** :
- Total évalué : 1500
- Accuracy : 85.2%
- Catégories ≥80% : 10/15

**Feuille "Par catégorie"** :
- Détail par cause
- Accuracy par catégorie
- Erreurs principales

## 🔧 Configuration Avancée

### Modifier les hyperparamètres LoRA

Éditer `config/lora_config.yaml` :

```yaml
r: 32                     # Plus grand = plus de capacité
lora_alpha: 64
lora_dropout: 0.05
```

### Modifier les paramètres d'entraînement

Éditer `config/train_config.yaml` :

```yaml
num_train_epochs: 5       # Nombre d'epochs
learning_rate: 1e-4       # Taux d'apprentissage
max_seq_length: 768       # Longueur max de séquence
```

## 🐛 Résolution de Problèmes

### Erreur : "CUDA out of memory"

**Solution** : Réduire la taille de batch ou la longueur de séquence :

```yaml
# Dans train_config.yaml
per_device_train_batch_size: 1
gradient_accumulation_steps: 16  # Augmenter
max_seq_length: 512              # Réduire
```

### Erreur : "File not found"

**Solution** : Vérifier les chemins dans `config/paths.yaml`

### Modèle fait des prédictions incorrectes

**Solutions** :
1. Augmenter le nombre d'epochs
2. Vérifier la qualité des données d'entraînement
3. Augmenter le rang LoRA (r)

## 📚 Exemples Supplémentaires

### Utilisation Programmatique

```python
from main import FineTuningPipeline

# Créer le pipeline
pipeline = FineTuningPipeline()

# Entraîner
pipeline.entrainer()

# Évaluer
pipeline.evaluer(use_merged=True)
```

### Exemples de Code

Voir `exemple.py` pour des exemples détaillés :

```bash
# Configuration
python exemple.py config

# Chargement de données
python exemple.py data

# Prédiction
python exemple.py predict

# Tous les exemples
python exemple.py all
```

## ⏱️ Durées Estimées

| Opération | Temps (GPU T4) | Temps (CPU) |
|-----------|----------------|-------------|
| Entraînement (5 epochs, 1000 exemples) | 1-2h | 10-15h |
| Merge | 5 min | 5 min |
| Évaluation (2000 lignes) | 15 min | 1h |
| Prédiction simple | <1s | 2-3s |

## 📞 Support

En cas de problème :

1. Vérifier la configuration des chemins
2. Consulter la documentation complète (`README.md`)
3. Vérifier les logs pour les erreurs
4. Contacter l'équipe de développement

## ✅ Checklist de Démarrage

- [ ] Python et pip installés
- [ ] GPU CUDA disponible (optionnel mais recommandé)
- [ ] Dépendances installées
- [ ] Chemins configurés dans `config/paths.yaml`
- [ ] Données d'entraînement disponibles (JSONL)
- [ ] Données de test disponibles (Excel)
- [ ] Commande `python main.py full` exécutée

**Durée totale** : ~3-5 heures pour le pipeline complet

---

**Prochaines étapes** : Une fois le modèle entraîné, vous pouvez l'utiliser pour :
- Analyser de nouveaux incidents
- Évaluer sur d'autres datasets
- Ajuster les hyperparamètres pour améliorer les performances
