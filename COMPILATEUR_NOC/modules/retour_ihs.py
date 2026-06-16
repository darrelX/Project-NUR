# ============================================================================
# modules/retour_ihs.py - Module de compilation Retour IHS
# ============================================================================

import pandas as pd
import streamlit as st
from io import BytesIO  # ← AJOUT

class RetourIhsModule:
    """
    Module de compilation pour les fichiers Retour IHS.
    Lit la sheet 'ALL', extrait 'Owner',
    et ajoute une colonne avec la référence {date retour IHS}:.
    """

    def __init__(self):
        self.nom = "Retour IHS"

    def compiler(self, df_principal, fichiers_sources, col_code_principal, date_reference):
        df_resultat = df_principal.copy()

        if "RETOUR IHS" not in df_resultat.columns:
            df_resultat["RETOUR IHS"] = ""

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
            col_owner = self._trouver_colonne(df_sheet, ["owner"])

            if col_code_source is None or col_owner is None:
                continue

            reference = f"{{{date_reference} retour IHS}}"
            
            st.info(f"✅ Retour IHS: {len(df_sheet)} lignes lues")
            matches_count = 0
            for idx, row in df_resultat.iterrows():
                code_site = str(row[col_code_principal]).strip().upper()
                ligne = df_sheet[df_sheet[col_code_source].astype(str).str.strip().str.upper() == code_site]

                if not ligne.empty:
                    owner_val = str(ligne.iloc[0][col_owner]) if pd.notna(ligne.iloc[0].get(col_owner)) else ""

                    if owner_val:
                        matches_count += 1
                        valeur = f"{reference}: {owner_val}"
                        if df_resultat.at[idx, "RETOUR IHS"] and valeur:
                            df_resultat.at[idx, "RETOUR IHS"] += " " + valeur
                        elif valeur:
                            df_resultat.at[idx, "RETOUR IHS"] = valeur
            
            st.success(f"✅ {matches_count} codes sites Retour IHS trouvés")

        return df_resultat

    def _trouver_colonne(self, df, mots_cles):
        for col in df.columns:
            for mot in mots_cles:
                if mot.lower() in str(col).lower():
                    return col
        return None