"""
Exemple d'utilisation programmatique du pipeline
"""

import sys
import os

# Ajouter le chemin du module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from data.loader import DataLoader
from data.tokenization import TokenizerManager
from models.model_loader import ModelLoader
from inference.predictor import Predictor
from utils.constants import MODEL_NAME


def exemple_prediction_simple():
    """
    Exemple : Faire une prédiction simple avec le modèle fine-tuné
    """
    print("\n" + "="*60)
    print("EXEMPLE : PRÉDICTION SIMPLE")
    print("="*60)
    
    # 1. Charger la configuration
    config = ConfigManager()
    
    # 2. Charger le modèle mergé
    print("\n[1/3] Chargement du modèle...")
    model_loader = ModelLoader(MODEL_NAME)
    merged_path = config.get_path("merged_folder")
    model = model_loader.charger_modele_merged(merged_path)
    
    # 3. Charger le tokenizer
    print("\n[2/3] Chargement du tokenizer...")
    tokenizer_mgr = TokenizerManager(MODEL_NAME)
    tokenizer = tokenizer_mgr.charger_tokenizer_depuis_checkpoint(merged_path)
    
    # 4. Créer le prédicteur
    print("\n[3/3] Création du prédicteur...")
    predictor = Predictor(model, tokenizer)
    
    # 5. Faire une prédiction
    print("\n" + "="*60)
    print("PRÉDICTION")
    print("="*60)
    
    commentaire = """
    Site indisponible depuis ce matin. Après vérification sur site, 
    le groupe électrogène ne démarre pas. Technicien sur place pour réparation.
    """
    
    analyse, cause, justification = predictor.predire(
        commentaire=commentaire.strip(),
        owner="MTN",
        topology="IHS"
    )
    
    print(f"\nCommentaire : {commentaire.strip()[:100]}...")
    print(f"\nCause prédite  : {cause}")
    print(f"Justification  : {justification}")
    print(f"Analyse        : {analyse[:150]}...")


def exemple_chargement_donnees():
    """
    Exemple : Charger et analyser les données d'entraînement
    """
    print("\n" + "="*60)
    print("EXEMPLE : CHARGEMENT DES DONNÉES")
    print("="*60)
    
    # 1. Charger la configuration
    config = ConfigManager()
    
    # 2. Créer le loader
    loader = DataLoader()
    
    # 3. Charger les données
    train_path = config.get_path("train_jsonl")
    val_path = config.get_path("val_jsonl")
    
    loader.charger_train_val(train_path, val_path)
    
    # 4. Accéder aux données
    train_data = loader.get_train_data()
    val_data = loader.get_val_data()
    
    print(f"\n✅ Données chargées :")
    print(f"   Train : {len(train_data)} exemples")
    print(f"   Val   : {len(val_data)} exemples")
    
    # Afficher un exemple
    if train_data:
        print(f"\n📄 Exemple d'entrée :")
        print(f"   Messages : {len(train_data[0].get('messages', []))} messages")
        for i, msg in enumerate(train_data[0].get('messages', [])[:3]):
            print(f"   Message {i+1} ({msg.get('role', 'N/A')}) : {msg.get('content', '')[:50]}...")


def exemple_configuration():
    """
    Exemple : Utiliser le gestionnaire de configuration
    """
    print("\n" + "="*60)
    print("EXEMPLE : GESTIONNAIRE DE CONFIGURATION")
    print("="*60)
    
    # Créer le gestionnaire
    config = ConfigManager()
    
    # Accéder aux chemins
    print("\n📁 Chemins configurés :")
    print(f"   Train JSONL  : {config.get_path('train_jsonl')}")
    print(f"   Val JSONL    : {config.get_path('val_jsonl')}")
    print(f"   LoRA folder  : {config.get_path('lora_folder')}")
    print(f"   Merged folder: {config.get_path('merged_folder')}")
    
    # Accéder aux paramètres LoRA
    print("\n⚙️  Configuration LoRA :")
    print(f"   r            : {config.get_lora_r()}")
    print(f"   alpha        : {config.get_lora_alpha()}")
    print(f"   dropout      : {config.get_lora_dropout()}")
    print(f"   target modules: {len(config.get_lora_target_modules())} modules")
    
    # Accéder aux paramètres d'entraînement
    print("\n🎯 Configuration entraînement :")
    print(f"   Epochs       : {config.get_num_epochs()}")
    print(f"   Batch size   : {config.get_batch_size()}")
    print(f"   Learning rate: {config.get_learning_rate()}")
    print(f"   Max seq len  : {config.get_max_seq_length()}")


def exemple_batch_predictions():
    """
    Exemple : Faire des prédictions sur un batch de commentaires
    """
    print("\n" + "="*60)
    print("EXEMPLE : PRÉDICTIONS EN BATCH")
    print("="*60)
    
    # 1. Charger la configuration
    config = ConfigManager()
    
    # 2. Charger le modèle
    print("\n[1/2] Chargement du modèle...")
    model_loader = ModelLoader(MODEL_NAME)
    merged_path = config.get_path("merged_folder")
    model = model_loader.charger_modele_merged(merged_path)
    
    tokenizer_mgr = TokenizerManager(MODEL_NAME)
    tokenizer = tokenizer_mgr.charger_tokenizer_depuis_checkpoint(merged_path)
    
    # 3. Créer le prédicteur
    print("\n[2/2] Prédictions en batch...")
    predictor = Predictor(model, tokenizer)
    
    # 4. Prédictions batch
    commentaires = [
        "Site down, pas de courant ENEO",
        "ODU HS suite à problème de liaison radio",
        "Fiber coupée par des travaux",
    ]
    
    resultats = predictor.predire_batch(commentaires)
    
    # 5. Afficher les résultats
    print("\n📊 RÉSULTATS :")
    for i, (com, (analyse, cause, justif)) in enumerate(zip(commentaires, resultats), 1):
        print(f"\n   [{i}] Commentaire : {com}")
        print(f"       Cause       : {cause}")
        print(f"       Confiance   : {predictor.evaluer_confiance(justif)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Exemples d'utilisation")
    parser.add_argument(
        "exemple",
        choices=["config", "data", "predict", "batch", "all"],
        help="Exemple à exécuter"
    )
    
    args = parser.parse_args()
    
    if args.exemple == "config":
        exemple_configuration()
    
    elif args.exemple == "data":
        exemple_chargement_donnees()
    
    elif args.exemple == "predict":
        exemple_prediction_simple()
    
    elif args.exemple == "batch":
        exemple_batch_predictions()
    
    elif args.exemple == "all":
        exemple_configuration()
        exemple_chargement_donnees()
        # Note: predict et batch nécessitent un modèle entraîné
        print("\n⚠️  Les exemples de prédiction nécessitent un modèle entraîné")
        print("   Exécutez d'abord : python main.py full")
    
    print("\n" + "="*60)
    print("✅ EXEMPLE TERMINÉ")
    print("="*60)
