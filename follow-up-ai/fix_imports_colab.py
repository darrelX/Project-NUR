#!/usr/bin/env python3
"""
Script pour corriger automatiquement tous les imports relatifs en imports absolus
À exécuter sur Colab : python fix_imports_colab.py
"""

import os
import re

def fix_file(filepath, replacements):
    """Applique les corrections à un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigé: {filepath}")
            return True
        else:
            print(f"⏭️  Déjà OK: {filepath}")
            return False
    except Exception as e:
        print(f"❌ Erreur sur {filepath}: {e}")
        return False

print("="*70)
print("🔧 CORRECTION AUTOMATIQUE DES IMPORTS")
print("="*70)

# Obtenir le chemin du projet
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"\n📂 Répertoire du projet: {project_root}\n")

corrections = []

# 1. config/__init__.py
print("[1/6] Correction de config/__init__.py")
corrections.append(fix_file(
    os.path.join(project_root, "config", "__init__.py"),
    [("from .config_manager import ConfigManager", "from config.config_manager import ConfigManager")]
))

# 2. data/__init__.py
print("[2/6] Correction de data/__init__.py")
corrections.append(fix_file(
    os.path.join(project_root, "data", "__init__.py"),
    [
        ("from .loader import DataLoader", "from data.loader import DataLoader"),
        ("from .preprocessing import DataPreprocessor", "from data.preprocessing import DataPreprocessor"),
        ("from .tokenization import TokenizerManager", "from data.tokenization import TokenizerManager"),
    ]
))

# 3. models/__init__.py
print("[3/6] Correction de models/__init__.py")
corrections.append(fix_file(
    os.path.join(project_root, "models", "__init__.py"),
    [
        ("from .model_loader import ModelLoader", "from models.model_loader import ModelLoader"),
        ("from .lora_manager import LoraManager", "from models.lora_manager import LoraManager"),
    ]
))

# 4. training/__init__.py
print("[4/6] Correction de training/__init__.py")
corrections.append(fix_file(
    os.path.join(project_root, "training", "__init__.py"),
    [("from .trainer import ModelTrainer", "from training.trainer import ModelTrainer")]
))

# 5. inference/__init__.py
print("[5/6] Correction de inference/__init__.py")
corrections.append(fix_file(
    os.path.join(project_root, "inference", "__init__.py"),
    [
        ("from .predictor import Predictor", "from inference.predictor import Predictor"),
        ("from .evaluator import Evaluator", "from inference.evaluator import Evaluator"),
    ]
))

# 6. utils/__init__.py
print("[6/6] Correction de utils/__init__.py")
corrections.append(fix_file(
    os.path.join(project_root, "utils", "__init__.py"),
    [
        ("from .constants import", "from utils.constants import"),
        ("from .helpers import", "from utils.helpers import"),
    ]
))

print("\n" + "="*70)
total_fixed = sum(corrections)
print(f"✅ {total_fixed} fichier(s) corrigé(s)")
print("="*70)

# Vérifier qu'il n'y a plus d'imports relatifs dans les __init__.py
print("\n🔍 Vérification finale...")
has_relative = False

for root, dirs, files in os.walk(project_root):
    for file in files:
        if file == "__init__.py":
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chercher les imports relatifs (from . ou from ..)
            relative_imports = re.findall(r'from \.\.?\w+', content)
            if relative_imports:
                has_relative = True
                print(f"⚠️  Imports relatifs restants dans {filepath}:")
                for imp in relative_imports:
                    print(f"    - {imp}")

if not has_relative:
    print("✅ Aucun import relatif trouvé dans les __init__.py !")
    print("\n🎉 Correction terminée ! Vous pouvez maintenant exécuter:")
    print("    python test_imports.py")
    print("    python main.py --help")
else:
    print("\n⚠️  Certains imports relatifs n'ont pas été corrigés.")
    print("    Veuillez les corriger manuellement.")

print("="*70)
