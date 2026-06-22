"""
Page Traitement Excel - Configuration et exécution des moteurs
"""

import streamlit as st
import sys
from pathlib import Path

# Ajouter le dossier parent au path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import des composants
from components.source_panel import render_source_panel
from components.celldown_card import render_celldown_card
from components.ticket_card import render_ticket_card
from components.ocm_card import render_ocm_card
from components.dashboard_celldown_card import render_dashboard_celldown_card
from components.hourly_ihs_card import render_hourly_ihs_card
from components.personalized_xlookup_card import render_personalized_xlookup_card
from components.execution_panel import render_execution_panel
from components.preview_panel import render_preview_panel

# Import des utilitaires
from utils.styles import get_custom_css


# Configuration de la page
st.set_page_config(
    page_title="Traitement Excel - NUR Project",
    page_icon="📊",
    layout="wide"
)

# Appliquer les styles CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Titre de la page
st.markdown("# 📊 Traitement Excel")
st.markdown("Configuration et exécution des moteurs de traitement")

st.markdown("---")

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

col4, col5, col6 = st.columns(3)

with col4:
    dashboard_celldown_config = render_dashboard_celldown_card()

with col5:
    hourly_ihs_config = render_hourly_ihs_card()

with col6:
    personalized_xlookup_config = render_personalized_xlookup_card()

# Section 3 : Exécution
render_execution_panel(
    source_config=st.session_state.get('source_config'),
    celldown_config=st.session_state.get('celldown_config'),
    ticket_config=st.session_state.get('ticket_config'),
    ocm_config=st.session_state.get('ocm_config'),
    dashboard_celldown_config=st.session_state.get('dashboard_celldown_config'),
    hourly_ihs_config=st.session_state.get('hourly_ihs_config'),
    personalized_xlookup_config=st.session_state.get('personalized_xlookup_config')
)

# Section 4 : Prévisualisation
if st.session_state.get('source_config'):
    render_preview_panel(st.session_state.get('source_config'))
