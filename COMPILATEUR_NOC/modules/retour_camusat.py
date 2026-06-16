# ============================================================================
# modules/retour_camusat.py - Module de compilation Retour CAMUSAT
# ============================================================================

import pandas as pd
import re
import streamlit as st
from io import BytesIO  # ← AJOUT

class RetourCamusatModule:
    """
    Module de compilation pour les fichiers Retour CAMUSAT.
    Lit la sheet 'Inputs_XX-XX', extrait 'CAMUSAT Feedback',
    et ajoute une colonne avec la référence {date retour CAMUSAT}:.
    """

    def __init__(self):
        self.nom = "Retour CAMUSAT"

    def compiler(self, df_principal, fichiers_sources, col_code_principal, date_reference):
        df_resultat = df_principal.copy()

        if "RETOUR CAMUSAT" not in df_resultat.columns:
            df_resultat["RETOUR CAMUSAT"] = ""

        for fichier_data in fichiers_sources:
            # CORRECTION : clé "binaire" + BytesIO
            contenu_binaire = fichier_data["binaire"]

            # CORRECTION : pd.ExcelFile reçoit BytesIO, pas des bytes bruts
            sheet_name = self._trouver_sheet_inputs(BytesIO(contenu_binaire))
            if sheet_name is None:
                continue

            df_sheet = pd.read_excel(BytesIO(contenu_binaire), sheet_name=sheet_name)

            col_code_source = self._trouver_colonne(df_sheet, [
                "code site", "site code", "code id"
            ])
            col_feedback = self._trouver_colonne(df_sheet, [
                "camusat feedback", "feedback"
            ])

            if col_code_source is None or col_feedback is None:
                continue

            reference = f"{{{date_reference} retour CAMUSAT}}"
            
            st.info(f"✅ Retour CAMUSAT: {len(df_sheet)} lignes lues")
            matches_count = 0
            for idx, row in df_resultat.iterrows():
                code_site = str(row[col_code_principal]).strip().upper()
                ligne = df_sheet[df_sheet[col_code_source].astype(str).str.strip().str.upper() == code_site]

                if not ligne.empty:
                    feedback_val = str(ligne.iloc[0][col_feedback]) if pd.notna(ligne.iloc[0].get(col_feedback)) else ""

                    if feedback_val:
                        matches_count += 1
                        valeur = f"{reference}: {feedback_val}"
                        if df_resultat.at[idx, "RETOUR CAMUSAT"] and valeur:
                            df_resultat.at[idx, "RETOUR CAMUSAT"] += " " + valeur
                        elif valeur:
                            df_resultat.at[idx, "RETOUR CAMUSAT"] = valeur
            
            st.success(f"✅ {matches_count} codes sites Retour CAMUSAT trouvés")

        return df_resultat

    def _trouver_sheet_inputs(self, fichier_bytesio):
        # CORRECTION : reçoit un BytesIO (réutilisable)
        xl = pd.ExcelFile(fichier_bytesio)
        for sheet in xl.sheet_names:
            if sheet.lower().startswith("inputs_"):
                return sheet
        return None

    def _trouver_colonne(self, df, mots_cles):
        for col in df.columns:
            for mot in mots_cles:
                if mot.lower() in str(col).lower():
                    return col
        return None