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

# Import des utilitaires
from utils.styles import get_custom_css


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
    if 'personalized_xlookup_config' not in st.session_state:
        st.session_state['personalized_xlookup_config'] = {'enabled': False}


def main():
    """Fonction principale de l'application"""
    
    # Configuration de la page
    st.set_page_config(
        page_title="Plateforme Excel - NUR Project Lyne",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialiser la session
    initialize_session_state()
    
    # Appliquer les styles CSS personnalisés
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Page d'accueil
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="color: #1e40af; font-size: 3rem; margin-bottom: 1rem;">🚀 Plateforme Excel NUR</h1>
        <p style="font-size: 1.2rem; color: #64748b; margin-bottom: 2rem;">
            Automatisation et traitement intelligent de fichiers Excel
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Message d'information pour la navigation
    st.info("👈 **Utilisez le menu latéral à gauche** pour naviguer entre les pages ou cliquez sur les boutons ci-dessous", icon="ℹ️")
    
    st.markdown("---")
    
    # Présentation des fonctionnalités
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Traitement Excel
        
        Accédez aux puissants moteurs de traitement :
        
        - **📱 CellDown** : Filtrage et enrichissement par date
        - **🎫 Ticket** : Extraction et liaison de tickets
        - **📡 OCM RAN** : Recherche et correspondance OCM
        - **📊 Dashboard Celldown** : XLOOKUP multi-feuilles avec filtrage
        - **⏰ Hourly IHS** : Extraction et TEXTJOIN d'événements horaires
        
        👉 **Utilisez le menu latéral pour accéder à cette section**
        """)
    
    with col2:
        st.markdown("""
        ### 💬 Assistant IA
        
        Discutez avec un assistant intelligent :
        
        - ❓ **Posez des questions** sur vos données
        - 📈 **Obtenez des analyses** et des insights
        - 🔍 **Explorez vos fichiers** Excel
        - 💡 **Recevez des suggestions** d'amélioration
        - 🤖 **Support par LLM** distant configurable
        
        👉 **Utilisez le menu latéral pour accéder au chat**
        """)
    
    st.markdown("---")
    
    # Guide rapide
    st.markdown("## 🎯 Guide de démarrage rapide")
    
    step1, step2, step3 = st.columns(3)
    
    with step1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
            <h3 style="color: white; margin-bottom: 1rem;">1️⃣ Traitement</h3>
            <p>Configurez vos fichiers sources et sélectionnez les moteurs de traitement</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
            <h3 style="color: white; margin-bottom: 1rem;">2️⃣ Exécution</h3>
            <p>Prévisualisez et lancez l'exécution des traitements configurés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
            <h3 style="color: white; margin-bottom: 1rem;">3️⃣ Assistance</h3>
            <p>Utilisez l'assistant IA pour obtenir de l'aide et des analyses</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Statistiques de session
    st.markdown("## 📊 Statistiques de la session")
    
    metric1, metric2, metric3, metric4 = st.columns(4)
    
    with metric1:
        celldown_count = st.session_state['celldown_config'].get('count', 0)
        st.metric("CellDown actifs", celldown_count)
    
    with metric2:
        ticket_enabled = "Oui" if st.session_state['ticket_config'].get('enabled', False) else "Non"
        st.metric("Ticket", ticket_enabled)
    
    with metric3:
        ocm_count = st.session_state['ocm_config'].get('count', 0)
        st.metric("OCM actifs", ocm_count)
    
    with metric4:
        source_status = "✅ Configuré" if st.session_state.get('source_file_path') else "⏳ À configurer"
        st.metric("Fichier source", source_status)
    
    st.markdown("---")
    
    # Actions rapides
    st.markdown("## 🔧 Actions rapides")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("🔄 Réinitialiser la session", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with col_action2:
        if st.button("📊 Aller au traitement", use_container_width=True, type="primary"):
            st.switch_page("pages/1_📊_Traitement_Excel.py")
    
    with col_action3:
        if st.button("💬 Aller au chat", use_container_width=True, type="primary"):
            st.switch_page("pages/2_💬_Assistant_IA.py")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; padding: 2rem;">
        <p><strong>Plateforme de traitement Excel</strong></p>
        <p>NUR Project Lyne © 2026 | Version 1.0</p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">
            💡 Utilisez le <strong>menu latéral</strong> pour naviguer entre les pages
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
