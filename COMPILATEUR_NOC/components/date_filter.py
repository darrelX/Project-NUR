"""
Composant: Filtre par date avec détection auto
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple
from utils import detect_date_column, parse_date


class DateFilter:
    """Composant pour filtrer par date"""
    
    def __init__(self):
        """Initialiser le composant"""
        self.date_column = None
        self.min_date = None
        self.max_date = None
    
    def render(self, df: Optional[pd.DataFrame] = None) -> Optional[Tuple[datetime, datetime]]:
        """
        Rendre le composant de filtrage par date
        
        Args:
            df: DataFrame pour détection auto (optionnel)
        
        Returns:
            Tuple (date_min, date_max) ou None
        """
        col1, col2 = st.columns(2)
        
        with col1:
            # Détection auto
            auto_detect = st.checkbox("Détection automatique", value=True)
            
            if auto_detect and df is not None:
                self.date_column = detect_date_column(df)
                if self.date_column:
                    st.info(f"📅 Colonne détectée: **{self.date_column}**")
            else:
                # Sélection manuelle
                if df is not None:
                    self.date_column = st.selectbox(
                        "Sélectionnez la colonne date",
                        options=df.columns.tolist()
                    )
        
        with col2:
            # Plage de dates
            if df is not None and self.date_column:
                date_range = st.slider(
                    "Plage de dates",
                    min_value=datetime.now() - timedelta(days=365),
                    max_value=datetime.now(),
                    value=(
                        datetime.now() - timedelta(days=30),
                        datetime.now()
                    )
                )
                return date_range
        
        return None
    
    def apply_filter(self, df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Appliquer le filtre de date
        
        Args:
            df: DataFrame à filtrer
            start_date: Date de début
            end_date: Date de fin
        
        Returns:
            DataFrame filtré
        """
        if self.date_column is None or self.date_column not in df.columns:
            return df
        
        # Convertir la colonne en datetime
        try:
            df[self.date_column] = pd.to_datetime(df[self.date_column])
        except Exception:
            return df
        
        # Appliquer le filtre
        mask = (df[self.date_column] >= start_date) & (df[self.date_column] <= end_date)
        return df[mask]
