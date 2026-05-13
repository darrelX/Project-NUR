"""
Service d'analyse de fichiers Excel pour l'interface Breakdown.
Extrait les métadonnées, colonnes, et détecte automatiquement les issues.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime, date


class ExcelAnalyzer:
    """Analyse les fichiers Excel pour extraire métadonnées et détecter les issues."""

    @staticmethod
    def _column_index_to_letter(idx: int) -> str:
        """Convertit un index de colonne (0-based) en lettre Excel."""
        result = ""
        idx += 1
        while idx > 0:
            idx, remainder = divmod(idx - 1, 26)
            result = chr(65 + remainder) + result
        return result

    @staticmethod
    def _make_json_serializable(val: Any) -> Any:
        """Convertit une valeur en type JSON-sérialisable."""
        # Gérer les valeurs NaN et inf
        if pd.isna(val) or (isinstance(val, float) and not np.isfinite(val)):
            return None
        
        # Gérer les types datetime
        if isinstance(val, (pd.Timestamp, datetime, date)):
            return val.isoformat()
        
        # Gérer les types numpy
        if isinstance(val, (np.integer, np.floating)):
            return val.item()
        
        # Gérer les types numpy bool
        if isinstance(val, np.bool_):
            return bool(val)
        
        # Si c'est déjà un type simple, le retourner
        return val

    @staticmethod
    def analyze_file(file_path: str) -> Dict[str, Any]:
        """
        Analyse complète d'un fichier Excel.
        
        Returns:
            {
                'fileName': str,
                'filePath': str,
                'sheets': List[str],
                'columns': Dict[sheet_name, List[ColumnInfo]],
                'preview': Dict[sheet_name, List[row_data]],
                'issues': List[PreviewItem] (optionnel)
            }
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Fichier introuvable: {file_path}")

        excel_file = pd.ExcelFile(file_path)
        sheets = excel_file.sheet_names

        metadata = {
            'fileName': Path(file_path).name,
            'filePath': file_path,
            'sheets': sheets,
            'columns': {},
            'preview': {},
        }

        # Analyser chaque feuille
        for sheet in sheets:
            df = pd.read_excel(file_path, sheet_name=sheet, nrows=10)
            
            # Extraire les colonnes avec détails
            columns = []
            for idx, col_name in enumerate(df.columns):
                # Convertir les valeurs d'exemple en liste et les rendre JSON-sérialisables
                sample_values = df[col_name].head(3).tolist()
                clean_samples = [ExcelAnalyzer._make_json_serializable(val) for val in sample_values]
                
                col_info = {
                    'name': str(col_name),
                    'letter': ExcelAnalyzer._column_index_to_letter(idx),
                    'index': idx,
                    'type': str(df[col_name].dtype),
                    'sampleValues': clean_samples
                }
                columns.append(col_info)
            
            metadata['columns'][sheet] = columns
            
            # Aperçu des données (5 premières lignes) - convertir TOUT en JSON-sérialisable
            preview_df = df.head(5)
            preview_data = []
            for _, row in preview_df.iterrows():
                row_dict = {}
                for col in preview_df.columns:
                    # Convertir le nom de colonne ET la valeur en JSON-sérialisable
                    col_key = ExcelAnalyzer._make_json_serializable(col)
                    col_value = ExcelAnalyzer._make_json_serializable(row[col])
                    row_dict[col_key] = col_value
                preview_data.append(row_dict)
            metadata['preview'][sheet] = preview_data

        return metadata

    @staticmethod
    def detect_issues(file_path: str, sheet_name: str) -> List[Dict[str, str]]:
        """
        Détecte automatiquement les issues/problèmes dans une feuille Excel.
        
        Recherche des patterns communs :
        - Mots-clés comme "cell down", "panne", "erreur", "timeout"
        - Cellules vides dans certaines colonnes
        - Valeurs anormales
        
        Returns:
            Liste de PreviewItem: [{'id': str, 'label': str}, ...]
        """
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        issues = []
        issue_id = 1

        # Patterns de mots-clés à rechercher
        keywords = [
            r'cell\s*down',
            r'panne',
            r'erreur',
            r'timeout',
            r'dépassement',
            r'failure',
            r'error',
            r'down',
            r'corrupted',
            r'invalid',
            r'missing',
            r'anomalie',
            r'défaillant',
        ]

        # Chercher dans toutes les colonnes textuelles
        for col in df.columns:
            if df[col].dtype == 'object':  # Colonnes textuelles
                for keyword in keywords:
                    matches = df[col].astype(str).str.contains(keyword, case=False, regex=True, na=False)
                    if matches.any():
                        matched_values = df[matches][col].unique()[:3]  # Max 3 exemples
                        for val in matched_values:
                            label = str(val)[:50]  # Tronquer si trop long
                            issues.append({
                                'id': f'issue_{issue_id}',
                                'label': label
                            })
                            issue_id += 1

        # Si aucune issue détectée, créer des issues génériques basées sur les lignes
        if not issues and len(df) > 0:
            # Prendre les 5 premières lignes comme exemples d'issues
            for idx in range(min(5, len(df))):
                row = df.iloc[idx]
                # Créer un label à partir de la première colonne textuelle
                label = None
                for col in df.columns:
                    if df[col].dtype == 'object' and pd.notna(row[col]):
                        label = f"{col}: {str(row[col])[:40]}"
                        break
                
                if not label:
                    label = f"Ligne {idx + 1}"
                
                issues.append({
                    'id': f'row_{idx + 1}',
                    'label': label
                })

        return issues

    @staticmethod
    def get_sheet_columns(file_path: str, sheet_name: str) -> List[Dict[str, Any]]:
        """Récupère les colonnes détaillées d'une feuille spécifique."""
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
        
        columns = []
        for idx, col_name in enumerate(df.columns):
            col_info = {
                'name': str(col_name),
                'letter': ExcelAnalyzer._column_index_to_letter(idx),
                'index': idx,
                'type': str(df[col_name].dtype),
                'sampleValues': df[col_name].dropna().head(3).tolist()
            }
            columns.append(col_info)
        
        return columns

    @staticmethod
    def get_sheet_preview(file_path: str, sheet_name: str, rows: int = 10) -> List[Dict]:
        """Récupère un aperçu des données d'une feuille."""
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=rows)
        return df.to_dict('records')


# =============================================================================
# TESTS
# =============================================================================
if __name__ == "__main__":
    # Test avec un fichier exemple
    test_file = r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx"
    
    if Path(test_file).exists():
        print("=" * 60)
        print("TEST: Analyse complète du fichier")
        print("=" * 60)
        
        metadata = ExcelAnalyzer.analyze_file(test_file)
        print(f"\nFichier: {metadata['fileName']}")
        print(f"Feuilles: {metadata['sheets']}")
        
        for sheet, columns in metadata['columns'].items():
            print(f"\nFeuille '{sheet}':")
            for col in columns:
                print(f"  - {col['letter']}: {col['name']} (type: {col['type']})")
        
        print("\n" + "=" * 60)
        print("TEST: Détection d'issues")
        print("=" * 60)
        
        for sheet in metadata['sheets']:
            issues = ExcelAnalyzer.detect_issues(test_file, sheet)
            print(f"\nFeuille '{sheet}': {len(issues)} issues détectées")
            for issue in issues[:5]:  # Afficher max 5
                print(f"  - {issue['id']}: {issue['label']}")
    else:
        print(f"❌ Fichier de test introuvable: {test_file}")
