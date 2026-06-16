# ============================================================================
# components/file_uploader.py
# Composant de chargement des fichiers sources (avec cache)
# ============================================================================

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SOURCES

# ============================================================================
# CACHE POUR LA LECTURE DES FICHIERS
# ============================================================================

import re

@st.cache_data(ttl=3600)
def lire_fichier_excel_cache(contenu_binaire, sheet_name=None):
    from io import BytesIO
    fichier = BytesIO(contenu_binaire)
    if sheet_name:
        return pd.read_excel(fichier, sheet_name=sheet_name)
    return pd.read_excel(fichier)

@st.cache_data(ttl=3600)
def lire_toutes_sheets_cache(contenu_binaire):
    from io import BytesIO
    fichier = BytesIO(contenu_binaire)
    return pd.read_excel(fichier, sheet_name=None)

@st.cache_data(ttl=3600)
def lire_noms_sheets_cache(contenu_binaire, nom_fichier=""):
    """Lit les noms des sheets, supporte xlsx et xlsb"""
    from io import BytesIO
    fichier = BytesIO(contenu_binaire)
    
    # Déterminer le format selon l'extension du fichier
    if nom_fichier.endswith(".xlsb"):
        try:
            # Pour les fichiers .xlsb
            import pyxlsb
            xl = pyxlsb.open_workbook(fichier)
            # workbook.sheets retourne directement une liste de noms (strings)
            sheet_names = xl.sheets
            return sheet_names
        except Exception as e:
            st.warning(f"⚠️ Erreur lecture .xlsb: {str(e)}")
            return []
    else:
        # Pour les fichiers .xlsx
        try:
            xl = pd.ExcelFile(fichier)
            return xl.sheet_names
        except Exception as e:
            st.warning(f"⚠️ Erreur lecture .xlsx: {str(e)}")
            return []

# =========================================================================
# FONCTIONS DE SÉLECTION AUTOMATIQUE DES SHEETS PAR SOURCE
# =========================================================================

def trouver_sheet_retour_camusat(noms_sheets):
    """Cherche sheet avec pattern: Inputs_XX-XX (date)"""
    for sheet in noms_sheets:
        if re.search(r"Inputs_\d{2}-\d{2}", sheet, re.IGNORECASE):
            return [sheet]
    return []

def trouver_sheet_hourly_ihs(noms_sheets):
    """Cherche sheet nommée 'hourly-ihs'"""
    for sheet in noms_sheets:
        if sheet.lower() == "hourly-ihs":
            return [sheet]
    return []

def trouver_sheet_ocm_ran(noms_sheets):
    """Cherche sheet nommée 'ALL SITE DOWN'"""
    for sheet in noms_sheets:
        if "all site down" in sheet.lower():
            return [sheet]
    return []

def trouver_sheet_ticket(noms_sheets):
    """Prend automatiquement la seule sheet (ou la première)"""
    if noms_sheets:
        return [noms_sheets[0]]
    return []

def trouver_sheet_dashboard_cell(noms_sheets):
    """Cherche sheet avec pattern: TOP OFF JJMM (jour et mois), prend la dernière date"""
    sheets_top_off = []
    for sheet in noms_sheets:
        match = re.search(r"TOP OFF\s+(\d{2})(\d{2})", sheet, re.IGNORECASE)
        if match:
            jj = match.group(1)  # Jour
            mm = match.group(2)  # Mois
            # Convertir en MMJJ pour tri chronologique correct
            date_sortable = mm + jj
            sheets_top_off.append((sheet, date_sortable))
    
    if sheets_top_off:
        # Trier par date MMJJ (chronologique) et prendre la dernière
        sheets_top_off.sort(key=lambda x: x[1], reverse=True)
        return [sheets_top_off[0][0]]
    return []


def render_file_uploader():

    st.header("📂 CHARGEMENT DES FICHIERS")
    st.caption("Chargez d'abord le fichier principal, puis les fichiers sources (optionnels).")

    # =========================================================================
    # INITIALISATION DE SESSION STATE
    # =========================================================================
    if "fichiers" not in st.session_state:
        st.session_state.fichiers = {
            "principal": None,
            "principal_nom": None,
            "principal_binaire": None,
            "sources": {}
        }
        for key in SOURCES:
            st.session_state.fichiers["sources"][key] = []

    for key in SOURCES:
        if key not in st.session_state.fichiers["sources"]:
            st.session_state.fichiers["sources"][key] = []
        elif st.session_state.fichiers["sources"][key] is None:
            st.session_state.fichiers["sources"][key] = []

    # =========================================================================
    # DATE DE RÉFÉRENCE GLOBALE
    # =========================================================================
    st.subheader("📅 Date de référence")

    col_date1, col_date2 = st.columns([1, 3])
    with col_date1:
        st.text_input(
            "Date",
            placeholder="JJ/MM/AAAA",
            key="date_reference",
            label_visibility="visible"
        )

    st.divider()

    # =========================================================================
    # FICHIER PRINCIPAL
    # =========================================================================
    st.subheader("📂 Fichier principal (obligatoire)")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.fichiers["principal"] is not None:
            st.success(f"✅ {st.session_state.fichiers.get('principal_nom', 'Fichier chargé')} - {len(st.session_state.fichiers['principal'])} sites")
        else:
            st.info("⏳ En attente du fichier principal...")

    with col2:
        fichier_principal = st.file_uploader(
            "Upload",
            type=["xlsx"],
            key="upload_principal",
            label_visibility="collapsed"
        )
        if fichier_principal is not None:
            if fichier_principal.name != st.session_state.fichiers.get("principal_nom"):
                contenu_binaire = fichier_principal.getvalue()
                df = lire_fichier_excel_cache(contenu_binaire, sheet_name="daily break down")
                st.session_state.fichiers["principal"] = df
                st.session_state.fichiers["principal_nom"] = fichier_principal.name
                st.session_state.fichiers["principal_binaire"] = contenu_binaire
                st.rerun()

    st.divider()

    # =========================================================================
    # FICHIERS SOURCES
    # =========================================================================
    st.subheader("📦 Fichiers sources (optionnels - plusieurs fichiers possibles)")

    sources_chargees = 0

    for key, config in SOURCES.items():
        nom_source = config["nom"]

        if key not in st.session_state.fichiers["sources"]:
            st.session_state.fichiers["sources"][key] = []

        if key == "cells_down":
            col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 1])
        else:
            col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.write(f"**{nom_source}**")

        with col2:
            fichiers_source = st.session_state.fichiers["sources"].get(key, [])
            if fichiers_source:
                sources_chargees += 1
                st.success(f"✅ {len(fichiers_source)} fichier(s)")
            else:
                st.info("⏳ En attente...")

        if key == "cells_down":
            with col3:
                st.text_input(
                    "📅 Date",
                    placeholder="JJ/MM/AAAA",
                    key=f"date_{key}",          # stocké dans "date_cells_down"
                    label_visibility="collapsed"
                )
            with col4:
                nouveaux_fichiers = st.file_uploader(
                    "Upload",
                    type=["xlsx", "xlsb"],
                    key=f"upload_{key}",
                    label_visibility="collapsed",
                    accept_multiple_files=True
                )
        else:
            with col3:
                nouveaux_fichiers = st.file_uploader(
                    "Upload",
                    type=["xlsx"],
                    key=f"upload_{key}",
                    label_visibility="collapsed",
                    accept_multiple_files=True
                )

        # Ajout des nouveaux fichiers avec rerun
        if nouveaux_fichiers:
            changement = False
            for fichier in nouveaux_fichiers:
                noms_existants = [f["nom"] for f in st.session_state.fichiers["sources"][key]]
                if fichier.name not in noms_existants:
                    contenu_binaire = fichier.getvalue()
                    st.session_state.fichiers["sources"][key].append({
                        "binaire": contenu_binaire,
                        "nom": fichier.name,
                    })
                    changement = True
            if changement:
                st.rerun()

        # -----------------------------------------------------------------
        # AFFICHAGE DES SHEETS
        # Logique spécifique par source
        # -----------------------------------------------------------------
        if st.session_state.fichiers["sources"].get(key):
            for idx_f, fichier_data in enumerate(st.session_state.fichiers["sources"][key]):
                noms_sheets = lire_noms_sheets_cache(fichier_data["binaire"], fichier_data["nom"])

                # Déterminer les sheets à sélectionner selon la source
                config_key = f"config_{key}"
                if config_key not in st.session_state:
                    st.session_state[config_key] = {}

                nom_fichier = fichier_data['nom']
                
                # ============================================================
                # SÉLECTION AUTOMATIQUE SANS AFFICHAGE
                # ============================================================
                if key == "ticket":
                    # Ticket : prendre automatiquement la seule sheet
                    sheets_auto = trouver_sheet_ticket(noms_sheets)
                    st.session_state[config_key][nom_fichier] = sheets_auto

                elif key == "incident":
                    # Incident : chercher toutes les sheets (pas d'affichage)
                    st.session_state[config_key][nom_fichier] = noms_sheets.copy()

                elif key == "retour_camusat":
                    # Retour CAMUSAT : chercher "Inputs_XX-XX" et AFFICHER
                    sheets_auto = trouver_sheet_retour_camusat(noms_sheets)
                    st.session_state[config_key][nom_fichier] = sheets_auto
                    if sheets_auto:
                        st.info(f"✅ {fichier_data['nom']}: Sheet sélectionnée automatiquement: **{sheets_auto[0]}**")

                elif key == "hourly_ihs":
                    # Hourly IHS : chercher "hourly-ihs"
                    sheets_auto = trouver_sheet_hourly_ihs(noms_sheets)
                    st.session_state[config_key][nom_fichier] = sheets_auto

                elif key == "ocm_ran":
                    # OCM RAN : chercher "ALL SITE DOWN"
                    sheets_auto = trouver_sheet_ocm_ran(noms_sheets)
                    st.session_state[config_key][nom_fichier] = sheets_auto

                elif key == "dashboard_cell":
                    # Dashboard Cell : chercher "TOP OFF" avec la dernière date (JJMM), AFFICHER UNIQUEMENT
                    sheets_auto = trouver_sheet_dashboard_cell(noms_sheets)
                    st.session_state[config_key][nom_fichier] = sheets_auto
                    if sheets_auto:
                        st.info(f"✅ {fichier_data['nom']}: Sheet sélectionnée automatiquement: **{sheets_auto[0]}**")

                # ============================================================
                # SÉLECTION AVEC FILTRAGE PAR DATE (cells_down)
                # ============================================================
                elif key == "cells_down":
                    date_saisie = st.session_state.get("date_cells_down", "")

                    if date_saisie:
                        # Nettoyer la date : "16/05/2026" → "16052026"
                        date_nettoyee = date_saisie.replace("/", "").replace("-", "").replace(".", "")

                        sheets_trouvees = [
                            s for s in noms_sheets
                            if date_nettoyee in s.replace("/", "").replace("-", "").replace(".", "")
                        ]

                        if sheets_trouvees:
                            with st.expander(f"📋 {fichier_data['nom']} - {len(sheets_trouvees)} sheets trouvées"):
                                if nom_fichier not in st.session_state[config_key]:
                                    st.session_state[config_key][nom_fichier] = sheets_trouvees.copy()

                                nouvelles_selections = []
                                for s in sheets_trouvees:
                                    coche = s in st.session_state[config_key][nom_fichier]
                                    if st.checkbox(s, value=coche, key=f"sheet_{key}_{idx_f}_{s}"):
                                        nouvelles_selections.append(s)

                                st.session_state[config_key][nom_fichier] = nouvelles_selections
                                st.caption(f"✅ {len(nouvelles_selections)}/{len(sheets_trouvees)} sheets sélectionnées")

                        else:
                            st.warning(f"⚠️ {fichier_data['nom']} : aucune sheet contenant '{date_nettoyee}' trouvée.")

                # ============================================================
                # AFFICHAGE DE TOUTES LES SHEETS (top_offenders, retour_ihs)
                # ============================================================
                else:
                    if noms_sheets:
                        with st.expander(f"📋 {fichier_data['nom']} - {len(noms_sheets)} sheets trouvées"):
                            if nom_fichier not in st.session_state[config_key]:
                                st.session_state[config_key][nom_fichier] = noms_sheets.copy()

                            nouvelles_selections = []
                            for s in noms_sheets:
                                coche = s in st.session_state[config_key][nom_fichier]
                                if st.checkbox(s, value=coche, key=f"sheet_{key}_{idx_f}_{s}"):
                                    nouvelles_selections.append(s)

                            st.session_state[config_key][nom_fichier] = nouvelles_selections
                            st.caption(f"✅ {len(nouvelles_selections)}/{len(noms_sheets)} sheets sélectionnées")

    # =========================================================================
    # BOUTONS VIDER
    # =========================================================================
    for key, config in SOURCES.items():
        if st.session_state.fichiers["sources"].get(key):
            if st.button(f"🗑️ Vider {config['nom']}", key=f"clear_{key}"):
                st.session_state.fichiers["sources"][key] = []
                st.rerun()

    # =========================================================================
    # RÉSUMÉ FINAL
    # =========================================================================
    st.divider()

    principal_ok = st.session_state.fichiers["principal"] is not None

    if principal_ok:
        nb_sites = len(st.session_state.fichiers["principal"])
        st.success(f"✅ Prêt pour la compilation : {nb_sites} sites, {sources_chargees}/{len(SOURCES)} sources chargées")
    else:
        st.warning("⚠️ Veuillez charger le fichier principal pour continuer.")

    return principal_ok