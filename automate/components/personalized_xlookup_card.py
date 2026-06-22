"""
Composant pour la carte Personalized XLOOKUP
XLOOKUP personnalisé avec extraction automatique de codes sites
"""

import streamlit as st
from typing import Optional, Dict


def render_personalized_xlookup_card() -> Optional[Dict]:
    """
    Affiche la carte de configuration Personalized XLOOKUP
    
    Returns:
        Dict avec la configuration ou None
    """
    st.markdown("### 🔍 Personalized XLOOKUP")
    
    with st.container():
        st.markdown('''
        <div class="custom-card">
            <div class="card-header">
                <div class="card-icon">🔍</div>
                <h3 class="card-title">Personalized XLOOKUP</h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Initialiser la config dans la session
        if 'personalized_xlookup_config' not in st.session_state:
            st.session_state['personalized_xlookup_config'] = {'enabled': False}
        
        # Checkbox d'activation
        enabled = st.checkbox(
            "Activer Personalized XLOOKUP",
            value=st.session_state['personalized_xlookup_config'].get('enabled', False),
            key="personalized_xlookup_enabled",
            help="XLOOKUP avec extraction automatique de codes sites et TEXTJOIN"
        )
        
        if not enabled:
            st.session_state['personalized_xlookup_config']['enabled'] = False
            return None
        
        st.markdown("---")
        
        # Fichier cible (target)
        st.markdown("#### 📁 Fichier de référence (Target)")
        target_file = st.file_uploader(
            "Fichier Excel de référence",
            type=['xlsx', 'xls'],
            key="personalized_xlookup_target",
            help="Fichier contenant les données à rechercher"
        )
        
        # Nom de la feuille cible
        target_sheet_name = st.text_input(
            "Nom de la feuille cible",
            value="Sheet1",
            key="personalized_xlookup_target_sheet",
            help="Nom de la feuille dans le fichier de référence (laisser vide pour la première feuille)"
        )
        
        st.markdown("---")
        
        # Configuration du résultat
        st.markdown("#### ⚙️ Configuration du résultat")
        
        col1, col2 = st.columns(2)
        
        with col1:
            result_column_name = st.text_input(
                "Nom de la colonne résultat",
                value="Résultat XLOOKUP",
                key="personalized_xlookup_result_name",
                help="Nom de la nouvelle colonne qui sera créée"
            )
        
        with col2:
            reference_name = st.text_input(
                "Nom de référence",
                value="",
                key="personalized_xlookup_reference_name",
                help="Préfixe pour les résultats (ex: 'Top Offenders')"
            )
        
        st.markdown("---")
        
        # Configuration avancée (repliable)
        with st.expander("⚙️ Configuration avancée", expanded=False):
            st.markdown("##### Colonnes cibles pour TEXTJOIN")
            st.info("💡 Si aucune colonne n'est spécifiée, la première colonne disponible sera utilisée automatiquement.", icon="ℹ️")
            
            # Colonnes à concaténer
            join_columns_input = st.text_input(
                "Colonnes à concaténer (séparées par des virgules)",
                value="",
                key="personalized_xlookup_join_columns",
                help="Noms des colonnes à concaténer avec TEXTJOIN (ex: 'Comment, Status'). Laissez vide pour une sélection automatique."
            )
            
            # Séparateur
            join_separator = st.text_input(
                "Séparateur TEXTJOIN",
                value=" .. ",
                key="personalized_xlookup_separator",
                help="Caractère(s) de séparation entre les valeurs concaténées"
            )
            
            # Position de la colonne résultat
            result_position = st.text_input(
                "Position de la colonne résultat",
                value="last_free",
                key="personalized_xlookup_result_position",
                help="Position où insérer la colonne (last_free, numéro, ou lettre Excel)"
            )
            
            st.markdown("---")
            st.markdown("##### Extraction des codes sites")
            
            # Préfixes pour l'extraction
            extract_prefixes = st.text_input(
                "Préfixes de codes sites (séparés par des virgules)",
                value="ABC",
                key="personalized_xlookup_prefixes",
                help="Préfixes à rechercher pour extraire les codes sites (ex: 'ABC, DEF, GHI')"
            )
            
            # Colonne d'extraction
            extract_column = st.text_input(
                "Colonne source pour extraction",
                value="",
                key="personalized_xlookup_extract_column",
                help="Nom de la colonne où chercher les codes sites (optionnel)"
            )
        
        # Bouton de validation
        st.markdown("---")
        if st.button("💾 Sauvegarder la configuration", key="save_personalized_xlookup", use_container_width=True):
            # Valider la configuration
            if not target_file:
                st.error("⚠️ Veuillez sélectionner un fichier de référence")
                return None
            
            if not result_column_name.strip():
                st.error("⚠️ Veuillez spécifier un nom pour la colonne résultat")
                return None
            
            # Préparer la liste des colonnes à joindre
            join_columns_list = []
            if join_columns_input.strip():
                join_columns_list = [col.strip() for col in join_columns_input.split(',') if col.strip()]
            
            # Préparer la liste des préfixes
            prefixes_list = [p.strip() for p in extract_prefixes.split(',') if p.strip()]
            
            # Créer la configuration
            config = {
                'enabled': True,
                'target_file': target_file,
                'target_sheet_name': target_sheet_name.strip(),
                'result_column_name': result_column_name.strip(),
                'reference_name': reference_name.strip(),
                'join_columns': join_columns_list,
                'join_separator': join_separator,
                'result_position': result_position.strip(),
                'extract_prefixes': prefixes_list,
                'extract_column': extract_column.strip() if extract_column.strip() else None
            }
            
            st.session_state['personalized_xlookup_config'] = config
            st.success("✅ Configuration sauvegardée")
            
            return config
        
        # Afficher l'aperçu de la configuration actuelle
        if st.session_state['personalized_xlookup_config'].get('enabled'):
            st.markdown("---")
            st.markdown("#### 📋 Configuration actuelle")
            config = st.session_state['personalized_xlookup_config']
            
            st.markdown(f"""
            - **Fichier cible** : {config.get('target_file').name if config.get('target_file') else 'Non défini'}
            - **Feuille cible** : {config.get('target_sheet_name', 'Sheet1')}
            - **Colonne résultat** : {config.get('result_column_name', 'N/A')}
            - **Référence** : {config.get('reference_name', 'Non défini')}
            - **Colonnes TEXTJOIN** : {', '.join(config.get('join_columns', [])) if config.get('join_columns') else 'Aucune'}
            - **Séparateur** : `{config.get('join_separator', '..')}`
            """)
        
        return st.session_state['personalized_xlookup_config'] if enabled else None
