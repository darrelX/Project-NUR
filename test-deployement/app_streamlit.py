# ══════════════════════════════════════════════════════════════
# app_streamlit.py — Application Breakdown IA (Streamlit)
# ══════════════════════════════════════════════════════════════
#
# Installation :
#   pip install streamlit requests pandas openpyxl
#
# Lancement :
#   streamlit run app_streamlit.py
#
# ══════════════════════════════════════════════════════════════

import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO
from datetime import datetime

# ── CONFIGURATION ────────────────────────────────────────────
# ⚠️ Remplace par l'URL réelle de ton pod RunPod (onglet Connect)
SERVEUR_IA_URL = "https://7z66mkxwkkwmyi-8000.proxy.runpod.net"

# Note : la classification de fichier ne dépend plus d'un timeout
# unique long — le traitement se fait en arrière-plan côté serveur
# et est suivi par interrogations courtes successives (polling),
# chacune avec son propre timeout court défini directement dans
# les fonctions demarrer/consulter/telecharger ci-dessous.
TIMEOUT_CHAT = 30          # 30s max pour une réponse de chat

st.set_page_config(
    page_title="Breakdown IA",
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── STYLE ORANGE — cohérent avec la charte du projet ──────────
st.markdown("""
<style>
    :root {
        --orange: #FF7900;
        --orange-dark: #E66D00;
    }
    .stApp { background-color: #FAFAFA; }
    h1, h2, h3 { color: #1A1A1A; }

    .badge-cause {
        display: inline-block;
        background: #FFF1E0;
        border: 1px solid #FF7900;
        color: #E66D00;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 14px;
        margin: 6px 0;
    }
    .carte-statut-ok {
        background: #EAF7EE;
        border: 1px solid #1B8A3D;
        padding: 10px 14px;
        border-radius: 8px;
        color: #1B8A3D;
        font-size: 13px;
        font-weight: 600;
    }
    .carte-statut-err {
        background: #FDEDEB;
        border: 1px solid #C0392B;
        padding: 10px 14px;
        border-radius: 8px;
        color: #C0392B;
        font-size: 13px;
        font-weight: 600;
    }
    div[data-testid="stSidebarNav"] { display: none; }

    .stButton button[kind="primary"] {
        background-color: #FF7900;
        border-color: #FF7900;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #E66D00;
        border-color: #E66D00;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# FONCTIONS D'APPEL AU SERVEUR IA
# ══════════════════════════════════════════════════════════════
def verifier_serveur_ia():
    try:
        r = requests.get(f"{SERVEUR_IA_URL}/health", timeout=5)
        if r.status_code == 200:
            return True, r.json()
        return False, {"erreur": f"Code HTTP {r.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"erreur": str(e)}


def demander_cause_ia(commentaire, owner="", topology="", vendors=""):
    try:
        payload = {
            "commentaire": commentaire,
            "owner": owner,
            "topology": topology,
            "vendors": vendors,
        }
        response = requests.post(f"{SERVEUR_IA_URL}/chat", json=payload, timeout=TIMEOUT_CHAT)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Erreur serveur IA ({response.status_code}) : {response.text[:300]}"
    except requests.exceptions.Timeout:
        return False, "Le modèle met trop de temps à répondre. Réessaie."
    except requests.exceptions.RequestException as e:
        return False, f"Impossible de joindre le serveur IA : {e}"


def demarrer_classification(fichier_bytes, nom_fichier):
    """
    Envoie le fichier complet (en une seule fois, sans découpage)
    et récupère immédiatement un identifiant de tâche. Le serveur
    répond en moins d'une seconde, bien avant que le proxy RunPod
    ne puisse couper la connexion.
    """
    try:
        fichiers = {
            "file": (
                nom_fichier,
                fichier_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }
        response = requests.post(
            f"{SERVEUR_IA_URL}/classifier/demarrer", files=fichiers, timeout=60
        )
        if response.status_code == 200:
            return True, response.json()["task_id"]
        return False, f"Erreur serveur IA ({response.status_code}) : {response.text[:300]}"
    except requests.exceptions.RequestException as e:
        return False, f"Impossible de joindre le serveur IA : {e}"


def consulter_statut_classification(task_id):
    """
    Interroge l'avancement du traitement. Réponse quasi instantanée,
    jamais bloquée par le proxy, à appeler en boucle toutes les
    quelques secondes pendant que le fichier complet est traité
    en arrière-plan sur le serveur.
    """
    try:
        response = requests.get(
            f"{SERVEUR_IA_URL}/classifier/statut/{task_id}", timeout=15
        )
        if response.status_code == 200:
            return True, response.json()
        return False, f"Erreur serveur IA ({response.status_code}) : {response.text[:300]}"
    except requests.exceptions.RequestException as e:
        return False, f"Impossible de joindre le serveur IA : {e}"


def telecharger_resultat_classification(task_id):
    """
    Récupère le fichier final, uniquement une fois le statut passé
    à "termine" côté serveur.
    """
    try:
        response = requests.get(
            f"{SERVEUR_IA_URL}/classifier/resultat/{task_id}", timeout=120
        )
        if response.status_code == 200:
            return True, response.content
        return False, f"Erreur serveur IA ({response.status_code}) : {response.text[:300]}"
    except requests.exceptions.RequestException as e:
        return False, f"Impossible de joindre le serveur IA : {e}"


# ══════════════════════════════════════════════════════════════
# ÉTAT DE SESSION
# ══════════════════════════════════════════════════════════════
if "historique_chat" not in st.session_state:
    st.session_state.historique_chat = []

if "resultat_classification" not in st.session_state:
    st.session_state.resultat_classification = None

if "nom_fichier_resultat" not in st.session_state:
    st.session_state.nom_fichier_resultat = None


# ══════════════════════════════════════════════════════════════
# SIDEBAR — navigation + statut serveur
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🟠 Breakdown IA")
    st.caption("NOC Orange Cameroun")
    st.divider()

    page = st.radio(
        "Navigation",
        ["💬 Chat", "📂 Classification de fichier"],
        label_visibility="collapsed",
    )

    st.divider()

    # Vérification du statut serveur
    ok, info = verifier_serveur_ia()
    if ok:
        st.markdown(
            f'<div class="carte-statut-ok">🟢 Modèle connecté<br>'
            f'<small>{info.get("gpu", "")}</small></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="carte-statut-err">🔴 Serveur IA indisponible<br>'
            f'<small>Vérifie que le pod RunPod est actif</small></div>',
            unsafe_allow_html=True,
        )

    if st.button("🔄 Rafraîchir le statut", use_container_width=True):
        st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE 1 — CHAT
# ══════════════════════════════════════════════════════════════
if page == "💬 Chat":
    st.title("Discuter avec le modèle")
    st.caption("Décris un incident réseau, le modèle propose une cause parmi les 21 catégories du référentiel NOC.")

    col_chat, col_contexte = st.columns([2.4, 1])

    with col_contexte:
        st.markdown("##### Contexte de l'incident")
        st.caption("Optionnel — améliore la précision de la classification")

        owner = st.selectbox(
            "Owner",
            ["— Non précisé —", "IHS", "CAMUSAT", "ESCO", "MTN", "OCM"],
        )
        owner = "" if owner == "— Non précisé —" else owner

        topology = st.text_input("Topology", placeholder="ex: Grid-Gen, good grid no ge")

        vendors = st.selectbox(
            "Vendors",
            ["— Non précisé —", "HUAWEI", "ZTE", "NOKIA"],
        )
        vendors = "" if vendors == "— Non précisé —" else vendors

        st.divider()
        if st.button("🗑️ Effacer la conversation", use_container_width=True):
            st.session_state.historique_chat = []
            st.rerun()

    with col_chat:
        zone_messages = st.container(height=480)

        with zone_messages:
            if not st.session_state.historique_chat:
                st.info("👋 Colle un commentaire d'incident ci-dessous pour commencer.")

            for msg in st.session_state.historique_chat:
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["contenu"])
                else:
                    with st.chat_message("assistant"):
                        st.markdown(f'<div class="badge-cause">{msg["cause"]}</div>', unsafe_allow_html=True)
                        st.write(msg["analyse"])

        commentaire = st.chat_input("Ex : Grid outage, no generator, ENEO down, battery discharging...")

        if commentaire:
            st.session_state.historique_chat.append({"role": "user", "contenu": commentaire})

            with st.spinner("Le modèle analyse le commentaire..."):
                succes, resultat = demander_cause_ia(commentaire, owner, topology, vendors)

            if succes:
                st.session_state.historique_chat.append({
                    "role": "assistant",
                    "cause": resultat.get("cause", "Non déterminée"),
                    "analyse": resultat.get("analyse", ""),
                })
            else:
                st.session_state.historique_chat.append({
                    "role": "assistant",
                    "cause": "Erreur",
                    "analyse": resultat,
                })

            st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE 2 — CLASSIFICATION DE FICHIER
# ══════════════════════════════════════════════════════════════
else:
    st.title("Classifier un fichier Breakdown")
    st.caption("Dépose le fichier Excel déjà compilé et nettoyé. Le modèle ajoute les colonnes CAUSE_PREDITE et ANALYSE.")

    st.markdown("##### Étapes du traitement")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("**1.** Fichier envoyé au modèle")
    c2.markdown("**2.** Chaque commentaire analysé")
    c3.markdown("**3.** Sites impactés résolus")
    c4.markdown("**4.** Fichier prêt au téléchargement")

    st.divider()

    fichier = st.file_uploader(
        "Glisse ton fichier ici ou clique pour parcourir",
        type=["xlsx", "xls"],
        help="Le fichier doit déjà être compilé et nettoyé par l'application.",
    )

    if fichier is not None:
        taille_ko = round(len(fichier.getvalue()) / 1024, 1)
        st.success(f"📄 **{fichier.name}** sélectionné ({taille_ko} Ko)")

        if st.button("🚀 Lancer la classification", type="primary", use_container_width=True):
            # Étape 1 — démarrer la tâche (réponse quasi instantanée,
            # le fichier complet est transmis en une seule fois)
            succes, resultat = demarrer_classification(fichier.getvalue(), fichier.name)

            if not succes:
                st.session_state.resultat_classification = None
                st.error(f"❌ Échec du démarrage : {resultat}")
            else:
                task_id = resultat
                barre = st.progress(0, text="Démarrage du traitement...")
                statut_texte = st.empty()

                # Étape 2 — interroger l'avancement toutes les 3 secondes.
                # Chaque appel est quasi instantané : le proxy RunPod ne
                # coupe jamais ce type de requête courte, contrairement
                # à l'ancien appel bloquant unique qui durait plusieurs
                # minutes.
                while True:
                    ok_statut, info = consulter_statut_classification(task_id)

                    if not ok_statut:
                        st.session_state.resultat_classification = None
                        st.error(f"❌ Erreur de suivi : {info}")
                        break

                    statut = info["statut"]

                    if statut in ("en_attente", "en_cours"):
                        pourcentage = int(info.get("pourcentage", 0))
                        barre.progress(
                            pourcentage / 100,
                            text=f"{info['message']} — {info['traitees']}/{info['total']} lignes ({pourcentage}%)"
                            if info["total"] > 0 else info["message"],
                        )
                        time.sleep(3)
                        continue

                    if statut == "erreur":
                        st.session_state.resultat_classification = None
                        st.error(f"❌ Échec du traitement : {info['message']}")
                        break

                    if statut == "termine":
                        barre.progress(1.0, text="Récupération du fichier...")
                        ok_dl, contenu = telecharger_resultat_classification(task_id)
                        if ok_dl:
                            st.session_state.resultat_classification = contenu
                            horodatage = datetime.now().strftime("%Y%m%d_%H%M")
                            st.session_state.nom_fichier_resultat = f"breakdown_classifie_{horodatage}.xlsx"
                            st.success(f"✅ {info['message']}")
                        else:
                            st.session_state.resultat_classification = None
                            st.error(f"❌ Échec du téléchargement : {contenu}")
                        break

    # ── Affichage du résultat (persistant tant qu'une nouvelle classification n'est pas lancée) ──
    if st.session_state.resultat_classification is not None:
        st.divider()
        st.markdown("##### Résultat")

        col_dl, col_apercu = st.columns([1, 2])

        with col_dl:
            st.download_button(
                label="⬇️ Télécharger le fichier classifié",
                data=st.session_state.resultat_classification,
                file_name=st.session_state.nom_fichier_resultat,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )

        with col_apercu:
            try:
                df_apercu = pd.read_excel(BytesIO(st.session_state.resultat_classification))
                nb_lignes = len(df_apercu)
                nb_classifiees = (
                    df_apercu["CAUSE_PREDITE"].notna().sum()
                    if "CAUSE_PREDITE" in df_apercu.columns else 0
                )
                st.metric("Lignes traitées", nb_lignes)
                st.metric("Lignes classifiées", nb_classifiees)
            except Exception:
                pass

        with st.expander("👁️ Aperçu du fichier résultat"):
            try:
                df_apercu = pd.read_excel(BytesIO(st.session_state.resultat_classification))
                colonnes_interessantes = [
                    c for c in df_apercu.columns
                    if c in ["Codesite", "CAUSE_PREDITE", "ANALYSE", "TYPE_CAS"]
                    or "verif" in c.lower()
                ]
                st.dataframe(
                    df_apercu[colonnes_interessantes] if colonnes_interessantes else df_apercu,
                    use_container_width=True,
                    height=300,
                )
            except Exception as e:
                st.warning(f"Aperçu indisponible : {e}")