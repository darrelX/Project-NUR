"""
Gestionnaire de configuration pour le projet
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Gestionnaire centralisé de configuration
    
    Charge et gère les configurations depuis les fichiers YAML
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialise le gestionnaire de configuration
        
        Args:
            config_dir: Chemin vers le dossier de configuration
        """
        if config_dir is None:
            # Chemin par défaut: dossier config/ relatif à ce fichier
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)
            
        self.paths_config = self._load_yaml("paths.yaml")
        self.lora_config = self._load_yaml("lora_config.yaml")
        self.train_config = self._load_yaml("train_config.yaml")
        
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Charge un fichier YAML
        
        Args:
            filename: Nom du fichier YAML
            
        Returns:
            Dictionnaire de configuration
        """
        filepath = self.config_dir / filename
        if not filepath.exists():
            print(f"⚠️  Fichier de configuration non trouvé : {filepath}")
            return {}
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def get_path(self, key: str) -> str:
        """
        Récupère un chemin depuis la configuration
        
        Args:
            key: Clé du chemin (ex: 'train_jsonl', 'lora_folder')
            
        Returns:
            Chemin complet
        """
        base = self.paths_config.get("base_drive", "")
        relative = self.paths_config.get(key, "")
        
        if not relative:
            raise ValueError(f"Clé de chemin non trouvée : {key}")
            
        # Si le chemin relatif est absolu, le retourner directement
        if os.path.isabs(relative):
            return relative
            
        return os.path.join(base, relative)
    
    def get_lora_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration LoRA
        
        Returns:
            Configuration LoRA
        """
        return self.lora_config
    
    def get_train_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration d'entraînement
        
        Returns:
            Configuration d'entraînement
        """
        return self.train_config
    
    def get_lora_r(self) -> int:
        """Retourne le rang LoRA"""
        return self.lora_config.get("r", 32)
    
    def get_lora_alpha(self) -> int:
        """Retourne l'alpha LoRA"""
        return self.lora_config.get("lora_alpha", 64)
    
    def get_lora_dropout(self) -> float:
        """Retourne le dropout LoRA"""
        return self.lora_config.get("lora_dropout", 0.05)
    
    def get_lora_target_modules(self) -> list:
        """Retourne les modules cibles LoRA"""
        return self.lora_config.get("target_modules", [
            "q_proj", "v_proj", "k_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ])
    
    def get_num_epochs(self) -> int:
        """Retourne le nombre d'epochs"""
        return self.train_config.get("num_train_epochs", 5)
    
    def get_batch_size(self) -> int:
        """Retourne la taille de batch"""
        return self.train_config.get("per_device_train_batch_size", 1)
    
    def get_gradient_accumulation_steps(self) -> int:
        """Retourne le nombre de steps d'accumulation de gradient"""
        return self.train_config.get("gradient_accumulation_steps", 8)
    
    def get_learning_rate(self) -> float:
        """Retourne le taux d'apprentissage"""
        return self.train_config.get("learning_rate", 1e-4)
    
    def get_max_seq_length(self) -> int:
        """Retourne la longueur maximale de séquence"""
        return self.train_config.get("max_seq_length", 768)
    
    def get_warmup_ratio(self) -> float:
        """Retourne le ratio de warmup"""
        return self.train_config.get("warmup_ratio", 0.05)
    
    def get_weight_decay(self) -> float:
        """Retourne le weight decay"""
        return self.train_config.get("weight_decay", 0.01)
    
    def __repr__(self) -> str:
        """Représentation textuelle du gestionnaire"""
        return f"ConfigManager(config_dir={self.config_dir})"
