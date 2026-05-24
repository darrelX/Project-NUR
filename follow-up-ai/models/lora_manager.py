"""
Gestionnaire LoRA pour le fine-tuning
"""

import os
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from typing import Dict, Any, Optional
from utils.helpers import nettoyer_memoire, creer_dossier


class LoraManager:
    """
    Classe pour gérer la configuration et l'application de LoRA
    """
    
    def __init__(self, r: int = 32, lora_alpha: int = 64, 
                 lora_dropout: float = 0.05, 
                 target_modules: Optional[list] = None):
        """
        Initialise le gestionnaire LoRA
        
        Args:
            r: Rang LoRA
            lora_alpha: Alpha LoRA
            lora_dropout: Dropout LoRA
            target_modules: Modules cibles pour LoRA
        """
        self.r = r
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        
        if target_modules is None:
            self.target_modules = [
                "q_proj", "v_proj", "k_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]
        else:
            self.target_modules = target_modules
        
        self.lora_config = None
        self.peft_model = None
        
    def creer_config(self) -> LoraConfig:
        """
        Crée la configuration LoRA
        
        Returns:
            Configuration LoRA
        """
        self.lora_config = LoraConfig(
            r=self.r,
            lora_alpha=self.lora_alpha,
            lora_dropout=self.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            target_modules=self.target_modules,
        )
        
        print("✅ Configuration LoRA créée :")
        print(f"   r              : {self.r}")
        print(f"   lora_alpha     : {self.lora_alpha}")
        print(f"   lora_dropout   : {self.lora_dropout}")
        print(f"   target_modules : {self.target_modules}")
        
        return self.lora_config
    
    def appliquer_lora(self, model):
        """
        Applique LoRA à un modèle
        
        Args:
            model: Modèle de base
            
        Returns:
            Modèle avec LoRA appliqué
        """
        if self.lora_config is None:
            self.creer_config()
        
        print("\n⏳ Application de LoRA au modèle...")
        
        self.peft_model = get_peft_model(model, self.lora_config)
        
        print("✅ LoRA appliqué")
        self.peft_model.print_trainable_parameters()
        
        return self.peft_model
    
    def merger_lora(self, model_base, chemin_lora: str, 
                    chemin_sortie: str) -> Any:
        """
        Merge les adaptateurs LoRA avec le modèle de base
        
        Args:
            model_base: Modèle de base
            chemin_lora: Chemin vers les adaptateurs LoRA
            chemin_sortie: Chemin de sauvegarde du modèle mergé
            
        Returns:
            Modèle mergé
        """
        nettoyer_memoire()
        
        print("\n⏳ Merge LoRA + Modèle de base...")
        print(f"   Modèle base : {model_base.config._name_or_path}")
        print(f"   LoRA        : {chemin_lora}")
        
        # Charger les adaptateurs LoRA
        print("   Chargement des adaptateurs...")
        model_merge = PeftModel.from_pretrained(model_base, chemin_lora)
        
        # Merger
        print("   Fusion en cours...")
        model_merge = model_merge.merge_and_unload()
        
        # Déplacer sur CPU pour libérer la VRAM
        print("   Déplacement vers CPU...")
        model_merge = model_merge.to("cpu")
        
        # Sauvegarder
        print(f"   Sauvegarde : {chemin_sortie}")
        creer_dossier(chemin_sortie)
        
        model_merge.save_pretrained(
            chemin_sortie,
            max_shard_size="2GB",
            safe_serialization=True
        )
        
        print(f"✅ Modèle mergé sauvegardé : {chemin_sortie}")
        
        # Afficher les fichiers créés
        if os.path.exists(chemin_sortie):
            fichiers = sorted(os.listdir(chemin_sortie))
            print(f"\n📁 Fichiers créés ({len(fichiers)}) :")
            for f in fichiers[:10]:  # Afficher les 10 premiers
                taille = os.path.getsize(os.path.join(chemin_sortie, f)) / 1024**2
                print(f"   {f:<40} {taille:>8.1f} MB")
            if len(fichiers) > 10:
                print(f"   ... et {len(fichiers) - 10} autres fichiers")
        
        nettoyer_memoire()
        
        return model_merge
    
    def sauvegarder_adaptateurs(self, chemin: str):
        """
        Sauvegarde les adaptateurs LoRA
        
        Args:
            chemin: Chemin de sauvegarde
        """
        if self.peft_model is None:
            raise ValueError("Aucun modèle PEFT disponible")
        
        print(f"\n⏳ Sauvegarde des adaptateurs LoRA : {chemin}")
        
        creer_dossier(chemin)
        self.peft_model.save_pretrained(chemin)
        
        print(f"✅ Adaptateurs sauvegardés : {chemin}")
    
    def get_config(self) -> Optional[LoraConfig]:
        """
        Retourne la configuration LoRA
        
        Returns:
            Configuration LoRA ou None
        """
        return self.lora_config
    
    def get_peft_model(self):
        """
        Retourne le modèle PEFT
        
        Returns:
            Modèle PEFT ou None
        """
        return self.peft_model
    
    def __repr__(self) -> str:
        """Représentation textuelle"""
        return f"LoraManager(r={self.r}, alpha={self.lora_alpha}, dropout={self.lora_dropout})"
