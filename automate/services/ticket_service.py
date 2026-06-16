"""
Service pour le traitement Ticket
Wrapper autour de la classe Ticket existante
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import streamlit as st

# Ajouter le dossier parent au path pour importer ticket
sys.path.insert(0, str(Path(__file__).parent.parent))

from ticket import Ticket
from utils.logger import Logger


class TicketService:
    """Service pour exécuter le traitement Ticket"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
    
    def execute(self, config: Dict[str, Any]) -> bool:
        """
        Exécute le traitement Ticket avec la configuration fournie
        
        Args:
            config: Dictionnaire de configuration avec les paramètres
                   
        Returns:
            bool: True si succès, False sinon
        """
        try:
            self.logger.info("Démarrage du traitement Ticket...")
            
            # Debug: afficher tous les paramètres reçus
            self.logger.info(f"=== DEBUG TICKET: Config reçue ===")
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
            
            # Créer l'instance Ticket
            self.logger.info(f"Fichier source : {config['source_file_path']}")
            self.logger.info(f"Fichier cible : {config['target_file_path']}")
            
            ticket = Ticket(
                source_file_path=config['source_file_path'],
                target_file_path=config['target_file_path'],
                source_sheet_name=config['source_sheet_name'],
                source_key_column=config.get('source_key_column', 'Codesite'),
                result_position_column=config.get('result_position_column', 'last_column'),
                result_column_name=config.get('result_column_name', 'Ticket'),
                reference_name=config.get('reference_name', 'Ticket'),
                target_join_columns=config.get('target_join_columns', [
                    ["Ticket ID", "Ticket ID(Create TT)"],
                    ["Description", "Description(Process TT)"],
                    ["Solution", "Solution(Process TT)"],
                    ["Root Cause", "Root Cause(Process TT)"],
                    ["Incident Reason", "Incident Reason Detail(Process TT)"]
                ]),
                join_separator=config.get('join_separator', '..'),
                ignore_empty=config.get('ignore_empty', True),
                extract_source_column=config.get('extract_source_column', ["Site Name", "Site ID", "SITE_ID", "site id", "site_code", "site code"]),
                target_sheet_name=config.get('target_sheet_name', '')
            )
            
            self.logger.info("Suppression des filtres Excel...")
            if config.get('source_sheet_name'):
                Ticket._remove_auto_filters(config['source_file_path'], config['source_sheet_name'])
            Ticket._remove_auto_filters(config['target_file_path'])
            
            self.logger.info("Exécution du traitement Ticket...")
            ticket.run()
            
            self.logger.success("✅ Ticket terminé avec succès !")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement Ticket : {str(e)}")
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
            return False, "Fichier cible Ticket introuvable"
        
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
            
            target_df = ExcelFileHandler.read_excel(
                config['target_file_path']
            )
            
            if source_df is None or target_df is None:
                return None
            
            # Pour Ticket, on ne peut pas facilement prévisualiser
            # car la clé est extraite dynamiquement
            # On retourne des stats basiques
            
            return {
                "source_total": len(source_df),
                "target_total": len(target_df),
                "total_matches": "N/A (extraction dynamique)",
                "match_rate": "N/A"
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la prévisualisation : {str(e)}")
            return None
