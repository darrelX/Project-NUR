# ============================================================================
# modules/dashboard_cell.py - Module de compilation Dashbord Cell
# ============================================================================

import pandas as pd
import streamlit as st
import re
from io import BytesIO  # ← AJOUT

class DashboardCellModule:
    """
    Module de compilation pour les fichiers Dashbord Cell.
    Lit la sheet 'TOP OFF XXXX', extrait 'Comment',
    et ajoute une colonne avec la référence {date dashboard_cell}:.
    """

    def __init__(self):
        self.nom = "Dashbord Cell"

    def compiler(self, df_principal, fichiers_sources, col_code_principal, date_reference):
        df_resultat = df_principal.copy()

        if "Dashbord suivi TOP OFFENDERS" not in df_resultat.columns:
            df_resultat["Dashbord suivi TOP OFFENDERS"] = ""

        for fichier_data in fichiers_sources:
            # CORRECTION : clé "binaire" + BytesIO
            contenu_binaire = fichier_data["binaire"]

            # CORRECTION : _trouver_sheet_top_off reçoit BytesIO
            sheet_name = self._trouver_sheet_top_off(BytesIO(contenu_binaire))
            if sheet_name is None:
                continue

            df_sheet = pd.read_excel(BytesIO(contenu_binaire), sheet_name=sheet_name)

            col_code_source = self._trouver_colonne(df_sheet, [
                "code site", "site code", "code id"
            ])
            col_comment = self._trouver_colonne(df_sheet, [
                "comment", "commentaire"
            ])

            if col_code_source is None or col_comment is None:
                continue

            reference = f"{{{date_reference} dashboard_cell}}"

            for idx, row in df_resultat.iterrows():
                code_site = str(row[col_code_principal]).strip()
                ligne = df_sheet[df_sheet[col_code_source].astype(str).str.strip() == code_site]

                if not ligne.empty:
                    comment_val = str(ligne.iloc[0][col_comment]) if pd.notna(ligne.iloc[0].get(col_comment)) else ""

                    if comment_val:
                        valeur = f"{reference}: {comment_val}"
                        if df_resultat.at[idx, "Dashbord suivi TOP OFFENDERS"] and valeur:
                            df_resultat.at[idx, "Dashbord suivi TOP OFFENDERS"] += " || " + valeur
                        elif valeur:
                            df_resultat.at[idx, "Dashbord suivi TOP OFFENDERS"] = valeur

        return df_resultat

    def _trouver_sheet_top_off(self, fichier_bytesio):
        # CORRECTION : reçoit un BytesIO
        xl = pd.ExcelFile(fichier_bytesio)
        sheets_top_off = []
        for sheet in xl.sheet_names:
            if sheet.upper().startswith("TOP OFF"):
                match = re.search(r'TOP OFF\s*(\d+)', sheet, re.IGNORECASE)
                if match:
                    sheets_top_off.append((int(match.group(1)), sheet))
        if not sheets_top_off:
            return None
        sheets_top_off.sort(key=lambda x: x[0], reverse=True)
        return sheets_top_off[0][1]

    def _trouver_colonne(self, df, mots_cles):
        for col in df.columns:
            for mot in mots_cles:
                if mot.lower() in str(col).lower():
                    return col
        return None