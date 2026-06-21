# 🚀 Guide de démarrage rapide - Interface Chat

## Installation

1. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

2. **Lancer l'application**

```bash
cd automate
streamlit run app.py
```

## Configuration rapide

### Option 1 : OpenAI (GPT-3.5 / GPT-4)

1. Créez un compte sur [platform.openai.com](https://platform.openai.com)
2. Générez une clé API
3. Dans l'interface :
   - URL : `https://api.openai.com/v1/chat/completions`
   - Clé API : `sk-proj-xxxxx...`
   - Modèle : `gpt-3.5-turbo` ou `gpt-4`

### Option 2 : Serveur local (gratuit)

**Avec LM Studio :**

1. Téléchargez [LM Studio](https://lmstudio.ai/)
2. Téléchargez un modèle (ex: Mistral 7B, Llama 3)
3. Lancez le serveur local (port 1234)
4. Dans l'interface :
   - URL : `http://localhost:1234/v1/chat/completions`
   - Clé API : `lm-studio` (ou vide)
   - Modèle : Le nom du modèle chargé

**Avec Ollama :**

1. Installez [Ollama](https://ollama.ai/)
2. Téléchargez un modèle : `ollama pull mistral`
3. Utilisez un wrapper API compatible OpenAI
4. Configurez l'URL selon le wrapper

### Option 3 : Anthropic Claude

1. Compte sur [console.anthropic.com](https://console.anthropic.com)
2. Générez une clé API
3. Dans l'interface :
   - URL : `https://api.anthropic.com/v1/messages`
   - Clé API : `sk-ant-xxxxx...`
   - Modèle : `claude-3-sonnet` ou `claude-3-opus`

## Test de connexion

Avant d'utiliser l'interface, testez votre configuration :

```bash
python test_llm_connection.py
```

Suivez les instructions à l'écran.

## Première utilisation

1. **Ouvrez l'onglet "💬 Assistant IA"**
2. **Cliquez sur "⚙️ Configuration du serveur LLM"**
3. **Renseignez vos informations** (URL, clé API, modèle)
4. **Cliquez sur "💾 Sauvegarder la configuration"**
5. **Posez votre première question !**

## Exemples de questions

```
"Bonjour, peux-tu m'aider à comprendre mes données ?"

"J'ai un fichier Excel avec des sites télécoms, comment puis-je analyser les pannes ?"

"Explique-moi ce que fait le traitement CellDown"

"Génère-moi une formule Excel pour calculer un taux de disponibilité"
```

## Résolution rapide des problèmes

### ❌ "Erreur de configuration"
➡️ Vérifiez que l'URL et la clé API sont renseignés
➡️ Cliquez sur "Sauvegarder la configuration"

### ❌ "Erreur 401"
➡️ Clé API invalide ou expirée
➡️ Vérifiez votre clé sur le site du fournisseur

### ❌ "Timeout"
➡️ Serveur trop lent ou indisponible
➡️ Essayez un autre serveur ou attendez

### ❌ "Erreur de connexion"
➡️ Vérifiez l'URL (doit inclure `/v1/chat/completions`)
➡️ Vérifiez votre connexion internet
➡️ Si serveur local, vérifiez qu'il est lancé

## Coûts

### OpenAI (payant)
- GPT-3.5-turbo : ~$0.002 / 1K tokens
- GPT-4 : ~$0.03 / 1K tokens
- Consultez [openai.com/pricing](https://openai.com/pricing)

### Anthropic Claude (payant)
- Claude-3-Sonnet : ~$0.003 / 1K tokens
- Claude-3-Opus : ~$0.015 / 1K tokens
- Consultez [anthropic.com/pricing](https://www.anthropic.com/pricing)

### Serveurs locaux (gratuit)
- LM Studio : Totalement gratuit
- Ollama : Totalement gratuit
- ⚠️ Nécessite un PC puissant (GPU recommandé)

## Support

📧 Contact : NUR Project Lyne  
📚 Documentation complète : [CHAT_README.md](CHAT_README.md)  
🧪 Test de connexion : `python test_llm_connection.py`

---

**Bonne utilisation ! 🚀**
