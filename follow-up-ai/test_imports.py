#!/usr/bin/env python3
"""
Script de test pour vérifier tous les imports du projet
"""

import sys
import os

# Ajouter le dossier parent au path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

print("="*70)
print("🧪 TEST DES IMPORTS DU PROJET FOLLOW-UP-AI")
print("="*70)

print(f"\n📂 Répertoire de travail : {os.getcwd()}")
print(f"📂 Dossier du script : {script_dir}")
print(f"📂 sys.path[0] : {sys.path[0]}\n")

# Test des imports un par un
tests = [
    ("utils.constants", ["CATEGORIES", "MODEL_NAME"]),
    ("utils.helpers", ["propre", "nettoyer_memoire"]),
    ("config.config_manager", ["ConfigManager"]),
    ("data.loader", ["DataLoader"]),
    ("data.tokenization", ["TokenizerManager"]),
    ("data.preprocessing", ["DataPreprocessor"]),
    ("models.model_loader", ["ModelLoader"]),
    ("models.lora_manager", ["LoraManager"]),
    ("training.trainer", ["ModelTrainer"]),
    ("inference.predictor", ["Predictor"]),
    ("inference.evaluator", ["Evaluator"]),
]

print("🔍 Test des imports individuels :\n")

erreurs = []
for i, (module_name, items) in enumerate(tests, 1):
    try:
        print(f"[{i:2d}/{len(tests)}] Import de {module_name:30s} ... ", end="")
        module = __import__(module_name, fromlist=items)
        
        # Vérifier que les items existent
        for item in items:
            if not hasattr(module, item):
                raise ImportError(f"{item} n'existe pas dans {module_name}")
        
        print(f"✅ OK")
    except Exception as e:
        print(f"❌ ERREUR")
        erreurs.append((module_name, str(e)))
        print(f"    └─ {e}")

print("\n" + "="*70)

if erreurs:
    print(f"❌ {len(erreurs)} ERREUR(S) DÉTECTÉE(S) :")
    for module, erreur in erreurs:
        print(f"   - {module}: {erreur}")
    sys.exit(1)
else:
    print("✅ TOUS LES IMPORTS FONCTIONNENT CORRECTEMENT !")
    print("\n🎉 Le projet est prêt à être utilisé !")
    print("\nCommandes disponibles :")
    print("   python main.py full          # Pipeline complet")
    print("   python main.py train         # Entraînement uniquement")
    print("   python main.py merge         # Fusion LoRA")
    print("   python main.py evaluate      # Évaluation")
    print("   python main.py predict       # Prédiction unique")
    print("="*70)
    sys.exit(0)
