"""
Composant: Sélecteur de sheets avec cases à cocher
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path


class SheetSelector:
    """Composant pour sélectionner les sheets"""
    
    def __init__(self):
        """Initialiser le composant"""
        self.selected_sheets = {}
    
    def render(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Rendre le composant de sélection de sheets
        
        Args:
            file_paths: Chemins des fichiers
        
        Returns:
            Dictionnaire {fichier: [sheets sélectionnées]}
        """
        selected_sheets = {}
        
        for file_path in file_paths:
            try:
                # Lire les sheets disponibles
                path = Path(file_path)
                
                if path.suffix.lower() in ['.xlsx', '.xls']:
                    sheets = pd.ExcelFile(file_path).sheet_names
                    
                    st.write(f"📋 **{path.name}** - {len(sheets)} sheet(s)")
                    
                    # Cases à cocher pour chaque sheet
                    cols = st.columns(min(3, len(sheets)))
                    selected = []
                    
                    for idx, sheet in enumerate(sheets):
                        with cols[idx % len(cols)]:
                            if st.checkbox(sheet, value=True, key=f"{file_path}_{sheet}"):
                                selected.append(sheet)
                    
                    if selected:
                        selected_sheets[file_path] = selected
                    
                    st.divider()
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture de {path.name}: {str(e)}")
        
        self.selected_sheets = selected_sheets
        return selected_sheets
    
    def get_dataframe_from_sheet(self, file_path: str, sheet_name: str) -> Optional[pd.DataFrame]:
        """
        Obtenir un DataFrame d'une sheet spécifique
        
        Args:
            file_path: Chemin du fichier
            sheet_name: Nom de la sheet
        
        Returns:
            DataFrame ou None
        """
        try:
            path = Path(file_path)
            
            if path.suffix.lower() in ['.xlsx', '.xls']:
                return pd.read_excel(file_path, sheet_name=sheet_name)
            elif path.suffix.lower() == '.csv':
                return pd.read_csv(file_path)
            
        except Exception:
            return None
        
        return None
