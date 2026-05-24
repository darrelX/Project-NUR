"""
Gestionnaire d'entraînement pour le fine-tuning
"""

from trl import SFTTrainer, SFTConfig
from typing import Dict, Any
from utils.helpers import creer_dossier


class ModelTrainer:
    """
    Classe pour gérer l'entraînement du modèle
    """
    
    def __init__(self, model, tokenizer, train_dataset, eval_dataset, config: Dict[str, Any]):
        """
        Initialise le gestionnaire d'entraînement
        
        Args:
            model: Modèle à entraîner
            tokenizer: Tokenizer
            train_dataset: Dataset d'entraînement
            eval_dataset: Dataset d'évaluation
            config: Configuration d'entraînement
        """
        self.model = model
        self.tokenizer = tokenizer
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset
        self.config = config
        self.trainer = None
        
    def creer_sft_config(self, output_dir: str, warmup_steps: int) -> SFTConfig:
        """
        Crée la configuration SFT
        
        Args:
            output_dir: Dossier de sortie
            warmup_steps: Nombre de steps de warmup
            
        Returns:
            Configuration SFT
        """
        creer_dossier(output_dir)
        
        sft_config = SFTConfig(
            output_dir=output_dir,
            num_train_epochs=self.config.get("num_train_epochs", 5),
            per_device_train_batch_size=self.config.get("per_device_train_batch_size", 1),
            per_device_eval_batch_size=self.config.get("per_device_eval_batch_size", 1),
            gradient_accumulation_steps=self.config.get("gradient_accumulation_steps", 8),
            optim=self.config.get("optim", "paged_adamw_8bit"),
            learning_rate=self.config.get("learning_rate", 1e-4),
            weight_decay=self.config.get("weight_decay", 0.01),
            warmup_steps=warmup_steps,
            lr_scheduler_type=self.config.get("lr_scheduler_type", "cosine"),
            bf16=self.config.get("bf16", True),
            fp16=self.config.get("fp16", False),
            logging_steps=self.config.get("logging_steps", 10),
            eval_strategy=self.config.get("eval_strategy", "steps"),
            eval_steps=self.config.get("eval_steps", 50),
            save_strategy=self.config.get("save_strategy", "steps"),
            save_steps=self.config.get("save_steps", 50),
            save_total_limit=self.config.get("save_total_limit", 2),
            load_best_model_at_end=self.config.get("load_best_model_at_end", True),
            metric_for_best_model=self.config.get("metric_for_best_model", "eval_loss"),
            greater_is_better=self.config.get("greater_is_better", False),
            report_to=self.config.get("report_to", "none"),
            gradient_checkpointing=self.config.get("gradient_checkpointing", True),
            gradient_checkpointing_kwargs=self.config.get(
                "gradient_checkpointing_kwargs", 
                {"use_reentrant": False}
            ),
            dataloader_num_workers=self.config.get("dataloader_num_workers", 0),
            group_by_length=self.config.get("group_by_length", True),
            max_grad_norm=self.config.get("max_grad_norm", 1.0),
            packing=self.config.get("packing", False),
        )
        
        print("✅ Configuration SFT créée")
        print(f"   Output dir     : {output_dir}")
        print(f"   Num epochs     : {sft_config.num_train_epochs}")
        print(f"   Batch size     : {sft_config.per_device_train_batch_size}")
        print(f"   Grad accum     : {sft_config.gradient_accumulation_steps}")
        print(f"   Learning rate  : {sft_config.learning_rate}")
        print(f"   Warmup steps   : {warmup_steps}")
        
        return sft_config
    
    def creer_trainer(self, sft_config: SFTConfig):
        """
        Crée le trainer SFT
        
        Args:
            sft_config: Configuration SFT
        """
        print("\n⏳ Création du trainer...")
        
        self.trainer = SFTTrainer(
            model=self.model,
            processing_class=self.tokenizer,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset,
            args=sft_config,
        )
        
        print("✅ Trainer créé")
        
    def entrainer(self):
        """
        Lance l'entraînement
        """
        if self.trainer is None:
            raise ValueError("Trainer non initialisé. Appelez creer_trainer() d'abord.")
        
        print("\n" + "="*60)
        print("🚀 LANCEMENT DE L'ENTRAÎNEMENT")
        print("="*60)
        
        self.trainer.train()
        
        print("\n" + "="*60)
        print("✅ ENTRAÎNEMENT TERMINÉ")
        print("="*60)
    
    def sauvegarder_modele(self, chemin: str):
        """
        Sauvegarde le modèle entraîné
        
        Args:
            chemin: Chemin de sauvegarde
        """
        print(f"\n⏳ Sauvegarde du modèle : {chemin}")
        
        creer_dossier(chemin)
        self.model.save_pretrained(chemin)
        
        print(f"✅ Modèle sauvegardé : {chemin}")
    
    def sauvegarder_tokenizer(self, chemin: str):
        """
        Sauvegarde le tokenizer
        
        Args:
            chemin: Chemin de sauvegarde
        """
        print(f"⏳ Sauvegarde du tokenizer : {chemin}")
        
        self.tokenizer.save_pretrained(chemin)
        
        print(f"✅ Tokenizer sauvegardé : {chemin}")
    
    def sauvegarder_tout(self, chemin: str):
        """
        Sauvegarde le modèle et le tokenizer
        
        Args:
            chemin: Chemin de sauvegarde
        """
        self.sauvegarder_modele(chemin)
        self.sauvegarder_tokenizer(chemin)
    
    def get_trainer(self):
        """
        Retourne le trainer
        
        Returns:
            Trainer ou None
        """
        return self.trainer
    
    def __repr__(self) -> str:
        """Représentation textuelle"""
        return f"ModelTrainer(epochs={self.config.get('num_train_epochs', 'N/A')}, trainer_ready={self.trainer is not None})"
