"""
Script de test de connexion au serveur LLM
Permet de vérifier que votre configuration fonctionne avant de l'utiliser dans l'interface
"""

import requests
import json

# ========== CONFIGURATION ==========
# Remplacez ces valeurs par votre configuration

SERVER_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "sk-your-api-key-here"
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.7
MAX_TOKENS = 500

# ====================================


def test_llm_connection():
    """
    Teste la connexion au serveur LLM
    """
    print("🔍 Test de connexion au serveur LLM...\n")
    print(f"📡 URL: {SERVER_URL}")
    print(f"🤖 Modèle: {MODEL}")
    print(f"🌡️  Température: {TEMPERATURE}")
    print(f"📊 Tokens max: {MAX_TOKENS}")
    print("\n" + "="*60 + "\n")
    
    # Préparer la requête
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Tu es un assistant IA serviable et concis."
            },
            {
                "role": "user",
                "content": "Dis bonjour et confirme que la connexion fonctionne en une phrase."
            }
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }
    
    try:
        print("📤 Envoi de la requête...")
        response = requests.post(
            SERVER_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📥 Code de réponse: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            
            # Afficher la structure de la réponse
            print("✅ CONNEXION RÉUSSIE !\n")
            print("Structure de la réponse:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("\n" + "="*60 + "\n")
            
            # Extraire et afficher le message
            if 'choices' in data and len(data['choices']) > 0:
                message = data['choices'][0]['message']['content']
                print("💬 Message de l'assistant:")
                print(f"\"{message}\"")
                
                # Informations supplémentaires
                if 'usage' in data:
                    print(f"\n📊 Utilisation:")
                    print(f"   - Tokens prompt: {data['usage'].get('prompt_tokens', 'N/A')}")
                    print(f"   - Tokens réponse: {data['usage'].get('completion_tokens', 'N/A')}")
                    print(f"   - Total: {data['usage'].get('total_tokens', 'N/A')}")
                
                return True
            else:
                print("⚠️ Format de réponse inattendu (pas de 'choices')")
                return False
        
        else:
            print(f"❌ ÉCHEC DE LA CONNEXION\n")
            print(f"Code d'erreur: {response.status_code}")
            print(f"Message: {response.text}")
            
            # Suggestions selon le code d'erreur
            if response.status_code == 401:
                print("\n💡 Suggestion: Vérifiez votre clé API")
            elif response.status_code == 404:
                print("\n💡 Suggestion: Vérifiez l'URL du serveur")
            elif response.status_code == 429:
                print("\n💡 Suggestion: Limite de requêtes atteinte, attendez un peu")
            elif response.status_code >= 500:
                print("\n💡 Suggestion: Le serveur rencontre un problème, réessayez plus tard")
            
            return False
    
    except requests.exceptions.Timeout:
        print("⏱️ TIMEOUT : Le serveur met trop de temps à répondre")
        print("💡 Suggestion: Vérifiez votre connexion internet ou augmentez le timeout")
        return False
    
    except requests.exceptions.ConnectionError:
        print("🔌 ERREUR DE CONNEXION : Impossible de joindre le serveur")
        print("💡 Suggestions:")
        print("   - Vérifiez l'URL du serveur")
        print("   - Vérifiez votre connexion internet")
        print("   - Le serveur est peut-être hors ligne")
        return False
    
    except Exception as e:
        print(f"❌ ERREUR INATTENDUE : {str(e)}")
        return False


def test_openai():
    """Configuration rapide pour tester OpenAI"""
    global SERVER_URL, MODEL
    SERVER_URL = "https://api.openai.com/v1/chat/completions"
    MODEL = "gpt-3.5-turbo"
    return test_llm_connection()


def test_local_server():
    """Configuration rapide pour tester un serveur local (ex: LM Studio)"""
    global SERVER_URL, API_KEY, MODEL
    SERVER_URL = "http://localhost:1234/v1/chat/completions"
    API_KEY = "lm-studio"
    MODEL = "local-model"
    return test_llm_connection()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           TEST DE CONNEXION AU SERVEUR LLM                   ║
║                  NUR Project Lyne                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("Choisissez un test:")
    print("1. Configuration manuelle (modifiez le script)")
    print("2. Test rapide OpenAI")
    print("3. Test rapide serveur local (LM Studio)")
    print()
    
    choice = input("Votre choix (1-3) : ").strip()
    
    print("\n" + "="*60 + "\n")
    
    if choice == "2":
        api_key = input("Entrez votre clé API OpenAI : ").strip()
        API_KEY = api_key
        success = test_openai()
    elif choice == "3":
        success = test_local_server()
    else:
        success = test_llm_connection()
    
    print("\n" + "="*60)
    
    if success:
        print("\n✅ Le serveur fonctionne correctement !")
        print("Vous pouvez maintenant utiliser cette configuration dans l'interface Streamlit.")
    else:
        print("\n❌ La connexion a échoué.")
        print("Vérifiez la configuration et les messages d'erreur ci-dessus.")
    
    print("\n" + "="*60)
