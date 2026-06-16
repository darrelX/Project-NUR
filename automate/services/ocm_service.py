"""
Service pour le traitement OCM RAN
Wrapper autour de la classe SuperXlookup existante
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import streamlit as st

# Ajouter le dossier parent au path pour importer super_xlookup
sys.path.insert(0, str(Path(__file__).parent.parent))

from super_xlookup import SuperXlookup
from utils.logger import Logger


class OcmService:
    """Service pour exécuter le traitement OCM RAN"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
    
    def execute(self, config: Dict[str, Any]) -> bool:
        """
        Exécute le traitement OCM RAN avec la configuration fournie
        
        Args:
            config: Dictionnaire de configuration avec les paramètres
                   
        Returns:
            bool: True si succès, False sinon
        """
        try:
            self.logger.info("Démarrage du traitement OCM RAN...")
            
            # Debug: afficher tous les paramètres reçus
            self.logger.info(f"=== DEBUG OCM: Config reçue ===")
            for key, value in config.items():
                self.logger.info(f"  {key}: {value}")
            self.logger.info(f"========================")
            
            # Validation des paramètres requis
            required_params = [
                'source_file_path',
                'target_file_path',
                'source_sheet_name'
            ]
            
            for param in required_params:
                if param not in config or not config[param]:
                    self.logger.error(f"Paramètre manquant : {param}")
                    return False
            
            # Créer l'instance SuperXlookup
            self.logger.info(f"Fichier source : {config['source_file_path']}")
            self.logger.info(f"Fichier cible : {config['target_file_path']}")
            
            ocm = SuperXlookup(
                source_file_path=config['source_file_path'],
                target_file_path=config['target_file_path'],
                source_sheet_name=config['source_sheet_name'],
                source_key_column=config.get('source_key_column', 'Codesite'),
                target_key_column=config.get('target_key_column', ['Site ID', 'SITE_ID', 'site id', 'Site Code']),
                target_value_column=config.get('target_value_column', ['Actions en cours', 'Action en cours', 'Actions']),
                result_position_column=config.get('result_position_column', 'last_column'),
                result_column_name=config.get('result_column_name', 'OCM RAN'),
                target_sheet_name=config.get('target_sheet_name', 'ALL SITES DOWN'),
                reference_name=config.get('reference_name', 'OCM RAN')
            )
            
            self.logger.info("Lecture des fichiers Excel...")
            
            self.logger.info("Exécution du XLOOKUP...")
            ocm.run()
            
            self.logger.success("✅ OCM RAN terminé avec succès !")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement OCM RAN : {str(e)}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Valide la configuration avant exécution
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Vérifier les fichiers
        source_path = Path(config.get('source_file_path', ''))
        target_path = Path(config.get('target_file_path', ''))
        
        if not source_path.exists():
            return False, "Fichier source introuvable"
        
        if not target_path.exists():
            return False, "Fichier cible OCM RAN introuvable"
        
        # Vérifier la feuille
        if not config.get('source_sheet_name'):
            return False, "Feuille source non spécifiée"
        
        return True, None
    
    def preview_matches(self, config: Dict[str, Any]) -> Optional[Dict]:
        """
        Prévisualise les correspondances sans modifier les fichiers
        
        Returns:
            Dict avec les statistiques de correspondances ou None si erreur
        """
        try:
            import pandas as pd
            from utils.excel_utils import ExcelFileHandler
            
            # Lire les fichiers
            source_df = ExcelFileHandler.read_excel(
                config['source_file_path'],
                config['source_sheet_name']
            )
            
            target_sheet = config.get('target_sheet_name', 'ALL SITES DOWN')
            target_df = ExcelFileHandler.read_excel(
                config['target_file_path'],
                target_sheet if target_sheet else None
            )
            
            if source_df is None or target_df is None:
                return None
            
            # Trouver les colonnes clés
            source_key = config.get('source_key_column', 'B')
            target_key = config.get('target_key_column', 'D')
            
            # Si ce sont des lettres, les convertir en index pour pandas
            if isinstance(source_key, str) and source_key.isalpha():
                source_key_idx = ExcelFileHandler._col_letter_to_index(source_key)
                if source_key_idx < len(source_df.columns):
                    source_key = source_df.columns[source_key_idx]
            
            if isinstance(target_key, str) and target_key.isalpha():
                target_key_idx = ExcelFileHandler._col_letter_to_index(target_key)
                if target_key_idx < len(target_df.columns):
                    target_key = target_df.columns[target_key_idx]
            
            # Analyser les correspondances
            if source_key in source_df.columns and target_key in target_df.columns:
                matches = ExcelFileHandler.analyze_matches(
                    source_df, target_df,
                    source_key, target_key
                )
                return matches
            else:
                return {
                    "error": "Colonnes clés non trouvées",
                    "total_matches": 0
                }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la prévisualisation : {str(e)}")
            return None


# Helper method pour ExcelFileHandler
def _col_letter_to_index(col: str) -> int:
    """Convertit une lettre Excel (A, B, AA) en index 0-based"""
    col = col.upper().strip()
    result = 0
    for ch in col:
        result = result * 26 + (ord(ch) - ord('A') + 1)
    return result - 1


# Ajouter la méthode à ExcelFileHandler si elle n'existe pas
from utils.excel_utils import ExcelFileHandler
if not hasattr(ExcelFileHandler, '_col_letter_to_index'):
    ExcelFileHandler._col_letter_to_index = staticmethod(_col_letter_to_index)
