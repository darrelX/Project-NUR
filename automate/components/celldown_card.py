"""
Composant pour la carte CellDown
Support de plusieurs fichiers CellDown (multi-vendors: Nokia, Huawei, ZTE)
"""

import streamlit as st
from typing import Optional, Dict, List
import re
from datetime import datetime
from utils.excel_utils import ExcelFileHandler, display_file_upload_info, create_date_picker_with_format


def _extract_vendor_from_filename(filename: str) -> str:
    """Extrait le nom du vendor du nom de fichier (Nokia, Huawei, ZTE, etc.)"""
    vendors = ['NOKIA', 'HUAWEI', 'ZTE', 'ERICSSON', 'SAMSUNG']
    filename_upper = filename.upper()
    
    for vendor in vendors:
        if vendor in filename_upper:
            return vendor.title()
    
    # Si pas de vendor trouvé, chercher après "CELLS_DOWN_" ou "CELLDOWN_"
    match = re.search(r'CELLS?[_ ]DOWN[_ ]+([A-Za-z]+)', filename, re.IGNORECASE)
    if match:
        return match.group(1).title()
    
    return "Unknown"


def render_celldown_card() -> Optional[Dict]:
    """
    Affiche la carte de configuration CellDown avec support multi-fichiers
    
    Returns:
        Dict avec la configuration CellDown ou None
    """
    st.markdown("### 📱 CellDown")
    
    with st.container():
        st.markdown('''
        <div class="custom-card">
            <div class="card-header">
                <div class="card-icon celldown-icon">📱</div>
                <h3 class="card-title">CellDown</h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Initialiser la liste de fichiers dans la session
        if 'celldown_files' not in st.session_state:
            st.session_state['celldown_files'] = []
        
        # Upload de fichiers CellDown (multiple)
        st.markdown("#### Fichiers CellDown")
        uploaded_files = st.file_uploader(
            "Fichier(s) Excel CellDown (vous pouvez en ajouter plusieurs pour chaque vendor)",
            type=['xlsx', 'xls'],
            key="celldown_file",
            accept_multiple_files=True,
            help="Fichier(s) contenant les données de cells down (ex: Nokia, Huawei, ZTE)"
        )
        
        # Date commune pour tous les fichiers CellDown
        st.markdown("#### Date de filtrage")
        date_str = st.text_input(
            "Date (format DDMMYYYY)",
            value=datetime.now().strftime("%d%m%Y"),
            key="celldown_date",
            help="Format: DDMMYYYY (ex: 12062026 pour le 12 juin 2026)"
        )
        
        # Date de référence
        st.markdown("#### Date de référence")
        reference_date = st.text_input(
            "Date de référence (format DD/MM/YYYY)",
            value=datetime.now().strftime("%d/%m/%Y"),
            key="celldown_ref_date",
            help="Format: DD/MM/YYYY (ex: 12/06/2026)"
        )
        
        configs = []
        
        if uploaded_files:
            # Traiter chaque fichier uploadé
            for uploaded_file in uploaded_files:
                with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                    display_file_upload_info(uploaded_file)
                    
                    # Sauvegarder le fichier
                    target_file_path = ExcelFileHandler.save_uploaded_file(uploaded_file)
                    
                    # Extraire le vendor du nom de fichier
                    vendor = _extract_vendor_from_filename(uploaded_file.name)
                    
                    # Configuration pour ce fichier
                    file_key = uploaded_file.name.replace('.', '_').replace(' ', '_')
                    
                    config = {
                        'target_file_path': target_file_path,
                        'enabled': True,
                        'filename': uploaded_file.name,
                        'date_str': date_str,
                        'reference_date': reference_date
                    }
                    
                    # Paramètres avancés par fichier
                    with st.expander("⚙️ Paramètres avancés", expanded=False):
                        st.markdown("##### Colonne clé source")
                        colown_key = st.text_input(
                            "Colonne clé dans le fichier source",
                            value="Codesite",
                            key=f"celldown_source_key_{file_key}",
                            help="Nom de la colonne contenant les identifiants dans le fichier source"
                        )
                        config['colown_key_path_source'] = colown_key
                        
                        st.markdown("##### Colonnes clés cibles (alternatives)")
                        target_keys_str = st.text_area(
                            "Liste des noms de colonnes possibles (un par ligne)",
                            value="Site Code\nSITE_CODE\nsite code\nCode Site",
                            key=f"celldown_target_keys_{file_key}",
                            help="Le système cherchera la première colonne correspondante"
                        )
                        target_keys = [k.strip() for k in target_keys_str.split('\n') if k.strip()]
                        config['target_key_column'] = target_keys
                        
                        st.markdown("##### Colonnes valeurs cibles (alternatives)")
                        target_values_str = st.text_area(
                            "Liste des noms de colonnes possibles (un par ligne)",
                            value="Comment\nCOMMENT\ncomment\nCommentaire",
                            key=f"celldown_target_values_{file_key}",
                            help="Colonne dont on veut rapporter la valeur"
                        )
                        target_values = [v.strip() for v in target_values_str.split('\n') if v.strip()]
                        config['target_value_column'] = target_values
                        
                        st.markdown("##### Position du résultat")
                        result_pos = st.text_input(
                            "Position de la colonne résultat",
                            value="last_column",
                            key=f"celldown_result_pos_{file_key}",
                            help="'last_column' pour ajouter à la fin"
                        )
                        config['result_position_column'] = result_pos
                        
                        st.markdown("##### Nom de référence")
                        ref_name = st.text_input(
                            "Nom de référence",
                            value=f"CellDown {vendor}",
                            key=f"celldown_ref_name_{file_key}",
                            help="Préfixe ajouté aux valeurs (détecté automatiquement du nom de fichier)"
                        )
                        config['reference_name'] = ref_name
                        
                        st.markdown("##### Feuille cible")
                        target_sheet = st.text_input(
                            "Nom de la feuille cible (optionnel)",
                            value="",
                            key=f"celldown_target_sheet_{file_key}",
                            help="Laissez vide pour utiliser la première feuille"
                        )
                        config['target_sheet_name'] = target_sheet if target_sheet else None
                    
                    configs.append(config)
            
            # Stocker dans la session
            st.session_state['celldown_config'] = {
                'enabled': True,
                'files': configs,
                'count': len(configs)
            }
            
            # Afficher un résumé
            st.success(f"✅ {len(configs)} fichier(s) CellDown configuré(s)")
            
            return st.session_state['celldown_config']
        else:
            st.session_state['celldown_config'] = {'enabled': False, 'files': [], 'count': 0}
    
    return None
