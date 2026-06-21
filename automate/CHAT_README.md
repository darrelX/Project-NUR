# 💬 Assistant IA - Interface Chat

## Description

L'interface de chat intégrée permet de communiquer avec un LLM (Large Language Model) hébergé sur un serveur distant pour obtenir de l'aide sur vos données Excel, poser des questions, et recevoir des analyses.

## Fonctionnalités

### 🎯 Principales caractéristiques

- **Interface type ChatGPT** : Discussion naturelle avec historique
- **Connexion serveur distant** : Compatible avec OpenAI, Anthropic, Mistral, etc.
- **Contexte automatique** : L'IA connaît vos fichiers et configurations
- **Export de conversation** : Sauvegarde de l'historique en fichier texte
- **Configuration flexible** : Température, tokens, modèle personnalisable

### 📡 Serveurs compatibles

L'interface supporte les API suivantes :

1. **OpenAI** (GPT-3.5, GPT-4)
   - URL : `https://api.openai.com/v1/chat/completions`
   - Clé API : Compte OpenAI

2. **Anthropic Claude** (Claude-3-Opus, Claude-3-Sonnet)
   - URL : `https://api.anthropic.com/v1/messages`
   - Clé API : Compte Anthropic

3. **Mistral AI**
   - URL : `https://api.mistral.ai/v1/chat/completions`
   - Clé API : Compte Mistral

4. **Serveur local/personnalisé**
   - Tout serveur compatible API OpenAI
   - Ex: LM Studio, Ollama avec API wrapper

## Configuration

### Étape 1 : Ouvrir l'onglet Assistant IA

Dans l'application Streamlit, cliquez sur l'onglet **💬 Assistant IA**

### Étape 2 : Configurer le serveur

Ouvrez la section **⚙️ Configuration du serveur LLM** et renseignez :

1. **URL du serveur** : L'endpoint de l'API
2. **Clé API** : Votre token d'authentification
3. **Modèle** : Le modèle LLM à utiliser
4. **Température** : Créativité (0-2)
5. **Tokens maximum** : Longueur de réponse (100-8000)

Cliquez sur **💾 Sauvegarder la configuration**

### Étape 3 : Options de contexte

- ☑️ **Inclure les infos du fichier source** : Permet à l'IA de connaître votre fichier Excel
- ☑️ **Inclure les statistiques** : Ajoute les métriques des traitements actifs

## Utilisation

### Exemples de questions

```
💬 "Combien de lignes contiennent des commentaires dans ma feuille TOP 1906 ?"

💬 "Peux-tu m'expliquer comment fonctionne le traitement CellDown ?"

💬 "Quels sont les sites qui apparaissent le plus souvent dans mes données ?"

💬 "Comment puis-je filtrer les sites par région ?"

💬 "Génère-moi une formule Excel pour calculer le taux de disponibilité"
```

### Actions disponibles

- **🗑️ Effacer l'historique** : Remet à zéro la conversation
- **💾 Exporter la conversation** : Télécharge l'historique en .txt
- **Compteur de messages** : Affiche le nombre total d'échanges

## Format de la réponse

L'IA reçoit automatiquement :

- Le nom et chemin de votre fichier source
- La feuille sélectionnée
- Le nombre de traitements CellDown actifs
- Le statut du traitement Ticket
- Le nombre de traitements OCM actifs
- L'historique récent de la conversation (5 derniers messages)

## Sécurité

⚠️ **Important** :

- Votre clé API est stockée uniquement dans la session en cours
- Elle n'est pas sauvegardée sur le disque
- Utilisez une clé API dédiée avec des permissions limitées
- Ne partagez jamais votre clé API

## Dépannage

### Erreur "Permission denied" ou "Configuration manquante"

✅ Vérifiez que l'URL et la clé API sont renseignés
✅ Cliquez sur "Sauvegarder la configuration"

### Erreur "Timeout"

✅ Vérifiez votre connexion internet
✅ Le serveur distant peut être temporairement indisponible
✅ Essayez avec un timeout plus long

### Erreur "Format inattendu"

✅ L'API du serveur ne renvoie pas le format standard OpenAI
✅ Vérifiez l'URL (doit pointer vers `/chat/completions`)

### Pas de réponse

✅ Vérifiez que la clé API est valide
✅ Regardez le message d'erreur retourné
✅ Testez avec curl : `curl -H "Authorization: Bearer YOUR_KEY" YOUR_URL`

## Architecture

```
components/
  └── chat_panel.py          # Interface de chat complète
      ├── render_chat_panel()       # Rendu principal
      ├── _build_context()          # Construction du contexte
      ├── _send_to_llm()            # Communication avec le serveur
      └── _export_conversation()    # Export historique
```

## Exemple de configuration

### OpenAI GPT-4

```
URL: https://api.openai.com/v1/chat/completions
Clé API: sk-proj-xxxxxxxxxxxxx
Modèle: gpt-4
Température: 0.7
Tokens max: 2000
```

### Serveur local (LM Studio)

```
URL: http://localhost:1234/v1/chat/completions
Clé API: lm-studio (ou vide)
Modèle: local-model
Température: 0.7
Tokens max: 2000
```

## Limitations

- Maximum 5 messages d'historique envoyés au LLM (pour éviter les tokens excessifs)
- Timeout de 30 secondes par requête
- Pas de streaming des réponses (réponse complète uniquement)

## Support

Pour toute question ou problème :
- Consultez la documentation du fournisseur d'API
- Vérifiez les quotas et limites de votre compte
- Contactez le support de NUR Project Lyne

---

**Version** : 1.0  
**Date** : Juin 2026  
**Auteur** : NUR Project Lyne
