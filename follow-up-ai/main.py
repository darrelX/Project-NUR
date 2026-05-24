"""
Pipeline principal de fine-tuning et évaluation
"""

import argparse
import sys
import os

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from data.loader import DataLoader
from data.tokenization import TokenizerManager
from data.preprocessing import DataPreprocessor
from models.model_loader import ModelLoader
from models.lora_manager import LoraManager
from training.trainer import ModelTrainer
from inference.predictor import Predictor
from inference.evaluator import Evaluator
from utils.constants import MODEL_NAME
from utils.helpers import afficher_info_gpu, nettoyer_memoire


class FineTuningPipeline:
    """
    Pipeline complet de fine-tuning et évaluation
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialise le pipeline
        
        Args:
            config_dir: Chemin vers le dossier de configuration
        """
        print("\n" + "="*60)
        print("🚀 INITIALISATION DU PIPELINE")
        print("="*60)
        
        self.config = ConfigManager(config_dir)
        print("✅ Configuration chargée")
        
    def entrainer(self):
        """
        Lance l'entraînement complet du modèle
        """
        print("\n" + "="*60)
        print("📚 PHASE 1 : ENTRAÎNEMENT")
        print("="*60)
        
        # 1. Charger les données
        print("\n[1/7] Chargement des données")
        data_loader = DataLoader()
        train_path = self.config.get_path("train_jsonl")
        val_path = self.config.get_path("val_jsonl")
        data_loader.charger_train_val(train_path, val_path)
        
        # 2. Charger le tokenizer
        print("\n[2/7] Chargement du tokenizer")
        tokenizer_mgr = TokenizerManager(MODEL_NAME)
        tokenizer = tokenizer_mgr.charger_tokenizer()
        
        # 3. Prétraiter les données
        print("\n[3/7] Prétraitement des données")
        preprocessor = DataPreprocessor(tokenizer)
        train_tok, val_tok = preprocessor.preparer_datasets(
            data_loader.get_train_data(),
            data_loader.get_val_data(),
            self.config.get_max_seq_length()
        )
        
        # Calculer les steps
        steps_info = preprocessor.calculer_steps(
            len(train_tok),
            self.config.get_batch_size(),
            self.config.get_gradient_accumulation_steps(),
            self.config.get_num_epochs(),
            self.config.get_warmup_ratio()
        )
        
        # 4. Charger le modèle
        print("\n[4/7] Chargement du modèle")
        afficher_info_gpu()
        model_loader = ModelLoader(MODEL_NAME)
        model = model_loader.charger_modele_base(use_quantization=True)
        
        # 5. Appliquer LoRA
        print("\n[5/7] Application de LoRA")
        lora_mgr = LoraManager(
            r=self.config.get_lora_r(),
            lora_alpha=self.config.get_lora_alpha(),
            lora_dropout=self.config.get_lora_dropout(),
            target_modules=self.config.get_lora_target_modules()
        )
        model = lora_mgr.appliquer_lora(model)
        
        # 6. Créer le trainer
        print("\n[6/7] Configuration du trainer")
        train_config = self.config.get_train_config()
        trainer = ModelTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=train_tok,
            eval_dataset=val_tok,
            config=train_config
        )
        
        lora_output = self.config.get_path("lora_folder")
        sft_config = trainer.creer_sft_config(
            lora_output, 
            steps_info["warmup_steps"]
        )
        trainer.creer_trainer(sft_config)
        
        # 7. Entraîner
        print("\n[7/7] Entraînement")
        trainer.entrainer()
        
        # Sauvegarder
        trainer.sauvegarder_tout(lora_output)
        
        print("\n✅ ENTRAÎNEMENT TERMINÉ")
        
        return lora_output
    
    def merger(self):
        """
        Merge les adaptateurs LoRA avec le modèle de base
        """
        print("\n" + "="*60)
        print("🔗 PHASE 2 : MERGE LoRA + MODÈLE DE BASE")
        print("="*60)
        
        nettoyer_memoire()
        
        # Charger le modèle de base
        print("\n[1/3] Chargement du modèle de base")
        model_loader = ModelLoader(MODEL_NAME)
        model_base = model_loader.charger_modele_base(use_quantization=False)
        
        # Merger
        print("\n[2/3] Merge en cours")
        lora_mgr = LoraManager()
        lora_path = self.config.get_path("lora_folder")
        merged_path = self.config.get_path("merged_folder")
        
        lora_mgr.merger_lora(model_base, lora_path, merged_path)
        
        # Sauvegarder le tokenizer
        print("\n[3/3] Sauvegarde du tokenizer")
        tokenizer_mgr = TokenizerManager(MODEL_NAME)
        tokenizer_mgr.charger_tokenizer_depuis_checkpoint(lora_path)
        tokenizer_mgr.sauvegarder_tokenizer(merged_path)
        
        print("\n✅ MERGE TERMINÉ")
        
        return merged_path
    
    def evaluer(self, use_merged: bool = True):
        """
        Évalue le modèle sur les données de test
        
        Args:
            use_merged: Si True, utilise le modèle mergé, sinon base+LoRA
        """
        print("\n" + "="*60)
        print("📊 PHASE 3 : ÉVALUATION")
        print("="*60)
        
        nettoyer_memoire()
        
        # Charger le modèle
        print("\n[1/4] Chargement du modèle")
        model_loader = ModelLoader(MODEL_NAME)
        
        if use_merged:
            merged_path = self.config.get_path("merged_folder")
            model = model_loader.charger_modele_merged(merged_path)
            tokenizer_path = merged_path
        else:
            lora_path = self.config.get_path("lora_folder")
            model = model_loader.charger_modele_avec_lora(
                lora_path, use_quantization=True
            )
            tokenizer_path = lora_path
        
        # Charger le tokenizer
        tokenizer_mgr = TokenizerManager(MODEL_NAME)
        tokenizer = tokenizer_mgr.charger_tokenizer_depuis_checkpoint(tokenizer_path)
        
        # Créer le prédicteur
        print("\n[2/4] Initialisation du prédicteur")
        predictor = Predictor(model, tokenizer)
        
        # Créer l'évaluateur
        print("\n[3/4] Évaluation sur fichier de test")
        evaluator = Evaluator(predictor)
        
        test_path = self.config.get_path("test_daily")
        df_resultats = evaluator.evaluer_fichier_test(test_path)
        
        # Sauvegarder les résultats
        result_path = self.config.get_path("result_test")
        df_resultats.to_excel(result_path, index=False, engine='openpyxl')
        print(f"\n✅ Résultats sauvegardés : {result_path}")
        
        # Évaluation avec validation si disponible
        print("\n[4/4] Évaluation avec fichier de validation")
        try:
            valid_path = self.config.get_path("valid_daily")
            metriques = evaluator.evaluer_avec_validation(
                df_resultats, valid_path
            )
            
            # Générer le rapport
            eval_report = self.config.get_path("eval_report")
            evaluator.generer_rapport_excel(
                metriques["df_eval"],
                metriques["erreurs_par_cat"],
                eval_report,
                metriques
            )
            
            print(f"\n✅ ÉVALUATION TERMINÉE")
            print(f"   Accuracy globale : {metriques['accuracy']:.1f}%")
            
        except Exception as e:
            print(f"\n⚠️  Évaluation avec validation impossible : {e}")
    
    def predire_simple(self, commentaire: str, owner: str = "", 
                      topology: str = "", vendors: str = ""):
        """
        Effectue une prédiction simple sur un commentaire
        
        Args:
            commentaire: Commentaire de l'incident
            owner: Owner (optionnel)
            topology: Topology (optionnel)
            vendors: Vendors (optionnel)
        """
        print("\n" + "="*60)
        print("🔮 PRÉDICTION SIMPLE")
        print("="*60)
        
        # Charger le modèle mergé
        print("\n[1/2] Chargement du modèle")
        model_loader = ModelLoader(MODEL_NAME)
        merged_path = self.config.get_path("merged_folder")
        model = model_loader.charger_modele_merged(merged_path)
        
        tokenizer_mgr = TokenizerManager(MODEL_NAME)
        tokenizer = tokenizer_mgr.charger_tokenizer_depuis_checkpoint(merged_path)
        
        # Créer le prédicteur et prédire
        print("\n[2/2] Prédiction en cours")
        predictor = Predictor(model, tokenizer)
        analyse, cause, justif = predictor.predire(
            commentaire, owner, topology, vendors
        )
        
        print("\n📋 RÉSULTAT :")
        print(f"   Commentaire    : {commentaire[:100]}...")
        print(f"   Cause prédite  : {cause}")
        print(f"   Justification  : {justif}")
        print(f"   Analyse        : {analyse[:100]}...")


def main():
    """
    Point d'entrée principal
    """
    parser = argparse.ArgumentParser(
        description="Pipeline de fine-tuning pour analyse d'incidents réseau"
    )
    
    parser.add_argument(
        "action",
        choices=["train", "merge", "evaluate", "full", "predict"],
        help="Action à effectuer"
    )
    
    parser.add_argument(
        "--config-dir",
        type=str,
        default=None,
        help="Chemin vers le dossier de configuration"
    )
    
    parser.add_argument(
        "--use-merged",
        action="store_true",
        help="Utiliser le modèle mergé pour l'évaluation"
    )
    
    parser.add_argument(
        "--commentaire",
        type=str,
        default="",
        help="Commentaire pour la prédiction simple"
    )
    
    args = parser.parse_args()
    
    # Créer le pipeline
    pipeline = FineTuningPipeline(args.config_dir)
    
    # Exécuter l'action demandée
    if args.action == "train":
        pipeline.entrainer()
    
    elif args.action == "merge":
        pipeline.merger()
    
    elif args.action == "evaluate":
        pipeline.evaluer(use_merged=args.use_merged)
    
    elif args.action == "full":
        print("\n🎯 PIPELINE COMPLET : TRAIN → MERGE → EVALUATE")
        pipeline.entrainer()
        pipeline.merger()
        pipeline.evaluer(use_merged=True)
    
    elif args.action == "predict":
        if not args.commentaire:
            print("❌ Veuillez fournir un commentaire avec --commentaire")
            sys.exit(1)
        pipeline.predire_simple(args.commentaire)
    
    print("\n" + "="*60)
    print("✅ TERMINÉ")
    print("="*60)


if __name__ == "__main__":
    main()
