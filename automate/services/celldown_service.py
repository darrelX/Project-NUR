"""
Service pour le traitement CellDown
Wrapper autour de la classe CellDown existante
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import streamlit as st

# Ajouter le dossier parent au path pour importer celldown
sys.path.insert(0, str(Path(__file__).parent.parent))

from celldown import CellDown
from utils.logger import Logger


class CellDownService:
    """Service pour exécuter le traitement CellDown"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
    
    def execute(self, config: Dict[str, Any]) -> bool:
        """
        Exécute le traitement CellDown avec la configuration fournie
        
        Args:
            config: Dictionnaire de configuration avec les paramètres
                   
        Returns:
            bool: True si succès, False sinon
        """
        try:
            self.logger.info("Démarrage du traitement CellDown...")
            
            # Debug: afficher tous les paramètres reçus
            self.logger.info(f"=== DEBUG: Config reçue ===")
            for key, value in config.items():
                self.logger.info(f"  {key}: {value}")
            self.logger.info(f"========================")
            
            # Validation des paramètres requis
            required_params = [
                'source_file_path',
                'target_file_path',
                'source_sheet_path',
                'date_str'
            ]
            
            for param in required_params:
                if param not in config or not config[param]:
                    self.logger.error(f"Paramètre manquant : {param}")
                    return False
            
            # Créer l'instance CellDown
            self.logger.info(f"Fichier source : {config['source_file_path']}")
            self.logger.info(f"Fichier cible : {config['target_file_path']}")
            self.logger.info(f"Date : {config['date_str']}")
            
            celldown = CellDown(
                source_file_path=config['source_file_path'],
                target_file_path=config['target_file_path'],
                source_sheet_path=config['source_sheet_path'],
                colown_key_path_source=config.get('colown_key_path_source', 'Codesite'),
                target_key_column=config.get('target_key_column', ['Site Code', 'SITE_CODE', 'site code', 'Code Site']),
                target_value_column=config.get('target_value_column', ['Comment', 'COMMENT', 'comment']),
                result_position_column=config.get('result_position_column', 'last_column'),
                date_str=config['date_str'],
                reference_name=config.get('reference_name', ''),
                reference_date=config.get('reference_date', ''),
                target_sheet_name=config.get('target_sheet_name')
            )
            
            self.logger.info("Lecture des fichiers Excel...")
            
            # Exécuter le traitement avec la méthode correcte
            self.logger.info("Filtrage par date et exécution du XLOOKUP...")
            celldown.super_xlookup_par_date()  # Méthode utilisée dans test_global.py
            
            self.logger.success("✅ CellDown terminé avec succès !")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement CellDown : {str(e)}")
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
            return False, "Fichier cible CellDown introuvable"
        
        # Vérifier la feuille
        if not config.get('source_sheet_path'):
            return False, "Feuille source non spécifiée"
        
        # Vérifier la date
        if not config.get('date_str'):
            return False, "Date non spécifiée"
        
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
                config['source_sheet_path']
            )
            
            target_df = ExcelFileHandler.read_excel(
                config['target_file_path']
            )
            
            if source_df is None or target_df is None:
                return None
            
            # Trouver les colonnes clés
            source_key = config.get('colown_key_path_source', 'Codesite')
            target_key_options = config.get('target_key_column', ['Site Code', 'SITE_CODE'])
            
            # Trouver la colonne cible
            target_key = ExcelFileHandler.find_column_matches(target_df, target_key_options)
            
            if not target_key:
                return {
                    "error": "Colonne clé non trouvée dans le fichier cible",
                    "total_matches": 0
                }
            
            # Analyser les correspondances
            matches = ExcelFileHandler.analyze_matches(
                source_df, target_df,
                source_key, target_key
            )
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la prévisualisation : {str(e)}")
            return None
