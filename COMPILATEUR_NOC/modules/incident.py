# ============================================================================
# modules/incident.py - Module de compilation INCIDENT
# ============================================================================

import pandas as pd
import streamlit as st
from io import BytesIO  # ← AJOUT : nécessaire pour lire le binaire en mémoire

class IncidentModule:
    """
    Module de compilation pour les fichiers INCIDENT.
    Extrait les informations de la colonne 'root cause' vers la colonne 'INCIDENT'.
    """

    def __init__(self):
        self.nom = "INCIDENT"

    def compiler(self, df_principal, fichiers_sources, col_code_principal, date_reference):
        """
        Compile les données INCIDENT dans le fichier principal.
        
        fichiers_sources : liste de dicts {"binaire": bytes, "nom": str}
        """
        df_resultat = df_principal.copy()

        # Initialiser la colonne INCIDENT si elle n'existe pas
        if "INCIDENT" not in df_resultat.columns:
            df_resultat["INCIDENT"] = ""

        for fichier_data in fichiers_sources:

            # CORRECTION : la clé est "binaire" (bytes), pas "fichier" (objet fichier)
            contenu_binaire = fichier_data["binaire"]
            nom_fichier     = fichier_data["nom"]

            # Récupérer les sheets sélectionnées pour ce fichier
            config_key = "config_incident"
            sheets_selectionnees = st.session_state.get(config_key, {}).get(nom_fichier, [])

            if not sheets_selectionnees:
                continue

            for sheet_name in sheets_selectionnees:

                # CORRECTION : envelopper le binaire dans BytesIO avant read_excel
                df_sheet = pd.read_excel(BytesIO(contenu_binaire), sheet_name=sheet_name)

                # Trouver la colonne Code site dans la sheet source
                col_code_source = None
                for col in df_sheet.columns:
                    if "code site" in str(col).lower() or "site code" in str(col).lower():
                        col_code_source = col
                        break

                if col_code_source is None:
                    continue

                # Trouver la colonne root cause
                col_root_cause = None
                for col in df_sheet.columns:
                    if "root cause" in str(col).lower():
                        col_root_cause = col
                        break

                if col_root_cause is None:
                    continue

                # XLOOKUP : pour chaque site du fichier principal
                for idx, row in df_resultat.iterrows():
                    code_site = str(row[col_code_principal]).strip()

                    # Chercher dans la sheet source
                    ligne = df_sheet[
                        df_sheet[col_code_source].astype(str).str.strip() == code_site
                    ]

                    if not ligne.empty:
                        valeur_raw = ligne.iloc[0][col_root_cause]
                        valeur = str(valeur_raw) if pd.notna(valeur_raw) else ""

                        # Si la cellule est déjà remplie, ajouter après un séparateur
                        if df_resultat.at[idx, "INCIDENT"] and valeur:
                            df_resultat.at[idx, "INCIDENT"] += " | " + valeur
                        elif valeur:
                            df_resultat.at[idx, "INCIDENT"] = valeur

        return df_resultat