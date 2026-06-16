# ============================================================================
# modules/top_offenders.py - Module de compilation Top Offenders
# ============================================================================

import pandas as pd
import streamlit as st
from io import BytesIO  # ← AJOUT

class TopOffendersModule:
    """
    Module de compilation pour les fichiers Top Offenders.
    Lit la sheet 'ALL', extrait 'Comment',
    et ajoute une colonne avec la référence {date top offenders}:.
    """

    def __init__(self):
        self.nom = "Top Offenders"

    def compiler(self, df_principal, fichiers_sources, col_code_principal, date_reference):
        df_resultat = df_principal.copy()

        if "top offenders" not in df_resultat.columns:
            df_resultat["top offenders"] = ""

        for fichier_data in fichiers_sources:
            # CORRECTION : clé "binaire" + BytesIO
            contenu_binaire = fichier_data["binaire"]

            try:
                df_sheet = pd.read_excel(BytesIO(contenu_binaire), sheet_name="ALL")
            except:
                continue

            col_code_source = self._trouver_colonne(df_sheet, [
                "code site", "site code", "code id"
            ])
            col_comment = self._trouver_colonne(df_sheet, [
                "comment", "commentaire"
            ])

            if col_code_source is None or col_comment is None:
                continue

            reference = f"{{{date_reference} top offenders}}"
            
            st.info(f"✅ Top Offenders: {len(df_sheet)} lignes lues")
            matches_count = 0
            for idx, row in df_resultat.iterrows():
                code_site = str(row[col_code_principal]).strip().upper()
                ligne = df_sheet[df_sheet[col_code_source].astype(str).str.strip().str.upper() == code_site]

                if not ligne.empty:
                    comment_val = str(ligne.iloc[0][col_comment]) if pd.notna(ligne.iloc[0].get(col_comment)) else ""

                    if comment_val:
                        matches_count += 1
                        valeur = f"{reference}: {comment_val}"
                        if df_resultat.at[idx, "top offenders"] and valeur:
                            df_resultat.at[idx, "top offenders"] += " " + valeur
                        elif valeur:
                            df_resultat.at[idx, "top offenders"] = valeur
            
            st.success(f"✅ {matches_count} codes sites Top Offenders trouvés")

        return df_resultat

    def _trouver_colonne(self, df, mots_cles):
        for col in df.columns:
            for mot in mots_cles:
                if mot.lower() in str(col).lower():
                    return col
        return None