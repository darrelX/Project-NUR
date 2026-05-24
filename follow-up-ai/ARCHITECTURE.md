# 🏗️ Architecture du Projet

Ce document décrit l'architecture détaillée du projet de fine-tuning.

## 📐 Vue d'Ensemble

Le projet suit une architecture modulaire en couches :

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│              (Orchestration Pipeline)               │
└─────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Training    │ │  Inference    │ │    Models     │
│               │ │               │ │               │
│ - Trainer     │ │ - Predictor   │ │ - ModelLoader │
│               │ │ - Evaluator   │ │ - LoraManager │
└───────────────┘ └───────────────┘ └───────────────┘
        ↓               ↓               ↓
┌─────────────────────────────────────────────────────┐
│                     Data Layer                       │
│  - DataLoader  - Preprocessor  - TokenizerManager   │
└─────────────────────────────────────────────────────┘
        ↓               ↓               ↓
┌─────────────────────────────────────────────────────┐
│                  Utils & Config                      │
│    - Constants  - Helpers  - ConfigManager          │
└─────────────────────────────────────────────────────┘
```

## 🎯 Principes de Design

### 1. Séparation des Responsabilités

Chaque module a une responsabilité unique et bien définie :
- **config/** : Configuration uniquement
- **data/** : Chargement et prétraitement de données
- **models/** : Gestion des modèles
- **training/** : Entraînement
- **inference/** : Prédiction et évaluation
- **utils/** : Utilitaires partagés

### 2. Injection de Dépendances

Les classes reçoivent leurs dépendances en paramètres :

```python
# Mauvais
class Trainer:
    def __init__(self):
        self.model = load_model()  # Dépendance cachée

# Bon
class ModelTrainer:
    def __init__(self, model, tokenizer, ...):
        self.model = model  # Dépendance explicite
```

### 3. Configuration Externe

Toute la configuration est dans des fichiers YAML :
- `paths.yaml` : Chemins des fichiers
- `lora_config.yaml` : Paramètres LoRA
- `train_config.yaml` : Paramètres d'entraînement

### 4. Interfaces Claires

Chaque classe expose des méthodes publiques documentées avec des types.

## 📦 Modules Détaillés

### 1. config/

#### ConfigManager
Gestionnaire centralisé de configuration.

**Responsabilités** :
- Charger les fichiers YAML
- Fournir des getters typés pour les valeurs
- Gérer les chemins absolus/relatifs

**Méthodes principales** :
```python
get_path(key: str) -> str
get_lora_config() -> Dict[str, Any]
get_train_config() -> Dict[str, Any]
get_lora_r() -> int
# ... etc
```

**Utilisation** :
```python
config = ConfigManager()
train_path = config.get_path("train_jsonl")
lora_r = config.get_lora_r()
```

---

### 2. data/

#### DataLoader
Charge les données JSONL et analyse leur distribution.

**Responsabilités** :
- Lire les fichiers JSONL
- Analyser la distribution des causes
- Fournir les données d'entraînement/validation

**Méthodes principales** :
```python
charger_jsonl(chemin: str) -> List[Dict[str, Any]]
charger_train_val(train_path: str, val_path: str)
analyser_distribution()
get_train_data() -> List[Dict[str, Any]]
```

#### DataPreprocessor
Prépare les données pour l'entraînement.

**Responsabilités** :
- Formater les exemples avec le chat template
- Tokeniser les données
- Créer les datasets HuggingFace

**Méthodes principales** :
```python
formater_exemple(exemple: Dict) -> Dict[str, str]
tokeniser_exemple(exemple: Dict, max_length: int) -> Dict[str, Any]
preparer_datasets(train_data, val_data, max_seq_length) -> tuple
calculer_steps(...) -> Dict[str, int]
```

#### TokenizerManager
Gère le chargement et la configuration du tokenizer.

**Responsabilités** :
- Charger le tokenizer depuis HuggingFace
- Configurer les tokens spéciaux (pad, eos)
- Sauvegarder/charger depuis checkpoint

**Méthodes principales** :
```python
charger_tokenizer() -> AutoTokenizer
sauvegarder_tokenizer(chemin: str)
charger_tokenizer_depuis_checkpoint(chemin: str) -> AutoTokenizer
```

---

### 3. models/

#### ModelLoader
Charge et gère les modèles.

**Responsabilités** :
- Charger le modèle de base (avec/sans quantization)
- Charger un modèle mergé
- Charger un modèle avec adaptateurs LoRA
- Sauvegarder les modèles

**Méthodes principales** :
```python
creer_quant_config(load_in_4bit: bool) -> BitsAndBytesConfig
charger_modele_base(use_quantization: bool) -> AutoModelForCausalLM
charger_modele_merged(chemin: str) -> AutoModelForCausalLM
charger_modele_avec_lora(chemin_lora: str) -> PeftModel
sauvegarder_modele(chemin: str)
```

#### LoraManager
Gère LoRA : configuration, application, merge.

**Responsabilités** :
- Créer la configuration LoRA
- Appliquer LoRA à un modèle
- Merger LoRA avec le modèle de base
- Sauvegarder les adaptateurs

**Méthodes principales** :
```python
creer_config() -> LoraConfig
appliquer_lora(model) -> PeftModel
merger_lora(model_base, chemin_lora, chemin_sortie) -> Any
sauvegarder_adaptateurs(chemin: str)
```

---

### 4. training/

#### ModelTrainer
Gère l'entraînement du modèle.

**Responsabilités** :
- Créer la configuration SFT
- Créer le trainer
- Lancer l'entraînement
- Sauvegarder le modèle et le tokenizer

**Méthodes principales** :
```python
creer_sft_config(output_dir: str, warmup_steps: int) -> SFTConfig
creer_trainer(sft_config: SFTConfig)
entrainer()
sauvegarder_tout(chemin: str)
```

---

### 5. inference/

#### Predictor
Effectue des prédictions avec le modèle.

**Responsabilités** :
- Construire les prompts
- Générer les prédictions
- Extraire et normaliser les causes
- Gérer les prédictions batch

**Méthodes principales** :
```python
predire(commentaire: str, owner: str, ...) -> Tuple[str, str, str]
predire_batch(commentaires: list, ...) -> list
predire_avec_contexte(commentaire: str, contexte: dict) -> Tuple[str, str, str]
evaluer_confiance(justification: str) -> str
```

**Retour de `predire`** :
```python
(analyse, cause_normalisee, justification)
# analyse: Résumé du commentaire
# cause_normalisee: Cause officielle
# justification: Réponse brute du modèle
```

#### Evaluator
Évalue les performances du modèle.

**Responsabilités** :
- Classifier les lignes (normal, impacté, no_root_cause)
- Traiter les cas normaux et impactés
- Comparer avec validation
- Générer des rapports Excel détaillés

**Méthodes principales** :
```python
evaluer_fichier_test(chemin_test: str, ...) -> pd.DataFrame
evaluer_avec_validation(df_test, chemin_valid) -> Dict[str, Any]
generer_rapport_excel(df_eval, erreurs_par_cat, chemin_sortie, metriques)
```

---

### 6. utils/

#### constants.py
Définit toutes les constantes globales :
- `CATEGORIES` : Les 15 catégories officielles
- `SYSTEM_PROMPT` : Le prompt système
- `GENERATION_CONFIG` : Paramètres de génération
- `PATTERN_IMPACT` : Regex pour détecter les sites impactés
- `PATTERN_CODE_SITE` : Regex pour extraire les codes sites

#### helpers.py
Fonctions utilitaires réutilisables :
- `propre()` : Nettoyer une valeur
- `est_impacte()` : Détecter un site impacté
- `extraire_site_impactant()` : Extraire le code site impactant
- `normaliser_cause()` : Normaliser vers une catégorie officielle
- `nettoyer_memoire()` : Libérer la VRAM
- `afficher_info_gpu()` : Afficher les infos GPU
- `construire_prompt_utilisateur()` : Construire un prompt

---

## 🔄 Flux de Données

### Phase 1 : Entraînement

```
1. ConfigManager charge les configurations
          ↓
2. DataLoader charge les JSONL
          ↓
3. TokenizerManager charge le tokenizer
          ↓
4. DataPreprocessor formate et tokenise
          ↓
5. ModelLoader charge le modèle de base
          ↓
6. LoraManager applique LoRA
          ↓
7. ModelTrainer entraîne
          ↓
8. Sauvegarde des adaptateurs LoRA
```

### Phase 2 : Merge

```
1. ModelLoader charge le modèle de base
          ↓
2. LoraManager charge les adaptateurs
          ↓
3. LoraManager merge
          ↓
4. Sauvegarde du modèle mergé
```

### Phase 3 : Évaluation

```
1. ModelLoader charge le modèle mergé
          ↓
2. TokenizerManager charge le tokenizer
          ↓
3. Predictor créé avec modèle + tokenizer
          ↓
4. Evaluator charge le fichier de test
          ↓
5. Classification des lignes
          ↓
6. Prédiction sur cas normaux
          ↓
7. Résolution des cas impactés
          ↓
8. Comparaison avec validation
          ↓
9. Génération du rapport Excel
```

## 🔌 Points d'Extension

### Ajouter une Nouvelle Source de Données

1. Créer une nouvelle classe dans `data/`
2. Implémenter l'interface :
   ```python
   class CustomLoader:
       def charger(self, chemin: str) -> List[Dict]:
           pass
   ```
3. Utiliser dans le pipeline

### Ajouter une Nouvelle Métrique

1. Ajouter la méthode dans `Evaluator`
2. Mettre à jour `generer_rapport_excel()`

### Ajouter un Nouveau Modèle

1. Mettre à jour `MODEL_NAME` dans `constants.py`
2. Ajuster les `target_modules` LoRA si nécessaire

## 🧪 Tests

Structure de test recommandée :

```
tests/
├── test_config.py
├── test_data.py
├── test_models.py
├── test_training.py
└── test_inference.py
```

Exemple de test :

```python
def test_data_loader():
    loader = DataLoader()
    data = loader.charger_jsonl("test_data.jsonl")
    assert len(data) > 0
    assert "messages" in data[0]
```

## 📊 Métriques de Performance

Le système mesure :
- **Accuracy globale** : % de prédictions correctes
- **Accuracy par catégorie** : Performance par cause
- **Temps de prédiction** : ms par prédiction
- **Cas résolus/non résolus** : Pour les sites impactés
- **Confusions principales** : Erreurs les plus fréquentes

## 🔒 Gestion des Erreurs

Stratégie de gestion des erreurs :

1. **Chargement de fichiers** : Try/except avec message clair
2. **Prédictions** : Capture d'erreurs + retour "ERREUR"
3. **GPU OOM** : Suggestions de réduction de batch/séquence
4. **Validation** : Assertions pour vérifier les données

## 💡 Bonnes Pratiques

### Pour le Code

1. **Type hints** partout
2. **Docstrings** pour toutes les fonctions publiques
3. **Noms explicites** pour les variables
4. **Pas de magic numbers** (utiliser des constantes)

### Pour les Classes

1. **Une responsabilité par classe**
2. **Injection de dépendances**
3. **Méthodes courtes** (<50 lignes)
4. **État minimal** (peu d'attributs mutables)

### Pour les Modules

1. **Imports explicites** dans `__init__.py`
2. **Pas de dépendances circulaires**
3. **Organisation logique** des fichiers

---

**Date de dernière mise à jour** : Mai 2026
**Version** : 1.0
