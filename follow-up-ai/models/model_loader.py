"""
Chargeur de modèles pour le fine-tuning
"""

import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from typing import Optional
from utils.helpers import nettoyer_memoire, afficher_info_gpu


class ModelLoader:
    """
    Classe pour charger et gérer les modèles
    """
    
    def __init__(self, model_name: str):
        """
        Initialise le chargeur de modèles
        
        Args:
            model_name: Nom du modèle (ex: "Qwen/Qwen2.5-3B-Instruct")
        """
        self.model_name = model_name
        self.model = None
        
    def creer_quant_config(self, load_in_4bit: bool = True) -> BitsAndBytesConfig:
        """
        Crée la configuration de quantization
        
        Args:
            load_in_4bit: Si True, utilise la quantization 4-bit
            
        Returns:
            Configuration de quantization
        """
        if load_in_4bit:
            config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            print("✅ Configuration 4-bit créée")
        else:
            config = None
            print("✅ Pas de quantization")
        
        return config
    
    def charger_modele_base(self, use_quantization: bool = True) -> AutoModelForCausalLM:
        """
        Charge le modèle de base
        
        Args:
            use_quantization: Si True, utilise la quantization 4-bit
            
        Returns:
            Modèle chargé
        """
        nettoyer_memoire()
        
        print(f"\n⏳ Chargement du modèle : {self.model_name}")
        
        if use_quantization:
            quant_config = self.creer_quant_config()
            dtype = None
        else:
            quant_config = None
            dtype = torch.float16
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=quant_config,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )
        
        self.model.config.use_cache = False
        
        print(f"✅ Modèle chargé")
        afficher_info_gpu()
        
        return self.model
    
    def charger_modele_merged(self, chemin: str) -> AutoModelForCausalLM:
        """
        Charge un modèle mergé (LoRA fusionné avec le modèle de base)
        
        Args:
            chemin: Chemin vers le modèle mergé
            
        Returns:
            Modèle chargé
        """
        nettoyer_memoire()
        
        print(f"\n⏳ Chargement du modèle mergé : {chemin}")
        
        self.model = AutoModelForCausalLM.from_pretrained(
            chemin,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        
        self.model.eval()
        
        print(f"✅ Modèle mergé chargé")
        afficher_info_gpu()
        
        return self.model
    
    def charger_modele_avec_lora(self, chemin_lora: str, 
                                 use_quantization: bool = True) -> PeftModel:
        """
        Charge le modèle de base et applique les adaptateurs LoRA
        
        Args:
            chemin_lora: Chemin vers les adaptateurs LoRA
            use_quantization: Si True, utilise la quantization 4-bit
            
        Returns:
            Modèle avec LoRA appliqué
        """
        # Charger le modèle de base
        if self.model is None:
            self.charger_modele_base(use_quantization=use_quantization)
        
        print(f"\n⏳ Chargement des adaptateurs LoRA : {chemin_lora}")
        
        self.model = PeftModel.from_pretrained(self.model, chemin_lora)
        self.model.eval()
        
        print(f"✅ LoRA appliqué au modèle")
        
        return self.model
    
    def get_model(self) -> Optional[AutoModelForCausalLM]:
        """
        Retourne le modèle chargé
        
        Returns:
            Modèle ou None si pas encore chargé
        """
        return self.model
    
    def deplacer_vers_cpu(self):
        """
        Déplace le modèle vers le CPU pour libérer la VRAM
        """
        if self.model is not None:
            print("⏳ Déplacement du modèle vers CPU...")
            self.model = self.model.to("cpu")
            nettoyer_memoire()
            print("✅ Modèle sur CPU")
    
    def sauvegarder_modele(self, chemin: str, max_shard_size: str = "2GB"):
        """
        Sauvegarde le modèle
        
        Args:
            chemin: Chemin de sauvegarde
            max_shard_size: Taille maximale des shards
        """
        if self.model is None:
            raise ValueError("Aucun modèle chargé")
        
        print(f"\n⏳ Sauvegarde du modèle : {chemin}")
        
        self.model.save_pretrained(
            chemin,
            max_shard_size=max_shard_size,
            safe_serialization=True
        )
        
        print(f"✅ Modèle sauvegardé : {chemin}")
    
    def __repr__(self) -> str:
        """Représentation textuelle"""
        return f"ModelLoader(model_name={self.model_name}, loaded={self.model is not None})"
