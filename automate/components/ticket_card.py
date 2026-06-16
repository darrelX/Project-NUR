"""
Composant pour la carte Ticket
"""

import streamlit as st
from typing import Optional, Dict
from utils.excel_utils import ExcelFileHandler, display_file_upload_info


def render_ticket_card() -> Optional[Dict]:
    """
    Affiche la carte de configuration Ticket
    
    Returns:
        Dict avec la configuration Ticket ou None
    """
    st.markdown("### 🎫 Ticket")
    
    with st.container():
        st.markdown('''
        <div class="custom-card">
            <div class="card-header">
                <div class="card-icon ticket-icon">🎫</div>
                <h3 class="card-title">Ticket</h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Upload du fichier Ticket
        st.markdown("#### Fichier Ticket")
        uploaded_file = st.file_uploader(
            "Fichier Excel Ticket",
            type=['xlsx', 'xls'],
            key="ticket_file",
            help="Fichier contenant les données de tickets"
        )
        
        config = {}
        
        if uploaded_file is not None:
            display_file_upload_info(uploaded_file)
            
            # Sauvegarder le fichier
            target_file_path = ExcelFileHandler.save_uploaded_file(uploaded_file)
            config['target_file_path'] = target_file_path
            config['enabled'] = True
            
            # Paramètres avancés
            with st.expander("⚙️ Paramètres avancés"):
                st.markdown("##### Colonne clé source")
                source_key = st.text_input(
                    "Colonne clé dans le fichier source",
                    value="Codesite",
                    key="ticket_source_key",
                    help="Nom de la colonne (ex: 'Codesite') ou lettre (ex: 'B')"
                )
                config['source_key_column'] = source_key
                
                st.markdown("##### Position du résultat")
                result_pos = st.text_input(
                    "Position de la colonne résultat",
                    value="last_free",
                    key="ticket_result_pos",
                    help="'last_free' pour trouver la première colonne vide, ou spécifiez une lettre"
                )
                config['result_position_column'] = result_pos
                
                st.markdown("##### Nom de la colonne résultat")
                result_name = st.text_input(
                    "Nom de la colonne résultat",
                    value="Ticket",
                    key="ticket_result_name",
                    help="En-tête de la colonne créée"
                )
                config['result_column_name'] = result_name
                
                st.markdown("##### Nom de référence")
                ref_name = st.text_input(
                    "Nom de référence pour le préfixe",
                    value="Ticket",
                    key="ticket_ref_name",
                    help="Utilisé pour le préfixe [NOM - date]"
                )
                config['reference_name'] = ref_name
                
                st.markdown("##### Colonnes à concaténer (TEXTJOIN)")
                st.caption("Format : Nom1 | Alternative1 | Alternative2 (séparés par |, un groupe par ligne)")
                join_cols_str = st.text_area(
                    "Liste des colonnes à concaténer avec alternatives",
                    value="Ticket ID | Ticket ID(Create TT)\nDescription | Description(Process TT)\nSolution | Solution(Process TT)\nRoot Cause | Root Cause(Process TT)\nIncident Reason | Incident Reason Detail(Process TT)",
                    key="ticket_join_cols",
                    help="Chaque ligne peut avoir plusieurs noms alternatifs séparés par |"
                )
                # Parser les colonnes avec alternatives
                join_cols = []
                for line in join_cols_str.split('\n'):
                    if line.strip():
                        alternatives = [alt.strip() for alt in line.split('|') if alt.strip()]
                        if alternatives:
                            join_cols.append(alternatives if len(alternatives) > 1 else alternatives[0])
                config['target_join_columns'] = join_cols
                
                st.markdown("##### Séparateur")
                separator = st.text_input(
                    "Séparateur pour TEXTJOIN",
                    value="..",
                    key="ticket_separator",
                    help="Caractère(s) utilisé(s) pour séparer les valeurs"
                )
                config['join_separator'] = separator
                
                st.markdown("##### Options")
                ignore_empty = st.checkbox(
                    "Ignorer les cellules vides",
                    value=True,
                    key="ticket_ignore_empty",
                    help="Ne pas inclure les cellules vides dans la concaténation"
                )
                config['ignore_empty'] = ignore_empty
                
                st.markdown("##### Colonnes d'extraction (alternatives)")
                extract_cols_str = st.text_area(
                    "Liste des colonnes pour extraction (un par ligne)",
                    value="Site Name\nSite ID\nSITE_ID\nsite id\nsite_code\nsite code",
                    key="ticket_extract_cols",
                    help="Colonnes où chercher les codes sites (préfixes CTR_, SUO_, etc.)"
                )
                extract_cols = [c.strip() for c in extract_cols_str.split('\n') if c.strip()]
                config['extract_source_column'] = extract_cols
                
                st.markdown("##### Feuille cible")
                target_sheet = st.text_input(
                    "Nom de la feuille cible (optionnel)",
                    value="",
                    key="ticket_target_sheet",
                    help="Laissez vide pour utiliser la première feuille"
                )
                config['target_sheet_name'] = target_sheet if target_sheet else ''
            
            # Stocker dans la session
            st.session_state['ticket_config'] = config
            
            return config
        else:
            config['enabled'] = False
            st.session_state['ticket_config'] = config
    
    return None
