"""
Gestionnaire de tokenizer pour le fine-tuning
"""

from transformers import AutoTokenizer
from typing import Optional


class TokenizerManager:
    """
    Classe pour gérer le chargement et la configuration du tokenizer
    """
    
    def __init__(self, model_name: str):
        """
        Initialise le gestionnaire de tokenizer
        
        Args:
            model_name: Nom du modèle (ex: "Qwen/Qwen2.5-3B-Instruct")
        """
        self.model_name = model_name
        self.tokenizer = None
        
    def charger_tokenizer(self) -> AutoTokenizer:
        """
        Charge et configure le tokenizer
        
        Returns:
            Tokenizer configuré
        """
        print(f"⏳ Chargement du tokenizer : {self.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        
        # Configuration du tokenizer
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        print(f"✅ Tokenizer chargé et configuré")
        print(f"   Vocab size    : {len(self.tokenizer)}")
        print(f"   Pad token     : {self.tokenizer.pad_token}")
        print(f"   EOS token     : {self.tokenizer.eos_token}")
        print(f"   Padding side  : {self.tokenizer.padding_side}")
        
        return self.tokenizer
    
    def get_tokenizer(self) -> AutoTokenizer:
        """
        Retourne le tokenizer (le charge si nécessaire)
        
        Returns:
            Tokenizer
        """
        if self.tokenizer is None:
            return self.charger_tokenizer()
        return self.tokenizer
    
    def sauvegarder_tokenizer(self, chemin: str):
        """
        Sauvegarde le tokenizer
        
        Args:
            chemin: Chemin de sauvegarde
        """
        if self.tokenizer is None:
            raise ValueError("Aucun tokenizer chargé")
            
        self.tokenizer.save_pretrained(chemin)
        print(f"✅ Tokenizer sauvegardé : {chemin}")
    
    def charger_tokenizer_depuis_checkpoint(self, chemin: str) -> AutoTokenizer:
        """
        Charge un tokenizer depuis un checkpoint
        
        Args:
            chemin: Chemin du checkpoint
            
        Returns:
            Tokenizer chargé
        """
        print(f"⏳ Chargement du tokenizer depuis : {chemin}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            chemin,
            trust_remote_code=True
        )
        
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        print(f"✅ Tokenizer chargé depuis checkpoint")
        
        return self.tokenizer
    
    def __repr__(self) -> str:
        """Représentation textuelle"""
        return f"TokenizerManager(model_name={self.model_name}, loaded={self.tokenizer is not None})"
