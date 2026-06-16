# ============================================================================
# test_uploader.py - Test minimal de l'upload
# ============================================================================

import streamlit as st
from components.file_uploader import render_file_uploader

st.set_page_config(page_title="Test Uploader", layout="wide")
st.title("🧪 Test de l'upload")

# Afficher le composant
principal_ok = render_file_uploader()

# Débogage : afficher l'état de st.session_state
st.divider()
st.subheader("🔍 État de st.session_state")

if st.checkbox("Voir st.session_state"):
    st.write("### Fichier principal :")
    if st.session_state.fichiers["principal"] is not None:
        st.success(f"✅ Chargé : {len(st.session_state.fichiers['principal'])} lignes")
    else:
        st.warning("❌ Non chargé")
    
    st.write("### Fichiers sources :")
    for key in st.session_state.fichiers["sources"]:
        fichiers = st.session_state.fichiers["sources"][key]
        if fichiers:
            for f in fichiers:
                st.write(f"- **{key}** : {f['nom']} (binaire: {len(f.get('binaire', ''))} octets)")
        else:
            st.write(f"- **{key}** : Aucun")