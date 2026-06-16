# ============================================================================
# modules/cells_down.py - Module de compilation Cells DOWN
# ============================================================================

import pandas as pd
import streamlit as st
from io import BytesIO  # ← AJOUT

class CellsDownModule:
    """
    Module de compilation pour les fichiers Cells DOWN.
    Extrait les colonnes Comment et Action Plan des sheets filtrées par date.
    """

    def __init__(self):
        self.nom = "Cells DOWN"

    def compiler(self, df_principal, fichiers_sources, col_code_principal, date_reference):
        df_resultat = df_principal.copy()

        for fichier_data in fichiers_sources:
            # CORRECTION : clé "binaire" + BytesIO
            contenu_binaire = fichier_data["binaire"]
            nom_fichier     = fichier_data["nom"]

            type_ref = self._determiner_type_reference(nom_fichier)

            config_key = "config_cells_down"
            sheets_selectionnees = st.session_state.get(config_key, {}).get(nom_fichier, [])

            if not sheets_selectionnees:
                continue

            date_ref = self._formater_date_reference(date_reference)

            for sheet_name in sheets_selectionnees:
                # Gestion .xlsx et .xlsb
                try:
                    if nom_fichier.lower().endswith(".xlsb"):
                        # Pour les fichiers .xlsb
                        try:
                            import pyxlsb
                        except ImportError:
                            st.error("❌ Module pyxlsb non installé. Installez-le avec: pip install pyxlsb")
                            continue
                        
                        fichier_bytes = BytesIO(contenu_binaire)
                        workbook = pyxlsb.open_workbook(fichier_bytes)
                        
                        # workbook.sheets retourne une liste de noms (strings)
                        # Vérifier si la sheet existe
                        if sheet_name not in workbook.sheets:
                            st.warning(f"⚠️ Sheet '{sheet_name}' non trouvée dans {nom_fichier}. Sheets disponibles: {workbook.sheets}")
                            continue
                        
                        # Obtenir la sheet et la convertir en DataFrame
                        sheet = workbook.get_sheet(sheet_name)
                        # Lire la première ligne comme headers (sheet.rows est une méthode)
                        rows = list(sheet.rows())
                        if not rows:
                            st.warning(f"⚠️ Sheet '{sheet_name}' est vide dans {nom_fichier}")
                            continue
                        
                        # Convertir les lignes en DataFrame avec gestion robuste des types
                        headers = []
                        for cell in rows[0]:
                            if cell is not None:
                                headers.append(str(cell).strip())
                            else:
                                headers.append("")
                        
                        data = []
                        for row in rows[1:]:
                            row_data = []
                            for cell in row:
                                if cell is not None:
                                    row_data.append(str(cell).strip())
                                else:
                                    row_data.append("")
                            data.append(row_data)
                        
                        df_sheet = pd.DataFrame(data, columns=headers)
                    else:
                        # Pour les fichiers .xlsx
                        df_sheet = pd.read_excel(BytesIO(contenu_binaire), sheet_name=sheet_name, engine="openpyxl")
                except Exception as e:
                    st.warning(f"⚠️ Erreur lecture {nom_fichier} (sheet: {sheet_name}): {str(e)}")
                    continue

                col_code_source = self._trouver_colonne(df_sheet, ["site code", "code site", "code id"])
                if col_code_source is None:
                    st.warning(f"⚠️ Colonne 'Code Site' non trouvée dans {nom_fichier} sheet '{sheet_name}'. Colonnes: {list(df_sheet.columns)}")
                    continue

                col_comment = self._trouver_colonne(df_sheet, ["comment"])
                col_action  = self._trouver_colonne(df_sheet, ["action plan"])

                nom_colonne = sheet_name
                
                st.info(f"✅ Cells Down ({nom_fichier}, sheet '{sheet_name}'): {len(df_sheet)} lignes lues")

                matches_count = 0
                for idx, row in df_resultat.iterrows():
                    code_site = str(row[col_code_principal]).strip().upper()
                    ligne = df_sheet[df_sheet[col_code_source].astype(str).str.strip().str.upper() == code_site]

                    if not ligne.empty:
                        matches_count += 1
                        comment_val = str(ligne.iloc[0][col_comment]) if col_comment and pd.notna(ligne.iloc[0].get(col_comment)) else ""
                        action_val  = str(ligne.iloc[0][col_action])  if col_action  and pd.notna(ligne.iloc[0].get(col_action))  else ""

                        if comment_val and action_val:
                            valeur = f"({date_ref} {type_ref}): {comment_val} / {action_val}"
                        elif comment_val:
                            valeur = f"({date_ref} {type_ref}): {comment_val}"
                        elif action_val:
                            valeur = f"({date_ref} {type_ref}): {action_val}"
                        else:
                            valeur = ""
                    else:
                        valeur = ""

                    df_resultat.at[idx, nom_colonne] = valeur
                
                st.success(f"✅ {matches_count} codes sites trouvés dans sheet '{sheet_name}'")

        return df_resultat

    def _determiner_type_reference(self, nom_fichier):
        nom_upper = nom_fichier.upper()
        if "NOKIA" in nom_upper:
            return "cell nokia"
        elif "HUAWEI" in nom_upper:
            return "cell huawei"
        elif "ZTE" in nom_upper:
            return "cell zte"
        return "cell"

    def _formater_date_reference(self, date_str):
        if not date_str:
            return ""
        return date_str.replace("-", "/").replace(".", "/")

    def _trouver_colonne(self, df, mots_cles):
        for col in df.columns:
            for mot in mots_cles:
                if mot.lower() in str(col).lower():
                    return col
        return None