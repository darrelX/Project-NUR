"""
Composant pour la carte OCM RAN
Support de plusieurs fichiers OCM (multi-horaires)
"""

import streamlit as st
from typing import Optional, Dict, List
import re
from utils.excel_utils import ExcelFileHandler, display_file_upload_info


def _extract_time_from_filename(filename: str) -> str:
    """Extrait l'heure UTC du nom de fichier (ex: 18H UTC, 13H UTC)"""
    match = re.search(r'(\d{1,2})[Hh]\s*UTC', filename)
    if match:
        return f"{match.group(1)}H UTC"
    return "UTC"


def render_ocm_card() -> Optional[Dict]:
    """
    Affiche la carte de configuration OCM RAN avec support multi-fichiers
    
    Returns:
        Dict avec la configuration OCM RAN ou None
    """
    st.markdown("### 📡 OCM RAN")
    
    with st.container():
        st.markdown('''
        <div class="custom-card">
            <div class="card-header">
                <div class="card-icon ocm-icon">📡</div>
                <h3 class="card-title">OCM RAN</h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Initialiser la liste de fichiers dans la session
        if 'ocm_files' not in st.session_state:
            st.session_state['ocm_files'] = []
        
        # Upload de fichiers OCM RAN (multiple)
        st.markdown("#### Fichiers OCM RAN")
        uploaded_files = st.file_uploader(
            "Fichier(s) Excel OCM RAN (vous pouvez en ajouter plusieurs)",
            type=['xlsx', 'xls'],
            key="ocm_file",
            accept_multiple_files=True,
            help="Fichier(s) contenant les données OCM RAN (ex: différentes heures UTC)"
        )
        
        configs = []
        
        if uploaded_files:
            # Traiter chaque fichier uploadé
            for uploaded_file in uploaded_files:
                with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                    display_file_upload_info(uploaded_file)
                    
                    # Sauvegarder le fichier
                    target_file_path = ExcelFileHandler.save_uploaded_file(uploaded_file)
                    
                    # Extraire l'heure du nom de fichier pour personnaliser
                    time_label = _extract_time_from_filename(uploaded_file.name)
                    
                    # Configuration pour ce fichier
                    file_key = uploaded_file.name.replace('.', '_').replace(' ', '_')
                    
                    config = {
                        'target_file_path': target_file_path,
                        'enabled': True,
                        'filename': uploaded_file.name
                    }
                    
                    # Paramètres avancés par fichier
                    with st.expander("⚙️ Paramètres avancés", expanded=False):
                        st.markdown("##### Colonne clé source")
                        source_key = st.text_input(
                            "Colonne clé dans le fichier source",
                            value="Codesite",
                            key=f"ocm_source_key_{file_key}",
                            help="Nom de la colonne contenant les identifiants sites"
                        )
                        config['source_key_column'] = source_key
                        
                        st.markdown("##### Colonnes clés cibles (alternatives)")
                        target_keys_str = st.text_area(
                            "Liste des noms de colonnes possibles (un par ligne)",
                            value="Site ID\nSITE_ID\nsite id\nSite Code",
                            key=f"ocm_target_keys_{file_key}",
                            help="Le système cherchera la première colonne correspondante"
                        )
                        target_keys = [k.strip() for k in target_keys_str.split('\n') if k.strip()]
                        config['target_key_column'] = target_keys
                        
                        st.markdown("##### Colonnes valeurs cibles (alternatives)")
                        target_values_str = st.text_area(
                            "Liste des noms de colonnes possibles (un par ligne)",
                            value="Actions en cours\nAction en cours\nActions\nCommentaire",
                            key=f"ocm_target_values_{file_key}",
                            help="Colonne dont on veut rapporter la valeur"
                        )
                        target_values = [v.strip() for v in target_values_str.split('\n') if v.strip()]
                        config['target_value_column'] = target_values
                        
                        st.markdown("##### Position du résultat")
                        result_pos = st.text_input(
                            "Position de la colonne résultat",
                            value="last_column",
                            key=f"ocm_result_pos_{file_key}",
                            help="'last_column' pour ajouter à la fin"
                        )
                        config['result_position_column'] = result_pos
                        
                        st.markdown("##### Nom de la colonne résultat")
                        result_name = st.text_input(
                            "Nom de la colonne résultat",
                            value=f"OCM RAN {time_label}",
                            key=f"ocm_result_name_{file_key}",
                            help="En-tête de la colonne créée"
                        )
                        config['result_column_name'] = result_name
                        
                        st.markdown("##### Feuille cible")
                        target_sheet = st.text_input(
                            "Nom de la feuille cible",
                            value="ALL SITES DOWN",
                            key=f"ocm_target_sheet_{file_key}",
                            help="Nom de la feuille à utiliser dans le fichier cible"
                        )
                        config['target_sheet_name'] = target_sheet
                        
                        st.markdown("##### Nom de référence")
                        ref_name = st.text_input(
                            "Nom de référence",
                            value="OCM RAN",
                            key=f"ocm_ref_name_{file_key}",
                            help="Préfixe ajouté aux valeurs"
                        )
                        config['reference_name'] = ref_name
                    
                    configs.append(config)
            
            # Stocker dans la session
            st.session_state['ocm_config'] = {
                'enabled': True,
                'files': configs,
                'count': len(configs)
            }
            
            # Afficher un résumé
            st.success(f"✅ {len(configs)} fichier(s) OCM RAN configuré(s)")
            
            return st.session_state['ocm_config']
        else:
            st.session_state['ocm_config'] = {'enabled': False, 'files': [], 'count': 0}
    
    return None
