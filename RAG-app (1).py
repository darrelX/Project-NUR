# ============================================================================
# RAG-app.py - VERSION CORRIGÉE
# - Chargement de plusieurs fichiers Excel
# - Saisie manuelle de Owner, Topology, et Commentaire
# - Recherche d'incidents similaires
# ============================================================================

import streamlit as st
import pandas as pd
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
import chromadb
from llama_index.core.node_parser import SentenceSplitter

# =====================================================
# 1. CONFIGURATION DES MODÈLES
# =====================================================
embed_model = OllamaEmbedding(
    model_name="nomic-embed-text", 
    base_url="http://localhost:11434"
)

llm = Ollama(
    model="llama3.2:3b", 
    base_url="http://localhost:11434",
    request_timeout=120.0
)

Settings.embed_model = embed_model
Settings.llm = llm
Settings.node_parser = SentenceSplitter(chunk_size=2048, chunk_overlap=200)

def truncate_text(text, max_length=1500):
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

# =====================================================
# 2. FONCTION D'INDEXATION (MODIFIÉE)
# =====================================================
@st.cache_resource
def build_index(uploaded_files):
    """
    Indexe TOUS les fichiers Excel chargés.
    Retourne l'index et la liste des valeurs disponibles.
    """
    all_docs = []
    all_values = {
        "owners": set(),
        "topologies": set(),
    }
    
    total_files = len(uploaded_files)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for file_idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"📂 Lecture de {uploaded_file.name}...")
        
        try:
            # Essayer de lire la feuille "daily break down"
            df = pd.read_excel(uploaded_file, sheet_name="daily break down", engine="openpyxl", header=1)
        except Exception as e:
            st.warning(f"⚠️ Erreur de lecture de {uploaded_file.name} : {e}")
            continue
        
        # Vérifier les colonnes requises
        required_cols = ["Verifications", "Owner", "Topology"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.warning(f"⚠️ Colonnes manquantes dans {uploaded_file.name} : {missing_cols}")
            continue
        
        for idx, row in df.iterrows():
            comment = row.get("Verifications")
            if pd.isna(comment) or str(comment).strip() == "":
                continue
            
            comment = truncate_text(comment, max_length=1500)
            
            owner_val = str(row.get("Owner", "")) if pd.notna(row.get("Owner")) else ""
            topology_val = str(row.get("Topology", "")) if pd.notna(row.get("Topology")) else ""
            
            if owner_val and owner_val != "nan":
                all_values["owners"].add(owner_val)
            if topology_val and topology_val != "nan":
                all_values["topologies"].add(topology_val)
            
            # Construction du texte pour la recherche
            text_to_index = f"""
            Commentaire: {comment}
            Topologie: {topology_val}
            Owner: {owner_val}
            """
            text_to_index = truncate_text(text_to_index, max_length=2000)
            
            # Métadonnées complètes
            metadata = {
                "commentaire": comment,
                "topology": topology_val,
                "owner": owner_val,
                "cause": str(row.get("CAUSE", "")) if pd.notna(row.get("CAUSE")) else "",
                "nomenclature": str(row.get("OCM NOMENCLATURE", "")) if pd.notna(row.get("OCM NOMENCLATURE")) else "",
                "categorie": str(row.get("CATEGORIE", "")) if pd.notna(row.get("CATEGORIE")) else "",
                "sub_rca": str(row.get("SUB RCA", "")) if pd.notna(row.get("SUB RCA")) else "",
                "source_file": uploaded_file.name,  # ✅ Ajout : nom du fichier source
            }
            
            doc = Document(text=text_to_index, metadata=metadata)
            all_docs.append(doc)
        
        progress_bar.progress((file_idx + 1) / total_files)
    
    status_text.text("✅ Lecture terminée. Création de l'index...")
    
    if not all_docs:
        st.error("❌ Aucun document valide trouvé dans les fichiers.")
        return None, None
    
    # Création de la base vectorielle Chroma
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    try:
        chroma_client.delete_collection("incidents")
    except:
        pass
    
    collection = chroma_client.create_collection("incidents")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    index = VectorStoreIndex.from_documents(all_docs, storage_context=storage_context)
    
    available_values = {
        "owners": sorted(list(all_values["owners"])),
        "topologies": sorted(list(all_values["topologies"])),
    }
    
    status_text.text("✅ Indexation terminée !")
    progress_bar.empty()
    
    return index, available_values

# =====================================================
# 3. FONCTION DE RECHERCHE
# =====================================================
def search_similar_incidents(index, owner, topology, comment, top_k=10):
    """
    Recherche les incidents similaires en utilisant le commentaire comme requête,
    puis filtre par Owner et Topology.
    """
    if not comment.strip():
        return []
    
    # Construction de la requête
    query_text = f"""
    Commentaire: {comment}
    Topologie: {topology}
    Owner: {owner}
    """
    
    # Recherche vectorielle
    retriever = index.as_retriever(similarity_top_k=50)
    results = retriever.retrieve(query_text)
    
    # Filtrage par Owner et Topology
    filtered_results = []
    for res in results:
        meta = res.metadata
        
        # Filtre Owner (si spécifié)
        if owner and owner.strip():
            if owner.lower() != meta["owner"].lower():
                continue
        
        # Filtre Topology (si spécifié)
        if topology and topology.strip():
            if topology.lower() != meta["topology"].lower():
                continue
        
        filtered_results.append(res)
    
    return filtered_results[:top_k]

# =====================================================
# 4. INTERFACE STREAMLIT (MODIFIÉE)
# =====================================================
st.set_page_config(page_title="RAG Incidents NOC", layout="wide")
st.title("🔍 Recherche d'incidents similaires - NOC Assistant")

# ===== SIDEBAR : Chargement des fichiers =====
with st.sidebar:
    st.header("📂 Base de connaissances")
    uploaded_files = st.file_uploader(
        "Charger vos fichiers Excel",
        type=["xlsx"],
        accept_multiple_files=True,
        help="Sélectionnez un ou plusieurs fichiers Excel contenant une feuille 'daily break down'"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} fichier(s) chargé(s)")
        for f in uploaded_files:
            st.caption(f"📄 {f.name}")
    
    st.divider()
    
    if st.button("🔄 Réindexer les données", type="secondary"):
        st.cache_resource.clear()
        st.rerun()

# ===== ZONE PRINCIPALE =====
if uploaded_files:
    with st.spinner("📥 Indexation en cours... (cela peut prendre quelques minutes)"):
        index, available_values = build_index(uploaded_files)
    
    if index and available_values:
        st.success(f"✅ Indexation terminée ! {len(available_values['owners'])} owners, {len(available_values['topologies'])} topologies indexés.")
        
        # ===== ZONE DE SAISIE =====
        st.subheader("📝 Décrivez l'incident")
        
        col1, col2 = st.columns(2)
        
        with col1:
            owner_input = st.text_input(
                "👤 Owner",
                placeholder="Ex: CAMUSAT, IHS, ORANGE...",
                help="Entrez le nom du propriétaire du site"
            )
        
        with col2:
            topology_input = st.text_input(
                "🏗️ Topologie",
                placeholder="Ex: Grid Only, Medium Grid + GE...",
                help="Entrez la topologie du site"
            )
        
        comment_input = st.text_area(
            "💬 Commentaire terrain",
            height=150,
            placeholder="Décrivez l'incident avec le plus de détails possible...",
            help="Ce texte sera utilisé pour trouver des incidents similaires"
        )
        
        # ===== BOUTON DE RECHERCHE =====
        if st.button("🔎 Rechercher des incidents similaires", type="primary", use_container_width=True):
            if not comment_input.strip():
                st.warning("⚠️ Veuillez entrer un commentaire.")
            else:
                with st.spinner("🔍 Recherche en cours..."):
                    results = search_similar_incidents(
                        index,
                        owner_input,
                        topology_input,
                        comment_input,
                        top_k=10
                    )
                
                st.divider()
                
                # ===== AFFICHAGE DES RÉSULTATS =====
                if not results:
                    st.warning("⚠️ Aucun incident similaire trouvé.")
                    st.info("""
                    **Suggestions :**
                    - Essayez sans spécifier d'Owner ou de Topologie
                    - Reformulez votre commentaire
                    - Vérifiez que vos fichiers contiennent des cas similaires
                    """)
                else:
                    st.success(f"📋 {len(results)} incident(s) similaire(s) trouvé(s)")
                    
                    for i, res in enumerate(results):
                        meta = res.metadata
                        with st.expander(
                            f"Résultat #{i+1} | Score: {res.score:.2f} | Owner: {meta['owner']} | Topologie: {meta['topology']}",
                            expanded=(i < 3)
                        ):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**📝 Commentaire:**")
                                st.text_area(
                                    f"comment_{i}",
                                    meta['commentaire'][:500],
                                    height=100,
                                    disabled=True,
                                    key=f"comment_{i}"
                                )
                            
                            with col2:
                                st.markdown(f"**📁 Source:** {meta.get('source_file', 'N/A')}")
                            
                            st.divider()
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown(f"**⚠️ CAUSE:** {meta['cause'] or 'Non spécifiée'}")
                                st.markdown(f"**📚 Nomenclature:** {meta['nomenclature'] or 'Non spécifiée'}")
                            with col_b:
                                st.markdown(f"**🗂️ Catégorie:** {meta['categorie'] or 'Non spécifiée'}")
                                st.markdown(f"**🔧 Sub RCA:** {meta['sub_rca'][:200] if meta['sub_rca'] else 'Non spécifiée'}")
        
        # ===== AFFICHAGE DES VALEURS DISPONIBLES (optionnel) =====
        with st.expander("📊 Voir toutes les valeurs disponibles dans la base"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**👤 Owners disponibles :**")
                for owner in available_values["owners"][:30]:
                    st.code(owner)
                if len(available_values["owners"]) > 30:
                    st.caption(f"... et {len(available_values['owners']) - 30} autres")
            
            with col2:
                st.markdown("**🏗️ Topologies disponibles :**")
                for topo in available_values["topologies"][:30]:
                    st.code(topo)
                if len(available_values["topologies"]) > 30:
                    st.caption(f"... et {len(available_values['topologies']) - 30} autres")

else:
    st.info("📂 Chargez au moins un fichier Excel dans la barre latérale pour commencer.")
    st.caption("Le fichier doit contenir une feuille nommée 'daily break down' avec les colonnes : Verifications, Owner, Topology")