"""
Composant pour la carte Dashboard Celldown
Traitement XLOOKUP avec filtrage par date/pattern sur plusieurs feuilles
"""

import streamlit as st
from typing import Optional, Dict
from datetime import datetime


def render_dashboard_celldown_card() -> Optional[Dict]:
    """
    Affiche la carte de configuration Dashboard Celldown
    
    Returns:
        Dict avec la configuration Dashboard Celldown ou None
    """
    st.markdown("### 📊 Dashboard Celldown")
    
    with st.container():
        st.markdown('''
        <div class="custom-card">
            <div class="card-header">
                <div class="card-icon dashboard-icon">📊</div>
                <h3 class="card-title">Dashboard Celldown</h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Upload du fichier cible Dashboard
        st.markdown("#### Fichier Dashboard")
        uploaded_file = st.file_uploader(
            "Fichier Excel Dashboard (ex: Dashbord suivi TOP OFFENDERS)",
            type=['xlsx', 'xls'],
            key="dashboard_celldown_file",
            help="Fichier Dashboard contenant plusieurs feuilles avec des dates/patterns"
        )
        
        # Date/Pattern de filtrage (OBLIGATOIRE)
        st.markdown("#### 🔴 Date/Pattern de filtrage (obligatoire)")
        date_str = st.text_input(
            "Date ou pattern de recherche *",
            value="",
            key="dashboard_date_str",
            placeholder="Ex: 1906 ou 19062026",
            help="⚠️ OBLIGATOIRE - Format: DDMMYYYY (ex: 19062026) ou pattern (ex: 1906 pour 'Top 1906')"
        )
        
        # Validation du champ obligatoire
        if date_str.strip() == "":
            st.error("⚠️ Le champ Date/Pattern est obligatoire !")
        else:
            st.success(f"✓ Pattern de recherche : '{date_str}'")
        
        # Feuille cible
        st.markdown("#### Feuille source (optionnelle)")
        target_sheet_name = st.text_input(
            "Nom de la feuille cible (laisser vide pour la première)",
            value="",
            key="dashboard_target_sheet",
            help="Optionnel: nom de la feuille dans le fichier Dashboard"
        )
        
        # Colonnes de recherche
        st.markdown("#### Configuration des colonnes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            source_key_column = st.text_input(
                "Colonne clé source",
                value="Codesite",
                key="dashboard_source_key",
                help="Nom de la colonne clé dans le fichier source"
            )
            
            target_key_column = st.text_input(
                "Colonne(s) clé cible (séparées par virgule)",
                value="Codesite, Site Code, SITE_CODE",
                key="dashboard_target_key",
                help="Liste de noms possibles pour la colonne clé dans les feuilles cibles"
            )
        
        with col2:
            target_value_column = st.text_input(
                "Colonne(s) valeur cible (séparées par virgule)",
                value="Comment, COMMENT, comment",
                key="dashboard_value_col",
                help="Liste de noms possibles pour la colonne à rapporter"
            )
            
            start_column = st.text_input(
                "Position de départ",
                value="last_column",
                key="dashboard_start_col",
                help="'last_column' ou lettre Excel (ex: C) ou numéro (ex: 3)"
            )
        
        # Date de référence
        st.markdown("#### Date de référence")
        reference_date = st.text_input(
            "Date de référence (format DD/MM/YYYY)",
            value=datetime.now().strftime("%d/%m/%Y"),
            key="dashboard_ref_date",
            help="Format: DD/MM/YYYY (ex: 19/06/2026)"
        )
        
        # Validation et retour de la configuration
        if uploaded_file and date_str.strip() != "":
            # Sauvegarder le fichier temporairement
            import tempfile
            from pathlib import Path
            
            temp_dir = Path(tempfile.gettempdir()) / "automate_uploads"
            temp_dir.mkdir(exist_ok=True)
            
            target_file_path = temp_dir / uploaded_file.name
            with open(target_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Parse les colonnes séparées par virgule
            target_key_list = [col.strip() for col in target_key_column.split(",") if col.strip()]
            target_value_list = [col.strip() for col in target_value_column.split(",") if col.strip()]
            
            config = {
                'enabled': True,
                'target_file_path': str(target_file_path),
                'date_str': date_str.strip(),
                'source_key_column': source_key_column.strip(),
                'target_key_column': target_key_list,
                'target_value_column': target_value_list,
                'start_column': start_column.strip(),
                'target_sheet_name': target_sheet_name.strip() if target_sheet_name.strip() else None,
                'reference_date': reference_date.strip()
            }
            
            # Stocker dans session_state
            st.session_state['dashboard_celldown_config'] = config
            
            st.success("✓ Configuration Dashboard Celldown prête")
            return config
        
        elif uploaded_file and date_str.strip() == "":
            st.error("⚠️ Veuillez renseigner le champ Date/Pattern obligatoire")
            st.session_state['dashboard_celldown_config'] = {'enabled': False}
            return None
        else:
            st.info("⏳ En attente du fichier Dashboard et de la date/pattern")
            st.session_state['dashboard_celldown_config'] = {'enabled': False}
            return None
