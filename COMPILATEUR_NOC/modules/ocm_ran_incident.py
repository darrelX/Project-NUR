# ============================================================================
# modules/ocm_ran_incident.py - Module de compilation OCM RAN
# ============================================================================

import pandas as pd
import re
import streamlit as st
from io import BytesIO  # ← AJOUT

class OcmRanModule:
    """
    Module de compilation pour les fichiers OCM RAN INCIDENT.
    Lit la sheet 'ALL SITES DOWN', extrait 'Actions en cours',
    et ajoute une colonne avec la référence horaire.
    """

    def __init__(self):
        self.nom = "OCM RAN"

    def compiler(self, df_principal, fichiers_sources, col_code_principal, date_reference):
        df_resultat = df_principal.copy()

        for fichier_data in fichiers_sources:
            # CORRECTION : clé "binaire" + BytesIO
            contenu_binaire = fichier_data["binaire"]
            nom_fichier     = fichier_data["nom"]

            heure = self._extraire_heure(nom_fichier)

            try:
                df_sheet = pd.read_excel(BytesIO(contenu_binaire), sheet_name="ALL SITES DOWN")
            except:
                continue

            col_code_source = None
            for col in df_sheet.columns:
                if "site id" in str(col).lower() or "siteid" in str(col).lower():
                    col_code_source = col
                    break

            if col_code_source is None:
                continue

            col_actions = None
            for col in df_sheet.columns:
                if "actions en cours" in str(col).lower():
                    col_actions = col
                    break

            if col_actions is None:
                continue

            date_formatee = date_reference.replace("/", "-") if date_reference else ""
            nom_colonne = f"OCM Ran {date_formatee} {heure}"
            reference   = f"{{{date_reference} ocm ran {heure}}}"

            valeurs = []
            for idx, row in df_principal.iterrows():
                code_site = str(row[col_code_principal]).strip()
                ligne = df_sheet[df_sheet[col_code_source].astype(str).str.strip() == code_site]

                if not ligne.empty:
                    action_val = str(ligne.iloc[0][col_actions]) if pd.notna(ligne.iloc[0].get(col_actions)) else ""
                    valeur = f"{reference}: {action_val}" if action_val else ""
                else:
                    valeur = ""

                valeurs.append(valeur)

            df_resultat[nom_colonne] = valeurs

        return df_resultat

    def _extraire_heure(self, nom_fichier):
        match = re.search(r'(\d{1,2}H)', nom_fichier, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return "00H"