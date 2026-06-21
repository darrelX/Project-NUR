"""
Composant pour la carte Hourly IHS
Traitement XLOOKUP avec extraction de codes sites et TEXTJOIN
"""

import streamlit as st
from typing import Optional, Dict
from datetime import datetime


def render_hourly_ihs_card() -> Optional[Dict]:
    """
    Affiche la carte de configuration Hourly IHS
    
    Returns:
        Dict avec la configuration Hourly IHS ou None
    """
    st.markdown("### ⏰ Hourly IHS")
    
    with st.container():
        st.markdown('''
        <div class="custom-card">
            <div class="card-header">
                <div class="card-icon ihs-icon">⏰</div>
                <h3 class="card-title">Hourly IHS</h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Upload du fichier cible Hourly IHS
        st.markdown("#### Fichier Hourly IHS")
        uploaded_file = st.file_uploader(
            "Fichier Excel Hourly IHS",
            type=['xlsx', 'xls'],
            key="hourly_ihs_file",
            help="Fichier Hourly IHS contenant les événements horaires"
        )
        
        # Configuration de base
        st.markdown("#### Configuration de la feuille cible")
        
        target_sheet_name = st.text_input(
            "Feuille cible (optionnelle)",
            value="ALL",
            key="hourly_target_sheet",
            help="Nom de la feuille dans le fichier Hourly IHS (laissez vide pour la première feuille)"
        )
        
        # Colonnes de recherche
        st.markdown("#### Configuration des colonnes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            source_key_column = st.text_input(
                "Colonne(s) clé source (séparées par virgule)",
                value="code site, site code, site id",
                key="hourly_source_key",
                help="Liste de noms possibles pour la colonne clé source"
            )
            
            target_key_column = st.text_input(
                "Colonne(s) clé cible (séparées par virgule)",
                value="Short description, Duration, Outage Start Time",
                key="hourly_target_key",
                help="Liste de noms possibles pour la colonne clé cible"
            )
        
        with col2:
            result_position = st.text_input(
                "Position du résultat",
                value="last_free",
                key="hourly_result_pos",
                help="'last_free' ou lettre Excel (ex: C) ou numéro (ex: 3)"
            )
            
            result_column_name = st.text_input(
                "Nom de la colonne résultat",
                value="Hourly IHS",
                key="hourly_result_name",
                help="Nom de la nouvelle colonne à créer"
            )
        
        # Configuration TEXTJOIN
        st.markdown("#### Configuration TEXTJOIN")
        st.info("💡 Les colonnes suivantes seront concaténées avec le séparateur ' .. '")
        
        join_columns = st.text_area(
            "Colonnes à joindre (une par ligne)",
            value="Event time\nDuration\nCMS\nLast Timeline Message\nShort description",
            key="hourly_join_cols",
            help="Liste des colonnes à concaténer (TEXTJOIN)"
        )
        
        # Nom de référence et date
        st.markdown("#### Identification")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reference_name = st.text_input(
                "Nom de référence",
                value="Hourly IHS",
                key="hourly_ref_name",
                help="Nom utilisé pour le préfixe des résultats"
            )
        
        with col2:
            reference_date = st.text_input(
                "Date de référence (optionnelle)",
                value="",
                key="hourly_ref_date",
                placeholder="Laissez vide pour date du jour",
                help="Format: YYYY-MM-DD (vide = date du jour)"
            )
        
        # Validation et retour de la configuration
        if uploaded_file:
            # Sauvegarder le fichier temporairement
            import tempfile
            from pathlib import Path
            
            temp_dir = Path(tempfile.gettempdir()) / "automate_uploads"
            temp_dir.mkdir(exist_ok=True)
            
            target_file_path = temp_dir / uploaded_file.name
            with open(target_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Parse les colonnes
            source_key_list = [col.strip() for col in source_key_column.split(",") if col.strip()]
            target_key_list = [col.strip() for col in target_key_column.split(",") if col.strip()]
            join_cols_list = [line.strip() for line in join_columns.split("\n") if line.strip()]
            
            config = {
                'enabled': True,
                'target_file_path': str(target_file_path),
                'target_sheet_name': target_sheet_name.strip() if target_sheet_name.strip() else "",
                'source_key_column': source_key_list,
                'target_key_column': target_key_list,
                'result_position_column': result_position.strip(),
                'result_column_name': result_column_name.strip(),
                'target_join_columns': join_cols_list,
                'join_separator': " .. ",
                'ignore_empty': True,
                'reference_name': reference_name.strip(),
                'reference_date': reference_date.strip() if reference_date.strip() else None
            }
            
            # Stocker dans session_state
            st.session_state['hourly_ihs_config'] = config
            
            st.success("✓ Configuration Hourly IHS prête")
            return config
        else:
            st.info("⏳ En attente du fichier Hourly IHS")
            st.session_state['hourly_ihs_config'] = {'enabled': False}
            return None
