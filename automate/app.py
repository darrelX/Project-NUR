"""
Application Streamlit principale - Plateforme de traitement Excel
Exécution des moteurs CellDown, Ticket et OCM RAN

Auteur: NUR Project Lyne
Version: 1.0
"""

import streamlit as st
import sys
from pathlib import Path

# Ajouter le dossier automate au path
sys.path.insert(0, str(Path(__file__).parent))

# Import des composants
from components.source_panel import render_source_panel
from components.celldown_card import render_celldown_card
from components.ticket_card import render_ticket_card
from components.ocm_card import render_ocm_card
from components.dashboard_celldown_card import render_dashboard_celldown_card
from components.hourly_ihs_card import render_hourly_ihs_card
from components.execution_panel import render_execution_panel
from components.preview_panel import render_preview_panel
from components.chat_panel import render_chat_panel

# Import des utilitaires
from utils.styles import get_custom_css, get_header_html


def initialize_session_state():
    """Initialise les variables de session"""
    if 'source_file_path' not in st.session_state:
        st.session_state['source_file_path'] = None
    if 'source_sheet_path' not in st.session_state:
        st.session_state['source_sheet_path'] = None
    if 'celldown_config' not in st.session_state:
        st.session_state['celldown_config'] = {'enabled': False, 'files': [], 'count': 0}
    if 'ticket_config' not in st.session_state:
        st.session_state['ticket_config'] = {'enabled': False}
    if 'ocm_config' not in st.session_state:
        st.session_state['ocm_config'] = {'enabled': False, 'files': [], 'count': 0}
    if 'dashboard_celldown_config' not in st.session_state:
        st.session_state['dashboard_celldown_config'] = {'enabled': False}
    if 'hourly_ihs_config' not in st.session_state:
        st.session_state['hourly_ihs_config'] = {'enabled': False}


def main():
    """Fonction principale de l'application"""
    
    # Configuration de la page
    st.set_page_config(
        page_title="Plateforme Excel - CellDown, Ticket, OCM RAN",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialiser la session
    initialize_session_state()
    
    # Appliquer les styles CSS personnalisés
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Header principal
    st.markdown(get_header_html(), unsafe_allow_html=True)
    
    # Sidebar avec informations
    with st.sidebar:
        st.markdown("## ℹ️ Information")
        st.markdown("""
        Cette application permet d'exécuter trois moteurs de traitement Excel :
        
        - **📱 CellDown** : Filtrage et enrichissement par date
        - **🎫 Ticket** : Extraction et liaison de tickets
        - **📡 OCM RAN** : Recherche et correspondance OCM
        - **� Dashboard Celldown** : XLOOKUP multi-feuilles avec filtrage date/pattern
        - **⏰ Hourly IHS** : Extraction et TEXTJOIN d'événements horaires
        - **�💬 Assistant IA** : Aide et analyse avec LLM
        
        ### Mode d'emploi
        1. Chargez votre fichier source principal
        2. Sélectionnez la feuille à traiter
        3. Configurez les catégories souhaitées
        4. Prévisualisez les correspondances
        5. Lancez l'exécution
        6. Discutez avec l'assistant IA
        """)
        
        st.markdown("---")
        
        st.markdown("### 📊 Statistiques")
        
        # Compter les catégories actives
        active_categories = 0
        
        celldown_count = st.session_state['celldown_config'].get('count', 0)
        if celldown_count > 0:
            active_categories += celldown_count
        
        if st.session_state['ticket_config'].get('enabled', False):
            active_categories += 1
        
        ocm_count = st.session_state['ocm_config'].get('count', 0)
        if ocm_count > 0:
            active_categories += ocm_count
        
        if st.session_state['dashboard_celldown_config'].get('enabled', False):
            active_categories += 1
        
        if st.session_state['hourly_ihs_config'].get('enabled', False):
            active_categories += 1
        
        st.metric("Traitements actifs", active_categories)
        
        if st.session_state.get('source_file_path'):
            st.success("✅ Source configurée")
        else:
            st.warning("⏳ Source à configurer")
        
        st.markdown("---")
        
        st.markdown("### 🔧 Actions")
        
        if st.button("🔄 Réinitialiser", use_container_width=True):
            # Effacer toute la session
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.caption("NUR Project Lyne © 2026")
    
    # Créer des onglets pour séparer les fonctionnalités
    tab1, tab2 = st.tabs(["📊 Traitement Excel", "💬 Assistant IA"])
    
    with tab1:
        # ONGLET TRAITEMENT EXCEL
        # Section 1 : Configuration de la source principale
        source_config = render_source_panel()
        
        # Stocker la config source dans la session
        if source_config:
            st.session_state['source_config'] = source_config
        
        st.markdown("---")
        
        # Section 2 : Catégories de traitement
        st.markdown("## 📋 Catégories de traitement")
        st.markdown("Configurez les moteurs de traitement à exécuter")
        
        # Afficher les 3 cartes principales côte à côte
        col1, col2, col3 = st.columns(3)
        
        with col1:
            celldown_config = render_celldown_card()
        
        with col2:
            ticket_config = render_ticket_card()
        
        with col3:
            ocm_config = render_ocm_card()
        
        # Afficher les 2 nouvelles cartes : Dashboard Celldown et Hourly IHS
        st.markdown("---")
        st.markdown("### 🆕 Traitements supplémentaires")
        
        col4, col5 = st.columns(2)
        
        with col4:
            dashboard_celldown_config = render_dashboard_celldown_card()
        
        with col5:
            hourly_ihs_config = render_hourly_ihs_card()
        
        # Section 3 : Exécution
        render_execution_panel(
            source_config=st.session_state.get('source_config'),
            celldown_config=st.session_state.get('celldown_config'),
            ticket_config=st.session_state.get('ticket_config'),
            ocm_config=st.session_state.get('ocm_config'),
            dashboard_celldown_config=st.session_state.get('dashboard_celldown_config'),
            hourly_ihs_config=st.session_state.get('hourly_ihs_config')
        )
        
        # Section 4 : Prévisualisation
        if st.session_state.get('source_config'):
            render_preview_panel(st.session_state.get('source_config'))
    
    with tab2:
        # ONGLET ASSISTANT IA
        render_chat_panel()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; padding: 2rem;">
        <p>Plateforme de traitement Excel | NUR Project Lyne | Version 1.0</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
