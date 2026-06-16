"""
Composant: Aperçu des données avant/après
"""

import streamlit as st
import pandas as pd
from typing import Optional, Tuple


class PreviewTable:
    """Composant pour afficher un aperçu des données"""
    
    def __init__(self):
        """Initialiser le composant"""
        self.original_df = None
        self.processed_df = None
    
    def render(self, original_df: Optional[pd.DataFrame] = None, 
               processed_df: Optional[pd.DataFrame] = None,
               max_rows: int = 10) -> None:
        """
        Rendre le composant d'aperçu
        
        Args:
            original_df: DataFrame original
            processed_df: DataFrame traité
            max_rows: Nombre max de lignes à afficher
        """
        if original_df is None or original_df.empty:
            st.info("Aucun DataFrame à afficher")
            return
        
        self.original_df = original_df
        self.processed_df = processed_df
        
        # Onglets pour avant/après
        tab1, tab2 = st.tabs(["📊 Original", "✨ Traité"])
        
        with tab1:
            self._render_table("Données originales", original_df, max_rows)
        
        with tab2:
            if processed_df is not None:
                self._render_table("Données traitées", processed_df, max_rows)
            else:
                st.info("Pas de données traitées disponibles")
    
    def _render_table(self, title: str, df: pd.DataFrame, max_rows: int) -> None:
        """
        Rendre une table
        
        Args:
            title: Titre de la table
            df: DataFrame à afficher
            max_rows: Nombre max de lignes
        """
        st.write(f"**{title}**")
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lignes", len(df))
        with col2:
            st.metric("Colonnes", len(df.columns))
        with col3:
            st.metric("Mémoire", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
        
        # Aperçu du tableau
        st.dataframe(
            df.head(max_rows),
            use_container_width=True
        )
        
        # Détails des colonnes
        with st.expander("📋 Détails des colonnes"):
            col_info = pd.DataFrame({
                "Colonne": df.columns,
                "Type": df.dtypes.values,
                "Non-null": df.count().values,
                "Null": df.isnull().sum().values,
            })
            st.dataframe(col_info, use_container_width=True)
    
    def export_summary(self) -> dict:
        """
        Exporter un résumé
        
        Returns:
            Dictionnaire avec les statistiques
        """
        summary = {}
        
        if self.original_df is not None:
            summary["original"] = {
                "rows": len(self.original_df),
                "columns": len(self.original_df.columns),
                "memory_kb": self.original_df.memory_usage(deep=True).sum() / 1024
            }
        
        if self.processed_df is not None:
            summary["processed"] = {
                "rows": len(self.processed_df),
                "columns": len(self.processed_df.columns),
                "memory_kb": self.processed_df.memory_usage(deep=True).sum() / 1024
            }
        
        return summary
