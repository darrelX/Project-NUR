"""
Composant pour la configuration de la source principale
"""

import streamlit as st
from typing import Optional, Dict
from utils.excel_utils import ExcelFileHandler, display_file_upload_info


def render_source_panel() -> Optional[Dict]:
    """
    Affiche le panneau de configuration de la source principale
    
    Returns:
        Dict avec source_file_path et source_sheet_path ou None
    """
    st.markdown("### 📂 Source principale")
    
    with st.container():
        st.markdown('<div class="config-section">', unsafe_allow_html=True)
        
        # Upload du fichier principal
        st.markdown("#### Fichier Excel source")
        uploaded_file = st.file_uploader(
            "Sélectionnez le fichier source principal",
            type=['xlsx', 'xls'],
            key="source_file",
            help="Fichier Excel qui sera enrichi par les traitements"
        )
        
        if uploaded_file is not None:
            display_file_upload_info(uploaded_file)
            
            # Sauvegarder le fichier
            source_file_path = ExcelFileHandler.save_uploaded_file(uploaded_file)
            
            if source_file_path:
                # Stocker dans la session
                st.session_state['source_file_path'] = source_file_path
                
                # Obtenir les informations du fichier
                file_info = ExcelFileHandler.get_file_info(source_file_path)
                
                # Afficher les stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Lignes", ExcelFileHandler.format_number(file_info.get('rows', 0)))
                with col2:
                    st.metric("Colonnes", file_info.get('columns', 0))
                with col3:
                    size_mb = file_info.get('size', 0) / (1024 * 1024)
                    st.metric("Taille", f"{size_mb:.2f} MB")
                
                # Sélection de la feuille
                st.markdown("#### Feuille de calcul")
                sheet_names = file_info.get('sheet_names', [])
                
                if sheet_names:
                    selected_sheet = st.selectbox(
                        "Sélectionnez la feuille à traiter",
                        options=sheet_names,
                        key="source_sheet",
                        help="Feuille qui sera utilisée pour les traitements"
                    )
                    
                    st.session_state['source_sheet_path'] = selected_sheet
                    
                    # Option pour prévisualiser
                    if st.checkbox("Afficher un aperçu des données", key="preview_source"):
                        with st.spinner("Chargement des données..."):
                            df = ExcelFileHandler.read_excel(source_file_path, selected_sheet, nrows=50)
                            if df is not None:
                                ExcelFileHandler.preview_dataframe(df, "Aperçu du fichier source")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Retourner les deux noms pour compatibilité avec toutes les classes
                    return {
                        'source_file_path': source_file_path,
                        'source_sheet_path': selected_sheet,  # Pour CellDown
                        'source_sheet_name': selected_sheet   # Pour Ticket et OCM RAN
                    }
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return None
