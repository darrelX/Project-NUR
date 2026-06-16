# ============================================================================
# modules/hourly_ihs.py - Module de compilation Hourly IHS
# ============================================================================

import pandas as pd
import streamlit as st
from io import BytesIO

class HourlyIhsModule:
    """
    Module de compilation pour les fichiers Hourly IHS.
    1. Lit la sheet 'hourly-ihs'
    2. Cherche les colonnes: Event time (ou Time Fault Occurred), Duration, CMS, Last Timeline Message
    3. Concatène avec '..'
    4. Référence: (hourly IHS): (sans date)
    5. XLOOKUP par code site
    """

    COLONNES_A_CHERCHER = {
        "event_time": ["event time", "time fault occurred"],
        "duration": ["duration"],
        "cms": ["cms"],
        "last_message": ["last timeline message", "last message", "timeline message"]
    }
    SEPARATEUR = ".."

    def __init__(self):
        self.nom = "Hourly IHS"

    def compiler(self, df_principal, fichiers_sources, col_code_principal, date_reference=None):
        df_resultat = df_principal.copy()

        if "Hourly IHS" not in df_resultat.columns:
            df_resultat["Hourly IHS"] = ""

        for fichier_data in fichiers_sources:
            contenu_binaire = fichier_data["binaire"]
            nom_fichier = fichier_data["nom"]

            try:
                df_sheet = pd.read_excel(BytesIO(contenu_binaire), sheet_name="hourly-ihs")
            except Exception as e:
                st.warning(f"⚠️ Hourly IHS {nom_fichier}: sheet 'hourly-ihs' non trouvée ou erreur: {str(e)}")
                continue

            # Chercher colonne code site
            col_code_source = self._trouver_colonne(df_sheet, [
                "site code", "code site", "code id", "site id", "tenant id", "tenant"
            ])
            if col_code_source is None:
                st.warning(f"⚠️ Hourly IHS {nom_fichier}: colonne 'Code Site' non trouvée. Colonnes disponibles: {list(df_sheet.columns)}")
                continue

            # Chercher les 4 colonnes nécessaires
            col_event_time   = self._trouver_colonne(df_sheet, self.COLONNES_A_CHERCHER["event_time"])
            col_duration     = self._trouver_colonne(df_sheet, self.COLONNES_A_CHERCHER["duration"])
            col_cms          = self._trouver_colonne(df_sheet, self.COLONNES_A_CHERCHER["cms"])
            col_last_message = self._trouver_colonne(df_sheet, self.COLONNES_A_CHERCHER["last_message"])

            # Afficher les colonnes trouvées
            colonnes_trouvees = []
            if col_event_time:
                colonnes_trouvees.append(f"Event Time: {col_event_time}")
            if col_duration:
                colonnes_trouvees.append(f"Duration: {col_duration}")
            if col_cms:
                colonnes_trouvees.append(f"CMS: {col_cms}")
            if col_last_message:
                colonnes_trouvees.append(f"Last Message: {col_last_message}")

            if colonnes_trouvees:
                st.info(f"✅ Hourly IHS {nom_fichier}: Colonnes trouvées: {', '.join(colonnes_trouvees)}")
            else:
                st.warning(f"⚠️ Hourly IHS {nom_fichier}: Colonnes manquantes. Disponibles: {list(df_sheet.columns)}")
                continue

            # XLOOKUP : pour chaque site du fichier principal
            matches_count = 0
            for idx, row in df_resultat.iterrows():
                code_site = str(row[col_code_principal]).strip()
                ligne = df_sheet[df_sheet[col_code_source].astype(str).str.strip() == code_site]

                if not ligne.empty:
                    # Récupérer les valeurs
                    event_time   = str(ligne.iloc[0][col_event_time]).strip() if col_event_time and pd.notna(ligne.iloc[0].get(col_event_time)) else ""
                    duration     = str(ligne.iloc[0][col_duration]).strip()   if col_duration and pd.notna(ligne.iloc[0].get(col_duration)) else ""
                    cms          = str(ligne.iloc[0][col_cms]).strip()        if col_cms and pd.notna(ligne.iloc[0].get(col_cms)) else ""
                    last_message = str(ligne.iloc[0][col_last_message]).strip() if col_last_message and pd.notna(ligne.iloc[0].get(col_last_message)) else ""

                    # Concaténer avec ".."
                    valeurs = []
                    if event_time and event_time.upper() != "NAN":
                        valeurs.append(event_time)
                    if duration and duration.upper() != "NAN":
                        valeurs.append(duration)
                    if cms and cms.upper() != "NAN":
                        valeurs.append(cms)
                    if last_message and last_message.upper() != "NAN":
                        valeurs.append(last_message)

                    if valeurs:
                        valeur_regroupee = self.SEPARATEUR.join(valeurs)
                        valeur_complete = f"(hourly IHS): {valeur_regroupee}"
                        
                        matches_count += 1
                        if df_resultat.at[idx, "Hourly IHS"] and valeur_complete:
                            df_resultat.at[idx, "Hourly IHS"] += " || " + valeur_complete
                        else:
                            df_resultat.at[idx, "Hourly IHS"] = valeur_complete

            st.success(f"✅ {matches_count} codes sites Hourly IHS trouvés et introduits")

        return df_resultat

        return df_resultat

    def _trouver_colonne(self, df, mots_cles):
        for col in df.columns:
            for mot in mots_cles:
                if mot.lower() in str(col).lower():
                    return col
        return None