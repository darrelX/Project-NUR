"""
Fonctions utilitaires du compilateur NOC
🔧 XLOOKUP, détection de dates, parsing, etc.
"""

import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# ============================================================================
# utils.py
# ============================================================================

import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)  # Cache valable 1 heure
def lire_fichier_excel(fichier):
    """Lit un fichier Excel et retourne son contenu. Avec cache."""
    return pd.read_excel(fichier, sheet_name=None)

@st.cache_data(ttl=3600)

def lire_sheet_specifique(fichier, sheet_name):
    """Lit une sheet spécifique d'un fichier Excel. Avec cache."""
    return pd.read_excel(fichier, sheet_name=sheet_name)

def xlookup(lookup_value, lookup_array, return_array, if_not_found="N/A"):
    """
    Simulation de la fonction XLOOKUP d'Excel
    
    Args:
        lookup_value: Valeur à chercher
        lookup_array: Colonne de recherche
        return_array: Colonne de retour
        if_not_found: Valeur par défaut si pas trouvée
    
    Returns:
        Valeur trouvée ou valeur par défaut
    """
    try:
        idx = lookup_array.tolist().index(lookup_value)
        return return_array.iloc[idx]
    except (ValueError, IndexError):
        return if_not_found


def detect_date_column(df: pd.DataFrame) -> Optional[str]:
    """
    Détecte automatiquement la colonne de date
    
    Args:
        df: DataFrame à analyser
    
    Returns:
        Nom de la colonne de date ou None
    """
    date_patterns = [
        r'date', r'day', r'jour', r'time', r'datetime',
        r'timestamp', r'heure', r'time_period'
    ]
    
    for col in df.columns:
        col_lower = col.lower()
        if any(re.search(pattern, col_lower) for pattern in date_patterns):
            return col
    
    return None


def parse_date(date_string: str, formats: List[str] = None) -> Optional[datetime]:
    """
    Parse une chaîne de date avec plusieurs formats
    
    Args:
        date_string: Chaîne à parser
        formats: Formats de date à essayer
    
    Returns:
        Objet datetime ou None
    """
    if formats is None:
        formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d",
            "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_string).strip(), fmt)
        except ValueError:
            continue
    
    return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie un DataFrame (supprime espaces, NaN, etc.)
    
    Args:
        df: DataFrame à nettoyer
    
    Returns:
        DataFrame nettoyé
    """
    # Supprimer les espaces dans les noms de colonnes
    df.columns = df.columns.str.strip()
    
    # Supprimer les lignes complètement vides
    df = df.dropna(how='all')
    
    return df


def merge_dataframes(dfs: List[pd.DataFrame], on: str = None, how: str = 'outer') -> pd.DataFrame:
    """
    Fusionne plusieurs DataFrames
    
    Args:
        dfs: Liste de DataFrames à fusionner
        on: Colonne sur laquelle fusionner
        how: Type de fusion ('outer', 'inner', 'left', 'right')
    
    Returns:
        DataFrame fusionné
    """
    if not dfs:
        return pd.DataFrame()
    
    result = dfs[0]
    for df in dfs[1:]:
        if on:
            result = pd.merge(result, df, on=on, how=how)
        else:
            result = pd.concat([result, df], ignore_index=True)
    
    return result


def export_to_excel(df: pd.DataFrame, filepath: str, sheet_name: str = "Sheet1"):
    """
    Exporte un DataFrame vers Excel
    
    Args:
        df: DataFrame à exporter
        filepath: Chemin du fichier
        sheet_name: Nom de la feuille
    """
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def validate_dataframe(df: pd.DataFrame, required_columns: List[str] = None) -> bool:
    """
    Valide un DataFrame
    
    Args:
        df: DataFrame à valider
        required_columns: Colonnes obligatoires
    
    Returns:
        True si valide, False sinon
    """
    if df.empty:
        return False
    
    if required_columns:
        return all(col in df.columns for col in required_columns)
    
    return True
