"""
Composant Chat - Interface de discussion avec LLM distant
"""

import streamlit as st
from typing import Optional, Dict, List
import time


def render_chat_panel() -> None:
    """
    Rendu du panneau de chat avec LLM distant
    """
    
    st.markdown("## 💬 Assistant IA")
    st.markdown("Posez vos questions sur vos données Excel ou demandez de l'aide")
    
    # Initialiser l'historique de chat
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    if 'llm_config' not in st.session_state:
        st.session_state['llm_config'] = {
            'server_url': '',
            'api_key': '',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 2000
        }
    
    # Configuration du LLM (repliable)
    with st.expander("⚙️ Configuration du serveur LLM", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            server_url = st.text_input(
                "URL du serveur",
                value=st.session_state['llm_config']['server_url'],
                placeholder="https://api.openai.com/v1/chat/completions",
                help="URL de l'API du serveur LLM distant"
            )
            
            model = st.selectbox(
                "Modèle",
                options=[
                    "gpt-4",
                    "gpt-3.5-turbo",
                    "claude-3-opus",
                    "claude-3-sonnet",
                    "mistral-large",
                    "custom"
                ],
                index=1,
                help="Sélectionnez le modèle LLM à utiliser"
            )
            
            if model == "custom":
                model = st.text_input("Nom du modèle personnalisé", value="")
        
        with col2:
            api_key = st.text_input(
                "Clé API",
                type="password",
                value=st.session_state['llm_config']['api_key'],
                placeholder="sk-...",
                help="Clé d'authentification API"
            )
            
            temperature = st.slider(
                "Température",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state['llm_config']['temperature'],
                step=0.1,
                help="Contrôle la créativité des réponses (0 = déterministe, 2 = très créatif)"
            )
            
            max_tokens = st.number_input(
                "Tokens maximum",
                min_value=100,
                max_value=8000,
                value=st.session_state['llm_config']['max_tokens'],
                step=100,
                help="Longueur maximale de la réponse"
            )
        
        # Bouton de sauvegarde de la config
        if st.button("💾 Sauvegarder la configuration", use_container_width=True):
            st.session_state['llm_config'] = {
                'server_url': server_url,
                'api_key': api_key,
                'model': model,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            st.success("✅ Configuration sauvegardée")
        
        # Ajouter contexte des fichiers chargés
        st.markdown("---")
        st.markdown("### 📄 Contexte automatique")
        
        include_source = st.checkbox(
            "Inclure les infos du fichier source",
            value=True,
            help="Permet à l'IA de connaître votre fichier Excel"
        )
        
        include_stats = st.checkbox(
            "Inclure les statistiques",
            value=True,
            help="Ajoute les métriques de vos données"
        )
    
    # Zone de chat
    st.markdown("---")
    
    # Container pour l'historique des messages
    chat_container = st.container()
    
    with chat_container:
        # Afficher l'historique
        for message in st.session_state['chat_history']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("timestamp"):
                    st.caption(f"🕒 {message['timestamp']}")
    
    # Zone de saisie du message (toujours en bas)
    user_input = st.chat_input(
        "Posez votre question ici...",
        key="chat_input"
    )
    
    # Traiter le nouveau message
    if user_input:
        # Ajouter le message utilisateur
        timestamp = time.strftime("%H:%M:%S")
        st.session_state['chat_history'].append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        # Afficher immédiatement le message utilisateur
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
                st.caption(f"🕒 {timestamp}")
        
        # Préparer le contexte
        context = _build_context(
            include_source=include_source if 'include_source' in locals() else True,
            include_stats=include_stats if 'include_stats' in locals() else True
        )
        
        # Envoyer au LLM et obtenir la réponse
        with st.spinner("🤔 L'assistant réfléchit..."):
            response = _send_to_llm(
                message=user_input,
                context=context,
                config=st.session_state['llm_config']
            )
        
        # Ajouter la réponse de l'assistant
        timestamp = time.strftime("%H:%M:%S")
        st.session_state['chat_history'].append({
            "role": "assistant",
            "content": response,
            "timestamp": timestamp
        })
        
        # Recharger la page pour afficher la réponse
        st.rerun()
    
    # Boutons d'action
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state['chat_history'] = []
            st.rerun()
    
    with col2:
        if st.button("💾 Exporter la conversation", use_container_width=True):
            _export_conversation()
    
    with col3:
        message_count = len(st.session_state['chat_history'])
        st.metric("Messages", message_count)


def _build_context(include_source: bool = True, include_stats: bool = True) -> str:
    """
    Construit le contexte à envoyer au LLM
    """
    context_parts = []
    
    if include_source and st.session_state.get('source_config'):
        source_config = st.session_state['source_config']
        context_parts.append(f"Fichier source: {source_config.get('file_path', 'Non défini')}")
        context_parts.append(f"Feuille: {source_config.get('sheet_name', 'Non défini')}")
    
    if include_stats:
        # Ajouter les statistiques des traitements actifs
        celldown_count = st.session_state.get('celldown_config', {}).get('count', 0)
        ticket_enabled = st.session_state.get('ticket_config', {}).get('enabled', False)
        ocm_count = st.session_state.get('ocm_config', {}).get('count', 0)
        
        context_parts.append(f"Traitements CellDown actifs: {celldown_count}")
        context_parts.append(f"Traitement Ticket actif: {'Oui' if ticket_enabled else 'Non'}")
        context_parts.append(f"Traitements OCM actifs: {ocm_count}")
    
    return "\n".join(context_parts) if context_parts else "Aucun contexte disponible"


def _send_to_llm(message: str, context: str, config: Dict) -> str:
    """
    Envoie le message au serveur LLM distant et retourne la réponse
    """
    import requests
    import json
    
    # Vérifier la configuration
    if not config.get('server_url') or not config.get('api_key'):
        return "❌ **Erreur de configuration** : Veuillez configurer l'URL du serveur et la clé API dans les paramètres."
    
    # Construire le prompt avec contexte
    system_prompt = f"""Tu es un assistant IA spécialisé dans l'analyse et le traitement de fichiers Excel.
Tu aides les utilisateurs à comprendre leurs données et à effectuer des opérations sur leurs fichiers.

Contexte actuel de l'utilisateur:
{context}

Réponds de manière claire, concise et professionnelle. Si tu ne peux pas répondre avec certitude, dis-le."""
    
    # Préparer la requête
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}"
    }
    
    # Construire l'historique des messages
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Ajouter l'historique récent (5 derniers messages)
    recent_history = st.session_state['chat_history'][-5:]
    for msg in recent_history[:-1]:  # Exclure le dernier message déjà ajouté
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Ajouter le message actuel
    messages.append({
        "role": "user",
        "content": message
    })
    
    payload = {
        "model": config['model'],
        "messages": messages,
        "temperature": config['temperature'],
        "max_tokens": config['max_tokens']
    }
    
    try:
        # Envoyer la requête
        response = requests.post(
            config['server_url'],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraire la réponse selon le format de l'API
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            elif 'content' in data:
                return data['content']
            else:
                return f"✅ Réponse reçue mais format inattendu:\n```json\n{json.dumps(data, indent=2)}\n```"
        else:
            return f"❌ **Erreur {response.status_code}** : {response.text}"
    
    except requests.exceptions.Timeout:
        return "⏱️ **Timeout** : Le serveur met trop de temps à répondre."
    
    except requests.exceptions.ConnectionError:
        return "🔌 **Erreur de connexion** : Impossible de joindre le serveur. Vérifiez l'URL."
    
    except Exception as e:
        return f"❌ **Erreur inattendue** : {str(e)}"


def _export_conversation() -> None:
    """
    Exporte la conversation en fichier texte
    """
    if not st.session_state.get('chat_history'):
        st.warning("⚠️ Aucune conversation à exporter")
        return
    
    # Construire le contenu
    lines = ["=" * 60, "CONVERSATION AVEC L'ASSISTANT IA", "=" * 60, ""]
    
    for message in st.session_state['chat_history']:
        role = "👤 UTILISATEUR" if message['role'] == 'user' else "🤖 ASSISTANT"
        timestamp = message.get('timestamp', 'N/A')
        lines.append(f"{role} [{timestamp}]")
        lines.append("-" * 60)
        lines.append(message['content'])
        lines.append("")
    
    content = "\n".join(lines)
    
    # Bouton de téléchargement
    st.download_button(
        label="📥 Télécharger la conversation",
        data=content,
        file_name=f"conversation_{time.strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )
    st.success("✅ Conversation prête à télécharger")
