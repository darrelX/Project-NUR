"""
Composant: Sélecteur de colonnes à extraire
"""

import streamlit as st
import pandas as pd
from typing import List, Optional


class ColumnSelector:
    """Composant pour sélectionner les colonnes"""
    
    def __init__(self):
        """Initialiser le composant"""
        self.selected_columns = []
    
    def render(self, df: Optional[pd.DataFrame] = None) -> List[str]:
        """
        Rendre le composant de sélection de colonnes
        
        Args:
            df: DataFrame pour récupérer les colonnes
        
        Returns:
            Liste des colonnes sélectionnées
        """
        if df is None or df.empty:
            st.info("Aucun DataFrame disponible")
            return []
        
        # Mode de sélection
        mode = st.radio(
            "Mode de sélection",
            ["Toutes les colonnes", "Colonnes spécifiques"],
            horizontal=True
        )
        
        if mode == "Toutes les colonnes":
            self.selected_columns = df.columns.tolist()
        else:
            # Sélection multi-colonnes
            self.selected_columns = st.multiselect(
                "Sélectionnez les colonnes à extraire",
                options=df.columns.tolist(),
                default=df.columns.tolist()
            )
        
        st.info(f"✅ {len(self.selected_columns)} colonne(s) sélectionnée(s)")
        
        return self.selected_columns
    
    def apply_selection(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Appliquer la sélection de colonnes
        
        Args:
            df: DataFrame source
        
        Returns:
            DataFrame avec les colonnes sélectionnées
        """
        if not self.selected_columns:
            return df
        
        # Filtrer les colonnes existantes
        available_cols = [col for col in self.selected_columns if col in df.columns]
        
        return df[available_cols] if available_cols else df
    
    def get_summary(self) -> dict:
        """
        Obtenir un résumé de la sélection
        
        Returns:
            Dictionnaire avec les informations
        """
        return {
            "count": len(self.selected_columns),
            "columns": self.selected_columns
        }
