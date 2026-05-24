"""
Prétraitement des données pour le fine-tuning
"""

from typing import Dict, Any, List
from datasets import Dataset


class DataPreprocessor:
    """
    Classe pour prétraiter les données et les formater pour l'entraînement
    """
    
    def __init__(self, tokenizer):
        """
        Initialise le préprocesseur
        
        Args:
            tokenizer: Tokenizer à utiliser pour le formatage
        """
        self.tokenizer = tokenizer
        
    def formater_exemple(self, exemple: Dict[str, Any]) -> Dict[str, str]:
        """
        Formate un exemple avec le chat template
        
        Args:
            exemple: Dictionnaire contenant les messages
            
        Returns:
            Dictionnaire avec le texte formaté
        """
        return {
            "text": self.tokenizer.apply_chat_template(
                exemple["messages"],
                tokenize=False,
                add_generation_prompt=False
            )
        }
    
    def tokeniser_exemple(self, exemple: Dict[str, str], max_length: int) -> Dict[str, Any]:
        """
        Tokenise un exemple
        
        Args:
            exemple: Dictionnaire contenant le texte formaté
            max_length: Longueur maximale de séquence
            
        Returns:
            Dictionnaire avec les tokens
        """
        tokens = self.tokenizer(
            exemple["text"],
            truncation=True,
            max_length=max_length,
            padding=False
        )
        tokens["labels"] = tokens["input_ids"].copy()
        return tokens
    
    def preparer_datasets(self, train_data: List[Dict[str, Any]], 
                         val_data: List[Dict[str, Any]], 
                         max_seq_length: int) -> tuple:
        """
        Prépare les datasets d'entraînement et de validation
        
        Args:
            train_data: Données d'entraînement
            val_data: Données de validation
            max_seq_length: Longueur maximale de séquence
            
        Returns:
            Tuple (train_tokenized, val_tokenized)
        """
        print("\n⏳ Préparation des datasets...")
        
        # Créer les datasets
        train_ds = Dataset.from_list(train_data)
        val_ds = Dataset.from_list(val_data)
        
        print(f"   Datasets créés : train={len(train_ds)}, val={len(val_ds)}")
        
        # Appliquer le formatage
        train_ds = train_ds.map(
            self.formater_exemple,
            remove_columns=train_ds.column_names
        )
        val_ds = val_ds.map(
            self.formater_exemple,
            remove_columns=val_ds.column_names
        )
        
        print("   ✅ Formatage appliqué")
        
        # Tokeniser
        train_tok = train_ds.map(
            lambda x: self.tokeniser_exemple(x, max_seq_length),
            remove_columns=["text"],
            batched=False
        )
        val_tok = val_ds.map(
            lambda x: self.tokeniser_exemple(x, max_seq_length),
            remove_columns=["text"],
            batched=False
        )
        
        print("   ✅ Tokenisation terminée")
        
        return train_tok, val_tok
    
    def calculer_steps(self, train_size: int, batch_size: int, 
                       grad_accum: int, num_epochs: int, 
                       warmup_ratio: float) -> Dict[str, int]:
        """
        Calcule les steps d'entraînement
        
        Args:
            train_size: Taille du dataset d'entraînement
            batch_size: Taille de batch
            grad_accum: Steps d'accumulation de gradient
            num_epochs: Nombre d'epochs
            warmup_ratio: Ratio de warmup
            
        Returns:
            Dictionnaire avec les steps calculés
        """
        steps_per_epoch = train_size // (batch_size * grad_accum)
        total_steps = steps_per_epoch * num_epochs
        warmup_steps = max(1, int(total_steps * warmup_ratio))
        
        steps_info = {
            "steps_per_epoch": steps_per_epoch,
            "total_steps": total_steps,
            "warmup_steps": warmup_steps
        }
        
        print(f"\n📊 Calcul des steps :")
        print(f"   Steps par epoch : {steps_per_epoch}")
        print(f"   Total steps     : {total_steps}")
        print(f"   Warmup steps    : {warmup_steps}")
        
        return steps_info
    
    def __repr__(self) -> str:
        """Représentation textuelle"""
        return f"DataPreprocessor(tokenizer={self.tokenizer.__class__.__name__})"
