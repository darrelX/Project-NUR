"""
Page Assistant IA - Chat avec LLM distant
"""

import streamlit as st
import sys
from pathlib import Path

# Ajouter le dossier parent au path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import du composant chat
from components.chat_panel import render_chat_panel

# Import des utilitaires
from utils.styles import get_custom_css


# Configuration de la page
st.set_page_config(
    page_title="Assistant IA - NUR Project",
    page_icon="💬",
    layout="wide"
)

# Appliquer les styles CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Titre de la page
st.markdown("# 💬 Assistant IA")
st.markdown("Discutez avec l'assistant pour obtenir de l'aide sur vos données Excel")

st.markdown("---")

# Rendre le panneau de chat
render_chat_panel()
