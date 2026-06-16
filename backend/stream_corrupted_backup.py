import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import traceback
from typing import Optional, List
import tempfile
import os

# Import des classes métier
from automate.celldown import CellDown
from automate.super_xlookup import SuperXlookup
from automate.ticket import Ticket


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def get_excel_columns(file_path: str, sheet_name: Optional[str] = None) -> List[str]:
    """Récupère la liste des colonnes d'un fichier Excel"""
    try:
        if not file_path or not Path(file_path).exists():
            return []
        df = pd.read_excel(file_path, sheet_name=sheet_name or 0, nrows=0)
        return df.columns.tolist()
    except Exception as e:
        return []

def get_excel_sheets(file_path: str) -> list:
    """Récupère la liste des feuilles d'un fichier Excel"""
    try:
        if not file_path or not Path(file_path).exists():
            return []
        excel_file = pd.ExcelFile(file_path)
        return excel_file.sheet_names
    except Exception as e:
        return []

def column_selector(label: str, file_path: str, sheet_name: Optional[str] = None, 
                   default_value: str = "", key: Optional[str] = None, 
                   allow_manual: bool = True, include_last_free: bool = False) -> str:
    """
    Crée un sélecteur de colonne intelligent avec dropdown ou saisie manuelle.
    
    Args:
        label: Texte du label
        file_path: Chemin du fichier Excel
        sheet_name: Nom de la feuille (None = première)
        default_value: Valeur par défaut
        key: Clé unique pour Streamlit
        allow_manual: Permettre la saisie manuelle si fichier non chargé
        include_last_free: Ajouter l'option "last_free" (pour position résultat)
    """
    columns = get_excel_columns(file_path, sheet_name)
    
    if columns:
        # Fichier chargé : dropdown avec les colonnes
        options = columns.copy()
        if include_last_free:
            options.insert(0, "last_free")
        
        # Trouver l'index par défaut
        try:
            default_idx = options.index(default_value) if default_value in options else 0
        except:
            default_idx = 0
        
        selected = st.selectbox(
            label,
            options=options,
            index=default_idx,
            key=key,
            help=f"📋 {len(columns)} colonnes disponibles"
        )
        return selected
    else:
        # Fichier non chargé : saisie manuelle
        if allow_manual:
            return st.text_input(
                label,
                value=default_value,
                key=key,
                help="⚠️ Fichier non chargé. Saisissez manuellement (lettre, numéro ou nom)"
            )
        else:
            st.warning("⚠️ Fichier non chargé. Impossible de lister les colonnes.")
            return default_value


def main():
    st.set_page_config(
        page_title="Excel Operations Suite",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🔧 Suite d'Opérations Excel")
    st.markdown("---")
    
    # Session state pour stocker le fichier source commun
    if 'source_file' not in st.session_state:
        st.session_state.source_file = ""
    if 'execution_log' not in st.session_state:
        st.session_state.execution_log = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}  # Pour stocker les chemins des fichiers uploadés
    
    # =============================================================================
    # SECTION 1: FICHIER SOURCE COMMUN
    
    # Onglets pour choisir entre Upload et Chemin manuel
    upload_tab, manual_tab = st.tabs(["📤 Upload Fichier", "📝 Chemin Manuel"])
    
    source_file = ""
    
    with upload_tab:
        st.info("💡 Uploadez votre fichier Excel. Il sera sauvegardé temporairement et modifié par les opérations.")
        uploaded_source = st.file_uploader(
            "Sélectionnez le fichier source",
            type=["xlsx", "xls"],
            key="source_uploader",
            help="Le fichier sera modifié par toutes les opérations activées"
        )
        
        if uploaded_source is not None:
            # Sauvegarder le fichier uploadé dans un dossier temporaire
            temp_dir = tempfile.gettempdir()
            source_file_path = os.path.join(temp_dir, uploaded_source.name)
            
            # Écrire le fichier
            with open(source_file_path, "wb") as f:
                f.write(uploaded_source.getbuffer())
            
            source_file = source_file_path
            st.session_state.source_file = source_file
            st.session_state.uploaded_files['source'] = source_file
            
            st.success(f"✅ Fichier uploadé : {uploaded_source.name}")
            st.caption(f"📂 Chemin temporaire : `{source_file_path}`")
    
    with manual_tab:
        st.info("💡 Entrez le chemin complet du fichier Excel sur votre ordinateur.")
        manual_source = st.text_input(
            "Chemin du fichier source",
            value=st.session_state.source_file if st.session_state.source_file and not st.session_state.source_file.startswith(tempfile.gettempdir()) else "",
            placeholder=r"C:\Users\...\Book1.xlsx",
            key="manual_source"
        )
        
        if manual_source:
            source_file = manual_source
            st.session_state.source_file = source_file
            
            if Path(source_file).exists():
                st.success("✅ Fichier trouvé")
            else:
                st.success("✅ Fichier trouvé")
        elif source_file:
            st.error("❌ Fichier introuvable")
    
    # Afficher un aperçu du fichier source
    if sourc# Onglets pour Upload ou Chemin manuel du fichier cible
            cd_upload_tab, cd_manual_tab = st.tabs(["📤 Upload Fichier Cible", "📝 Chemin Manuel"])
            
            cd_target_file = ""
            
            with cd_upload_tab:
                uploaded_cd_target = st.file_uploader(
                    "Sélectionnez le fichier cible CellDown",
                    type=["xlsx", "xls"],
                    key="cd_target_uploader",
                    help="Fichier avec plusieurs feuilles filtrées par date"
                )
                
                if uploaded_cd_target is not None:
                    temp_dir = tempfile.gettempdir()
                    cd_target_file = os.path.join(temp_dir, f"cd_target_{uploaded_cd_target.name}")
                    
                    with open(cd_target_file, "wb") as f:
                        f.write(uploaded_cd_target.getbuffer())
                    
                    st.session_state.uploaded_files['cd_target'] = cd_target_file
                    st.success(f"✅ Fichier uploadé : {uploaded_cd_target.name}")
            
            with cd_manual_tab:
                cd_target_file_manual = st.text_input(
                    "Fichier cible (avec plusieurs feuilles)",
                    placeholder=r"C:\Users\...\DAILY_CELLS_DOWN.xlsx",
                    key="cd_target_manual"
                )
                if cd_target_file_manual:
                    cd_target_file = cd_target_file_manual
            
            # Utiliser le fichier uploadé ou manuel
            if not cd_target_file and 'cd_target' in st.session_state.uploaded_files:
                cd_target_file = st.session_state.uploaded_files['cd_target']
            
            col1, col2 = st.columns(2)
            
            with col1:t.error(f"Erreur lors de la lecture: {e}")
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 2: CONFIGURATION DES OPÉRATIONS
    # =============================================================================
    st.header("⚙️ Configuration des Opérations")
    
    # Tabs pour chaque opération
    tab1, tab2, tab3 = st.tabs([
        "🔽 CellDown",
        "🔍 Super XLOOKUP",
        "🎫 Ticket (Multi-Column XLOOKUP)"
    ])
    
    # -------------------------------------------------------------------------
    # TAB 1: CELLDOWN
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("Configuration CellDown")
        st.markdown("*Effectue un XLOOKUP multiple sur les feuilles filtrées par date*")
        
        cd_enabled = st.checkbox("✅ Activer CellDown", value=False, key="cd_enabled")
        
        if cd_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                cd_target_file = st.text_input(
                    "Fichier cible (avec plusieurs feuilles)",
                    placeholder=r"C:\Users\...\DAILY_CELLS_DOWN.xlsx",
                    key="cd_target"
                )
                
                # Sélecteur de feuille source
                source_sheets = get_excel_sheets(source_file) if source_file else []
                if source_sheets:
                    cd_source_sheet = st.selectbox(
                        "Feuille source",
                        options=source_sheets,
                        index=0,
                        key="cd_source_sheet"
                    )
                else:
                    cd_source_sheet = st.text_input(
                        "Nom de la feuille source",
            # Onglets pour Upload ou Chemin manuel du fichier cible
            sx_upload_tab, sx_manual_tab = st.tabs(["📤 Upload Fichier Cible", "📝 Chemin Manuel"])
            
            sx_target_file = ""
            
            with sx_upload_tab:
                uploaded_sx_target = st.file_uploader(
                    "Sélectionnez le fichier cible SuperXlookup",
                    type=["xlsx", "xls"],
                    key="sx_target_uploader",
                    help="Fichier contenant les données à rapporter"
                )
                
                if uploaded_sx_target is not None:
                    temp_dir = tempfile.gettempdir()
                    sx_target_file = os.path.join(temp_dir, f"sx_target_{uploaded_sx_target.name}")
                    
                    with open(sx_target_file, "wb") as f:
                        f.write(uploaded_sx_target.getbuffer())
                    
                    st.session_state.uploaded_files['sx_target'] = sx_target_file
                    st.success(f"✅ Fichier uploadé : {uploaded_sx_target.name}")
            
            with sx_manual_tab:
                sx_target_file_manual = st.text_input(
                    "Fichier cible",
                    placeholder=r"C:\Users\...\incident.xlsx",
                    key="sx_target_manual"
                )
                if sx_target_file_manual:
                    sx_target_file = sx_target_file_manual
            
            # Utiliser le fichier uploadé ou manuel
            if not sx_target_file and 'sx_target' in st.session_state.uploaded_files:
                sx_target_file = st.session_state.uploaded_files['sx_target']
            
            col1, col2 = st.columns(2)
            
            with col1:   source_file,
                    cd_source_sheet if source_sheets else None,
                    default_value="B",
                    key="cd_source_key"
                )
                
                # Colonne clé dans cible (avec dropdown)
                cd_target_key = column_selector(
                    "Colonne clé dans cible",
                    cd_target_file,
                    None,  # Première feuille par défaut
                    default_value="B",
                    key="cd_target_key"
                )
            
            with col2:
                # Colonne valeur à rapporter (avec dropdown)
                cd_target_value = column_selector(
                    "Colonne valeur à rapporter",
                    cd_target_file,
                    None,
                    default_value="T",
                    key="cd_target_value"
                )
                
                cd_date = st.text_input(
                    "Date de filtrage (jjmmaaaa)",
                    value=datetime.now().strftime("%d%m%Y"),
                    key="cd_date"
                )
                
                # Colonne de départ (avec dropdown + last_free)
                cd_start_col = column_selector(
                    "Colonne de départ pour résultats",
                    source_file,
                    cd_source_sheet if source_sheets else None,
                    default_value="C",
                    key="cd_start_col",
                    include_last_free=True
                )
                
                cd_reference = st.text_input(
                    "Nom de référence (pour préfixe)",
                    value="CellDown",
                    key="cd_reference"
                )
    
    # -------------------------------------------------------------------------
    # TAB 2: SUPER XLOOKUP
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("Configuration Super XLOOKUP")
        st.markdown("*XLOOKUP simple avec préfixe [nom - date]*")
        
        sx_enabled = st.checkbox("✅ Activer Super XLOOKUP", value=False, key="sx_enabled")
        
        if sx_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                sx_target_file = st.text_input(
                    "Fichier cible",
                    placeholder=r"C:\Users\...\incident.xlsx",
                    key="sx_target"
                )
                
                # Sélecteur de feuille source
                source_sheets = get_excel_sheets(source_file) if source_file else []
                if source_sheets:
                    sx_source_sheet = st.selectbox(
                        "Feuille source",
                        options=source_sheets,
                        index=0,
                        key="sx_source_sheet"
                    )
                else:
                    sx_source_sheet = st.text_input(
                        "Feuille source",
                        value="Sheet1",
                        key="sx_source_sheet_manual"
                    )
                
                # Sélecteur de feuille cible
                target_sheets = get_excel_sheets(sx_target_file) if sx_target_file else []
                if target_sheets:
                    sx_target_sheet = st.selectbox(
                        "Feuille cible",
                        options=target_sheets,
                        index=0,
                        key="sx_target_sheet"
                    )
                else:
                    sx_target_sheet = st.text_input(
                        "Feuille cible",
                        value="Sheet1",
            # Onglets pour Upload ou Chemin manuel du fichier cible
            tk_upload_tab, tk_manual_tab = st.tabs(["📤 Upload Fichier Cible", "📝 Chemin Manuel"])
            
            tk_target_file = ""
            
            with tk_upload_tab:
                uploaded_tk_target = st.file_uploader(
                    "Sélectionnez le fichier cible Ticket",
                    type=["xlsx", "xls"],
                    key="tk_target_uploader",
                    help="Fichier contenant les tickets à concaténer"
                )
                
                if uploaded_tk_target is not None:
                    temp_dir = tempfile.gettempdir()
                    tk_target_file = os.path.join(temp_dir, f"tk_target_{uploaded_tk_target.name}")
                    
                    with open(tk_target_file, "wb") as f:
                        f.write(uploaded_tk_target.getbuffer())
                    
                    st.session_state.uploaded_files['tk_target'] = tk_target_file
                    st.success(f"✅ Fichier uploadé : {uploaded_tk_target.name}")
            
            with tk_manual_tab:
                tk_target_file_manual = st.text_input(
                    "Fichier cible",
                    placeholder=r"C:\Users\...\Incident_Ticket.xlsx",
                    key="tk_target_manual"
                )
                if tk_target_file_manual:
                    tk_target_file = tk_target_file_manual
            
            # Utiliser le fichier uploadé ou manuel
            if not tk_target_file and 'tk_target' in st.session_state.uploaded_files:
                tk_target_file = st.session_state.uploaded_files['tk_target']
            
            col1, col2 = st.columns(2)
            
            with col1:   sx_source_sheet if source_sheets else None,
                    default_value="B",
                    key="sx_source_key"
                )
            
            with col2:
                # Colonne clé cible (avec dropdown)
                sx_target_key = column_selector(
                    "Colonne clé cible",
                    sx_target_file,
                    sx_target_sheet if target_sheets else None,
                    default_value="D",
                    key="sx_target_key"
                )
                
                # Colonne valeur à rapporter (avec dropdown)
                sx_target_value = column_selector(
                    "Colonne valeur à rapporter",
                    sx_target_file,
                    sx_target_sheet if target_sheets else None,
                    default_value="J",
                    key="sx_target_value"
                )
                
                # Position colonne résultat (avec dropdown + last_free)
                sx_result_position = column_selector(
                    "Position colonne résultat",
                    source_file,
                    sx_source_sheet if source_sheets else None,
                    default_value="last_free",
                    key="sx_result_position",
                    include_last_free=True
                )
                
                sx_result_name = st.text_input(
                    "Nom colonne résultat",
                    value="Commentaire",
                    key="sx_result_name"
                )
                sx_reference = st.text_input(
                    "Nom de référence",
                    value="NOKIA",
                    key="sx_reference"
                )
    
    # -------------------------------------------------------------------------
    # TAB 3: TICKET
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("Configuration Ticket")
        st.markdown("*XLOOKUP avec extraction de codes sites et concaténation multi-colonnes (TEXTJOIN)*")
        
        tk_enabled = st.checkbox("✅ Activer Ticket", value=False, key="tk_enabled")
        
        if tk_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                tk_target_file = st.text_input(
                    "Fichier cible",
                    placeholder=r"C:\Users\...\Incident_Ticket.xlsx",
                    key="tk_target"
                )
                
                # Sélecteur de feuille source
                source_sheets = get_excel_sheets(source_file) if source_file else []
                if source_sheets:
                    tk_source_sheet = st.selectbox(
                        "Feuille source",
                        options=source_sheets,
                        index=0,
                        key="tk_source_sheet"
                    )
                else:
                    tk_source_sheet = st.text_input(
                        "Feuille source",
                        value="Sheet1",
                        key="tk_source_sheet_manual"
                    )
                
                # Sélecteur de feuille cible
                target_sheets = get_excel_sheets(tk_target_file) if tk_target_file else []
                if target_sheets:
                    tk_target_sheet = st.selectbox(
                        "Feuille cible",
                        options=target_sheets,
                        index=0,
                        key="tk_target_sheet"
                    )
                else:
                    tk_target_sheet = st.text_input(
                        "Feuille cible (vide = première)",
                        value="",
                        key="tk_target_sheet_manual"
                    )
                
                # Colonne clé source (avec dropdown)
                tk_source_key = column_selector(
                    "Colonne clé source",
                    source_file,
                    tk_source_sheet if source_sheets else None,
                    default_value="B",
                    key="tk_source_key"
                )
                
                # Colonne extraction codes (avec dropdown)
                tk_extract_col = column_selector(
                    "Colonne extraction codes (cible)",
                    tk_target_file,
                    tk_target_sheet if target_sheets else None,
                    default_value="T",
                    key="tk_extract_col"
                )
            
            with col2:
                # Position colonne résultat (avec dropdown + last_free)
                tk_result_position = column_selector(
                    "Position colonne résultat",
                    source_file,
                    tk_source_sheet if source_sheets else None,
                    default_value="last_free",
                    key="tk_result_position",
                    include_last_free=True
                )
                
                tk_result_name = st.text_input(
                    "Nom colonne résultat",
                    value="Ticket",
                    key="tk_result_name"
                )
                tk_reference = st.text_input(
                    "Nom de référence",
                    value="Ticket",
                    key="tk_reference"
                )
                
                # Colonnes à concaténer (multiselect si fichier chargé)
                target_columns = get_excel_columns(tk_target_file, tk_target_sheet if target_sheets else None)
                if target_columns:
                    tk_join_cols_list = st.multiselect(
                        "Colonnes à concaténer (TEXTJOIN)",
                        options=target_columns,
                        default=["L", "W", "X", "Y", "Z"] if all(col in target_columns for col in ["L", "W", "X", "Y", "Z"]) else [],
                        key="tk_join_cols_multi",
                        help="Sélectionnez plusieurs colonnes à concaténer"
                    )
                    # Convertir la liste en chaîne séparée par virgules
                    tk_join_cols = ",".join(tk_join_cols_list) if tk_join_cols_list else "L,W,X,Y,Z"
                else:
                    tk_join_cols = st.text_input(
                        "Colonnes à concaténer (séparées par virgule)",
                        value="L,W,X,Y,Z",
                        key="tk_join_cols"
                    )
                
                tk_separator = st.text_input(
                    "Séparateur TEXTJOIN",
                    value="..",
                    key="tk_separator"
                )
    
    st.markdown("---")
    
    # =============================================================================
    # SECTION 3: EXÉCUTION SÉQUENTIELLE
    # =============================================================================
    st.header("▶️ Exécution")
    
    # Mode debug
    debug_mode = st.checkbox("🐛 Mode Debug (afficher les paramètres avant exécution)", value=False)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        execute_button = st.button("🚀 Exécuter Toutes les Opérations", type="primary", use_container_width=True)
    
    with col2:
        clear_log = st.button("🗑️ Effacer le Log", use_container_width=True)
        if clear_log:
            st.session_state.execution_log = []
            st.rerun()
    
    # Vérification avant exécution
    if execute_button:
        if not source_file or not Path(source_file).exists():
            st.error("❌ Veuillez spécifier un fichier source valide")
        else:
            # Préparer les paramètres
            cd_params_dict = {
                'target_file': cd_target_file if cd_enabled else "",
                'source_sheet': cd_source_sheet if cd_enabled else "",
                'source_key': cd_source_key if cd_enabled else "",
                'target_key': cd_target_key if cd_enabled else "",
                'target_value': cd_target_value if cd_enabled else "",
                'date': cd_date if cd_enabled else "",
                'start_col': cd_start_col if cd_enabled else "",
                'reference': cd_reference if cd_enabled else ""
            }
            sx_params_dict = {
                'target_file': sx_target_file if sx_enabled else "",
                'source_sheet': sx_source_sheet if sx_enabled else "",
                'target_sheet': sx_target_sheet if sx_enabled else "",
                'source_key': sx_source_key if sx_enabled else "",
                'target_key': sx_target_key if sx_enabled else "",
                'target_value': sx_target_value if sx_enabled else "",
                'result_position': sx_result_position if sx_enabled else "",
                'result_name': sx_result_name if sx_enabled else "",
                'reference': sx_reference if sx_enabled else ""
            }
            tk_params_dict = {
                'target_file': tk_target_file if tk_enabled else "",
                'source_sheet': tk_source_sheet if tk_enabled else "",
                'target_sheet': tk_target_sheet if tk_enabled else "",
                'source_key': tk_source_key if tk_enabled else "",
                'extract_col': tk_extract_col if tk_enabled else "",
                'result_position': tk_result_position if tk_enabled else "",
                'result_name': tk_result_name if tk_enabled else "",
                'reference': tk_reference if tk_enabled else "",
                'join_cols': tk_join_cols if tk_enabled else "",
                'separator': tk_separator if tk_enabled else ""
            }
            
            # Afficher les paramètres en mode debug
            if debug_mode:
                st.subheader("🐛 Paramètres Debug")
                if cd_enabled:
                    with st.expander("CellDown Params"):
                        st.json(cd_params_dict)
                if sx_enabled:
                    with st.expander("SuperXlookup Params"):
                        st.json(sx_params_dict)
                if tk_enabled:
                    with st.expander("Ticket Params"):
                        st.json(tk_params_dict)
                st.markdown("---")
            
            execute_operations(
                source_file,
                cd_enabled, sx_enabled, tk_enabled,
                cd_params_dict,
                sx_params_dict,
                tk_params_dict
            )
    
    # Affichage du log d'exécution
    if st.session_state.execution_log:
        st.subheader("📋 Journal d'Exécution")
        for entry in st.session_state.execution_log:
            if entry['status'] == 'success':
                st.success(f"✅ **{entry['operation']}** - {entry['message']}")
            elif entry['status'] == 'error':
                st.error(f"❌ **{entry['operation']}** - {entry['message']}")
            elif entry['status'] == 'info':
                st.info(f"ℹ️ **{entry['operation']}** - {entry['message']}")
        
        # Afficher aperçu final avec bouton de rafraîchissement
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader("👁️ Aperçu du Fichier Après Traitement")
        with col2:
            if st.button("🔄 Rafraîchir l'aperçu", key="refresh_preview"):
                st.rerun()
        with col3:
            # Bouton de téléchargement du fichier modifié
            if source_file and Path(source_file).exists():
                try:
                    with open(source_file, "rb") as f:
                        file_bytes = f.read()
                    
                    # Nom du fichier modifié
                    original_name = Path(source_file).stem
                    download_name = f"{original_name}_modified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    
                    st.download_button(
                        label="📥 Télécharger",
                        data=file_bytes,
                        file_name=download_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Télécharger le fichier modifié"
                    )
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
        if source_file and Path(source_file).exists():
            try:
                df_final = pd.read_excel(source_file)
                st.info(f"📊 Fichier contient maintenant **{len(df_final.columns)} colonnes** et **{len(df_final)} lignes**")
                
                # Afficher les 20 premières lignes
                st.dataframe(df_final.head(20), use_container_width=True)
                
                # Afficher les noms de colonnes
                with st.expander("📋 Liste complète des colonnes"):
                    cols_display = ", ".join([f"`{col}`" for col in df_final.columns])
                    st.markdown(cols_display)
                    
            except Exception as e:
                st.error(f"Erreur lors de la lecture: {e}")


def execute_operations(source_file, cd_enabled, sx_enabled, tk_enabled, cd_params, sx_params, tk_params):
    """Exécute les opérations séquentiellement sur le même fichier source"""
    
    st.session_state.execution_log = []
    operations_count = sum([cd_enabled, sx_enabled, tk_enabled])
    
    if operations_count == 0:
        st.warning("⚠️ Aucune opération n'est activée")
        return
    
    # Vérifier que le fichier n'est pas verrouillé
    try:
        with open(source_file, 'r+b') as f:
            pass  # Juste tester qu'on peut ouvrir en écriture
    except PermissionError:
        st.error("❌ Le fichier source est verrouillé ou ouvert dans Excel. Fermez-le avant de continuer.")
        return
    except Exception as e:
        st.warning(f"⚠️ Avertissement lors de la vérification du fichier: {e}")
    
    # Compter les colonnes AVANT traitement
    try:
        df_before = pd.read_excel(source_file)
        cols_before = len(df_before.columns)
        st.session_state.execution_log.append({
            'operation': 'ÉTAT INITIAL',
            'status': 'info',
            'message': f'Fichier source avec {cols_before} colonnes: {", ".join(df_before.columns.tolist())}'
        })
    except Exception as e:
        st.session_state.execution_log.append({
            'operation': 'ÉTAT INITIAL',
            'status': 'error',
            'message': f'Impossible de lire le fichier: {e}'
        })
        return
    
    st.info(f"🔄 Exécution de {operations_count} opération(s) sur le fichier source...")
    
    # Ordre d'exécution: 1. CellDown, 2. SuperXlookup, 3. Ticket
    
    # -------------------------------------------------------------------------
    # 1. CELLDOWN
    # -------------------------------------------------------------------------
    if cd_enabled:
        try:
            st.session_state.execution_log.append({
                'operation': 'CellDown',
                'status': 'info',
                'message': 'Démarrage...'
            })
            
            # Validation
            if not cd_params['target_file'] or not Path(cd_params['target_file']).exists():
                raise FileNotFoundError(f"Fichier cible introuvable: {cd_params['target_file']}")
            
            celldown = CellDown(
                source_file_path=source_file,
                target_file_path=cd_params['target_file'],
                colown_key_path_source=cd_params['source_key'],
                target_key_column=cd_params['target_key'],
                target_value_column=cd_params['target_value'],
                result_position_column="last_free",  # Non utilisé dans super_xlookup_par_date
                source_sheet_path=cd_params['source_sheet'],
                date_str=cd_params['date'],
                start_column=cd_params['start_col'],
                reference_name=cd_params['reference']
            )
            
            # Capture de la sortie console
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                celldown.super_xlookup_par_date()
            
            output = f.getvalue()
            
            # Vérifier que le fichier a été modifié
            df_check = pd.read_excel(source_file)
            
            st.session_state.execution_log.append({
                'operation': 'CellDown',
                'status': 'success',
                'message': f'Terminé avec succès. Feuilles filtrées par date {cd_params["date"]}. Fichier maintenant avec {len(df_check.columns)} colonnes. Output: {output[:200]}'
            })
            
        except Exception as e:
            st.session_state.execution_log.append({
                'operation': 'CellDown',
                'status': 'error',
                'message': f'Erreur: {str(e)}\n{traceback.format_exc()}'
            })
    
    # -------------------------------------------------------------------------
    # 2. SUPER XLOOKUP
    # -------------------------------------------------------------------------
    if sx_enabled:
        try:
            st.session_state.execution_log.append({
                'operation': 'SuperXlookup',
                'status': 'info',
                'message': 'Démarrage...'
            })
            
            if not sx_params['target_file'] or not Path(sx_params['target_file']).exists():
                raise FileNotFoundError(f"Fichier cible introuvable: {sx_params['target_file']}")
            
            xlookup = SuperXlookup(
                source_file_path=source_file,
                target_file_path=sx_params['target_file'],
                source_key_column=sx_params['source_key'],
                target_key_column=sx_params['target_key'],
                target_value_column=sx_params['target_value'],
                result_position_column=sx_params['result_position'],
                result_column_name=sx_params['result_name'],
                source_sheet_name=sx_params['source_sheet'],
                target_sheet_name=sx_params['target_sheet'],
                reference_name=sx_params['reference']
            )
            
            # Capture de la sortie console
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                xlookup.run()
            
            output = f.getvalue()
            
            # Vérifier que le fichier a été modifié
            df_check = pd.read_excel(source_file)
            col_exists = sx_params["result_name"] in df_check.columns
            
            st.session_state.execution_log.append({
                'operation': 'SuperXlookup',
                'status': 'success',
                'message': f'Terminé. Résultat dans colonne "{sx_params["result_name"]}" ({"✅ trouvée" if col_exists else "❌ non trouvée"}). Fichier avec {len(df_check.columns)} colonnes. Output: {output[:200]}'
            })
            
        except Exception as e:
            st.session_state.execution_log.append({
                'operation': 'SuperXlookup',
                'status': 'error',
                'message': f'Erreur: {str(e)}\n{traceback.format_exc()}'
            })
    
    # -------------------------------------------------------------------------
    # 3. TICKET
    # -------------------------------------------------------------------------
    if tk_enabled:
        try:
            st.session_state.execution_log.append({
                'operation': 'Ticket',
                'status': 'info',
                'message': 'Démarrage...'
            })
            
            if not tk_params['target_file'] or not Path(tk_params['target_file']).exists():
                raise FileNotFoundError(f"Fichier cible introuvable: {tk_params['target_file']}")
            
            # Parse des colonnes à joindre
            join_cols = [col.strip() for col in tk_params['join_cols'].split(',')]
            
            ticket = Ticket(
                source_file_path=source_file,
                target_file_path=tk_params['target_file'],
                source_key_column=tk_params['source_key'],
                result_position_column=tk_params['result_position'],
                result_column_name=tk_params['result_name'],
                source_sheet_name=tk_params['source_sheet'],
                target_sheet_name=tk_params['target_sheet'],
                reference_name=tk_params['reference'],
                target_join_columns=join_cols,
                join_separator=tk_params['separator'],
                ignore_empty=True,
                extract_source_column=tk_params['extract_col']
            )
            
            # Capture de la sortie console
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                ticket.run()
            
            output = f.getvalue()
            
            # Vérifier que le fichier a été modifié
            df_check = pd.read_excel(source_file)
            col_exists = tk_params["result_name"] in df_check.columns
            
            st.session_state.execution_log.append({
                'operation': 'Ticket',
                'status': 'success',
                'message': f'Terminé. Résultat dans colonne "{tk_params["result_name"]}" ({"✅ trouvée" if col_exists else "❌ non trouvée"}). TEXTJOIN sur {len(join_cols)} colonnes. Fichier avec {len(df_check.columns)} colonnes. Output: {output[:200]}'
            })
            
        except Exception as e:
            st.session_state.execution_log.append({
                'operation': 'Ticket',
                'status': 'error',
                'message': f'Erreur: {str(e)}\n{traceback.format_exc()}'
            })
    
    # Résumé final
    success_count = sum(1 for log in st.session_state.execution_log if log['status'] == 'success')
    error_count = sum(1 for log in st.session_state.execution_log if log['status'] == 'error')
    
    # Compter les colonnes APRÈS traitement
    try:
        df_after = pd.read_excel(source_file)
        cols_after = len(df_after.columns)
        cols_added = cols_after - cols_before
        
        st.session_state.execution_log.append({
            'operation': 'ÉTAT FINAL',
            'status': 'info',
            'message': f'Fichier final avec {cols_after} colonnes (+{cols_added} nouvelles): {", ".join(df_after.columns.tolist())}'
        })
    except Exception as e:
        st.session_state.execution_log.append({
            'operation': 'ÉTAT FINAL',
            'status': 'error',
            'message': f'Impossible de lire le fichier final: {e}'
        })
    
    st.session_state.execution_log.append({
        'operation': 'RÉSUMÉ',
        'status': 'info',
        'message': f'✅ {success_count} succès | ❌ {error_count} erreurs'
    })


if __name__ == "__main__":
    main()
