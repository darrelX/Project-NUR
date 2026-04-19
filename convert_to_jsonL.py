import json
import os
import re
import pandas as pd

file = r"followup- 09-04-2026.xlsx"

# Lire le fichier Excel (pas d'en-têtes, données brutes)
df = pd.read_excel(file, sheet_name="Sheet1", header=None)

# Mapping des colonnes basé sur la structure du fichier
# Col 0: RCA, Col 1: Action Plan, Col 2: OWNER, Col 3: Status, Col 4: Comment
column_mapping = {
    0: "RCA",
    1: "Action Plan",
    2: "OWNER",
    3: "Status",
    4: "Comment"
}

# Renommer les colonnes
df.columns = [column_mapping.get(i, f"Col{i}") for i in range(len(df.columns))]

# Supprimer les lignes complètement vides
df = df.dropna(how='all')

print(f"Colonnes: {list(df.columns)}")
print(f"Nombre de lignes: {len(df)}")

# Préparer le fichier JSONL de sortie
output_file = "output.jsonl"

with open(output_file, "w", encoding="utf-8") as f:
    for idx, row in df.iterrows():
        # Extraire les valeurs
        rca = str(row["RCA"]) if pd.notna(row["RCA"]) else ""
        action_plan = str(row["Action Plan"]) if pd.notna(row["Action Plan"]) else ""
        owner = str(row["OWNER"]) if pd.notna(row["OWNER"]) else ""
        status = str(row["Status"]) if pd.notna(row["Status"]) else ""
        comment = str(row["Comment"]) if pd.notna(row["Comment"]) else ""
        
        # Ignorer les lignes sans RCA
        if not rca:
            continue
        
        # Extraire la date du commentaire si présente (format: DD/MM/YYYY ou DD.MM.YY)
        date_match = re.search(r'(\d{2}[./]\d{2}[./]\d{2,4})', comment)
        date_str = date_match.group(1) if date_match else ""
        
        # Construire le contenu user: date + infos contextuelles
        user_parts = []
        if date_str:
            user_parts.append(date_str)
        if rca:
            user_parts.append(rca)
        if comment and comment != rca:
            # Ajouter le commentaire nettoyé (sans la date déjà extraite)
            clean_comment = re.sub(r'^\d{2}[./]\d{2}[./]\d{2,4}[;:\s]*', '', comment).strip()
            if clean_comment and clean_comment != rca:
                user_parts.append(clean_comment)
        
        user_content = "; ".join(user_parts) if user_parts else rca
        
        # Construire la réponse assistant en JSON
        assistant_response = {
            "RCA": rca,
            "ETR": "",  # Non présent dans les données
            "OWNER": owner,
            "Action Plan": action_plan
        }
        
        # Créer l'entrée JSONL
        system_prompt = (
            "You are a telecom NOC analyst.\n\n"
            "Extract exactly these fields from the comment:\n"
            "- RCA\n"
            "- Action Plan\n"
            "- ETR\n"
            "- OWNER\n"
            "- Status\n"
            "Return ONLY one valid JSON object"
        )
        entry = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": json.dumps(assistant_response, ensure_ascii=False)}
            ]
        }
        
        # Écrire la ligne
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"\nFichier JSONL créé: {output_file}")

# Afficher un exemple
with open(output_file, "r", encoding="utf-8") as f:
    print("\nExemples:")
    for i, line in enumerate(f):
        if i < 3:
            print(line.strip())
        else:
            break


