"""
Chargeur de données pour le fine-tuning
"""

import json
from typing import List, Dict, Any
from collections import Counter


class DataLoader:
    """
    Classe pour charger et analyser les données d'entraînement et de validation
    """
    
    def __init__(self):
        """Initialise le chargeur de données"""
        self.train_data = []
        self.val_data = []
        
    def charger_jsonl(self, chemin: str) -> List[Dict[str, Any]]:
        """
        Charge un fichier JSONL
        
        Args:
            chemin: Chemin vers le fichier JSONL
            
        Returns:
            Liste de dictionnaires contenant les données
        """
        data = []
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                for ligne in f:
                    ligne = ligne.strip()
                    if ligne:
                        data.append(json.loads(ligne))
            print(f"✅ Chargé {len(data)} exemples depuis {chemin}")
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé : {chemin}")
        except Exception as e:
            print(f"❌ Erreur lors du chargement : {e}")
        
        return data
    
    def charger_train_val(self, train_path: str, val_path: str):
        """
        Charge les données d'entraînement et de validation
        
        Args:
            train_path: Chemin vers le fichier d'entraînement
            val_path: Chemin vers le fichier de validation
        """
        self.train_data = self.charger_jsonl(train_path)
        self.val_data = self.charger_jsonl(val_path)
        
        print(f"\n📊 Statistiques des données :")
        print(f"   Train      : {len(self.train_data)} exemples")
        print(f"   Validation : {len(self.val_data)} exemples")
        
        # Analyser la distribution
        self.analyser_distribution()
        
    def analyser_distribution(self):
        """
        Analyse et affiche la distribution des causes dans les données d'entraînement
        """
        if not self.train_data:
            print("⚠️  Aucune donnée d'entraînement chargée")
            return
            
        # Extraire les causes
        causes = []
        for ex in self.train_data:
            if "messages" in ex and len(ex["messages"]) >= 3:
                # La cause est dans le 3ème message (assistant)
                content = ex["messages"][2].get("content", "")
                if "Cause :" in content:
                    cause = content.replace("Cause :", "").strip()
                    causes.append(cause)
        
        if not causes:
            print("⚠️  Aucune cause trouvée dans les données")
            return
            
        # Compter la distribution
        dist = Counter(causes)
        
        print(f"\n📊 Distribution des causes (train) :")
        print(f"   {'Cause':<50} {'Nombre':>8} {'Statut':>8}")
        print(f"   {'-'*70}")
        
        for cause, count in sorted(dist.items(), key=lambda x: x[1], reverse=True):
            statut = "✅" if count >= 30 else "⚠️ "
            print(f"   {statut} {cause:<48} {count:>8}")
        
        print(f"   {'-'*70}")
        print(f"   {'TOTAL':<50} {len(causes):>8}")
        
    def get_train_data(self) -> List[Dict[str, Any]]:
        """Retourne les données d'entraînement"""
        return self.train_data
    
    def get_val_data(self) -> List[Dict[str, Any]]:
        """Retourne les données de validation"""
        return self.val_data
    
    def __len__(self) -> int:
        """Retourne le nombre total d'exemples"""
        return len(self.train_data) + len(self.val_data)
    
    def __repr__(self) -> str:
        """Représentation textuelle"""
        return f"DataLoader(train={len(self.train_data)}, val={len(self.val_data)})"
