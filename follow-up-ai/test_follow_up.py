# Test du système de complétion automatique avec Gemini
import pandas as pd
import numpy as np
import google.generativeai as genai
import json
import os

# Configuration de l'API Gemini
GEMINI_API_KEY = "AIzaSyDF6rYh4-4sQe3_sxWSQwg_KjyUFxua2p8"
genai.configure(api_key=GEMINI_API_KEY)

# Utiliser le modèle Gemini
model = genai.GenerativeModel('gemini-1.5-flash')
print("✅ Gemini API configurée avec succès\n")

# Chargement du fichier Excel
fichier_excel = 'darrel.xlsx'

try:
    df_darrel = pd.read_excel(fichier_excel, sheet_name='darrel')
    df_completer = pd.read_excel(fichier_excel, sheet_name='COMPLETER')
    
    print(f"✅ Feuille 'darrel' chargée : {len(df_darrel)} lignes")
    print(f"✅ Feuille 'COMPLETER' chargée : {len(df_completer)} lignes")
    print(f"\nColonnes de 'darrel' : {list(df_darrel.columns)}")
    print(f"Colonnes de 'COMPLETER' : {list(df_completer.columns)}\n")
    
    # Aperçu des données
    print("=== Aperçu de la feuille 'darrel' (exemples validés) ===")
    print(df_darrel.head(3))
    
    print("\n=== Aperçu de la feuille 'COMPLETER' (à traiter) ===")
    print(df_completer.head(3))
    
except FileNotFoundError:
    print("❌ Fichier 'darrel.xlsx' non trouvé dans le répertoire courant")
    print(f"   Répertoire actuel : {os.getcwd()}")
    print("   Place le fichier 'darrel.xlsx' dans le dossier follow-up-ai/")
    exit(1)
except Exception as e:
    print(f"❌ Erreur lors du chargement : {e}")
    exit(1)


def generer_champs_avec_gemini(commentaire, exemples_df):
    """
    Génère les champs RCA, ACTION PLAN, ETR, OWNER, STATUS 
    en s'inspirant des exemples validés
    """
    
    # Créer un contexte avec 5 exemples validés aléatoires
    exemples = exemples_df.sample(min(5, len(exemples_df)))
    
    exemples_text = ""
    for idx, row in exemples.iterrows():
        exemples_text += f"""
Exemple {idx + 1}:
- Commentaire: {row.get('commentaire', 'N/A')}
- RCA: {row.get('RCA', 'N/A')}
- ACTION PLAN: {row.get('ACTION PLAN', 'N/A')}
- ETR: {row.get('ETR', 'N/A')}
- OWNER: {row.get('OWNER', 'N/A')}
- STATUS: {row.get('STATUS', 'N/A')}
"""
    
    # Créer le prompt pour Gemini
    prompt = f"""Tu es un expert en analyse de tickets techniques. Voici des exemples validés de tickets avec leurs champs complétés :

{exemples_text}

Maintenant, analyse ce nouveau commentaire et génère les champs manquants en t'inspirant du style, de la formulation et de la logique des exemples ci-dessus :

Commentaire à analyser: {commentaire}

IMPORTANT:
- Inspire-toi des exemples pour le style et la formulation
- Sois cohérent avec les patterns observés
- Réponds UNIQUEMENT avec un JSON valide, sans aucun texte additionnel
- Format JSON attendu:
{{
  "RCA": "valeur",
  "ACTION PLAN": "valeur",
  "ETR": "valeur",
  "OWNER": "valeur",
  "STATUS": "valeur"
}}
"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Nettoyer la réponse (enlever les marqueurs markdown si présents)
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Parser le JSON
        result = json.loads(response_text)
        return result
    
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        if 'response' in locals():
            print(f"Réponse brute: {response.text}")
        return {
            "RCA": "ERROR",
            "ACTION PLAN": "ERROR",
            "ETR": "ERROR",
            "OWNER": "ERROR",
            "STATUS": "ERROR"
        }


# Créer les colonnes si elles n'existent pas
colonnes_requises = ['RCA', 'ACTION PLAN', 'ETR', 'OWNER', 'STATUS']
for col in colonnes_requises:
    if col not in df_completer.columns:
        df_completer[col] = ""

# Traiter chaque ligne (limiter à 3 pour le test)
print("\n🚀 Début du traitement (test sur 3 lignes)...\n")

for idx, row in df_completer.head(3).iterrows():
    commentaire = row.get('commentaire', '')
    
    if pd.isna(commentaire) or commentaire == '':
        print(f"⚠️  Ligne {idx + 1}: Pas de commentaire, ignorée")
        continue
    
    print(f"📝 Ligne {idx + 1}: Traitement en cours...")
    print(f"   Commentaire: {commentaire[:80]}...")
    
    # Générer les champs avec Gemini
    result = generer_champs_avec_gemini(commentaire, df_darrel)
    
    # Mettre à jour le DataFrame
    df_completer.at[idx, 'RCA'] = result.get('RCA', '')
    df_completer.at[idx, 'ACTION PLAN'] = result.get('ACTION PLAN', '')
    df_completer.at[idx, 'ETR'] = result.get('ETR', '')
    df_completer.at[idx, 'OWNER'] = result.get('OWNER', '')
    df_completer.at[idx, 'STATUS'] = result.get('STATUS', '')
    
    print(f"   ✅ RCA: {result.get('RCA', '')[:50]}...")
    print(f"   ✅ STATUS: {result.get('STATUS', '')}")
    print()

print("✅ Test terminé!\n")

# Afficher les résultats
print("=== RÉSULTATS COMPLÉTÉS ===\n")
print(df_completer[['commentaire', 'RCA', 'ACTION PLAN', 'ETR', 'OWNER', 'STATUS']].head(3))

# Sauvegarder le fichier Excel
output_filename = 'darrel_complete_test.xlsx'

with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    df_darrel.to_excel(writer, sheet_name='darrel', index=False)
    df_completer.to_excel(writer, sheet_name='COMPLETER', index=False)

print(f"\n✅ Fichier test sauvegardé: {output_filename}")
