import pandas as pd
import re
from pathlib import Path

# =====================================================
# VARIABLES GLOBALES
# =====================================================
SHEET_NAME = "daily break down"
COMMENT_COLUMN = "VerificationS"
CLEAN_COLUMN = "cleaning comment"

file = r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\daily-break-down -06-07-2026..xlsx"


def clean_comment(text):
    if pd.isna(text):
        return ""

    text = str(text)

    # Suppression des blocs dupliqués
    parts = [p.strip() for p in text.split(";..;..;")]
    unique_parts = []
    for part in parts:  
        if part not in unique_parts:
            unique_parts.append(part)
    text = " ; ".join(unique_parts)

    # Suppression des tickets
    text = re.sub(r"\b[A-Z]{2,10}-\d{8}-\d{6,12}\b", "", text, flags=re.IGNORECASE)

    # Mots‑clés à supprimer entre parenthèses ou accolades
    keywords = r"ocm\s+ran|ticket|ows|celldown|celldowns|hourly|camusat|ihs|top\s+offenders?|cell|zte|BO RAN"

    # Suppression des parenthèses
    text = re.sub(r"\([^()]*\b(?:" + keywords + r")\b[^()]*\)", "", text, flags=re.IGNORECASE)
    # Suppression des accolades
    text = re.sub(r"\{[^{}]*\b(?:" + keywords + r")\b[^{}]*\}", "", text, flags=re.IGNORECASE)

    # Blocs techniques inutiles
    useless_patterns = [
        r"FME\s+\w+\s+activer",
        r"Action en cours avec le lkevel\s*\d+",
        r"Power status check ongoing\.\.;\.\.",
        r"Others Transmission equipement fault",
        r"Power status check Ongoing",
        r"others",
        r"other",
    ]
    for pattern in useless_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # =====================================================
    # UNIFORMISATION (conserve les retours à la ligne)
    # =====================================================
    # On ne remplace pas \n par espace
    text = text.replace("||", " || ")
    text = re.sub(r"\|\|\s*\|\|", " || ", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"\s*:\s*", " : ", text)

    # Suppression des : et ; en début de phrase (début de chaîne ou après espace ou retour à la ligne)
    text = re.sub(r"(^|\s+)[:;]+", r"\1", text)

    # Nettoyage : réduire les espaces multiples (mais garder les \n)
    text = re.sub(r"[ \t]+", " ", text)  # remplace les espaces/tabulations multiples par un espace
    # Supprime les espaces en début/fin de ligne et réduit les sauts de ligne multiples
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(line for line in lines if line)  # enlève les lignes vides

    if re.fullmatch(r"[\W_]+", text):
        return ""

    return text


def clean_data(file_path):
    df = pd.read_excel(file_path, sheet_name=SHEET_NAME)

    if COMMENT_COLUMN not in df.columns:
        raise ValueError(f"La colonne '{COMMENT_COLUMN}' est introuvable.")

    comment_index = df.columns.get_loc(COMMENT_COLUMN)
    cleaned_comments = df[COMMENT_COLUMN].apply(clean_comment)

    if CLEAN_COLUMN in df.columns:
        df[CLEAN_COLUMN] = cleaned_comments
    else:
        df.insert(comment_index + 1, CLEAN_COLUMN, cleaned_comments)

    return df


if __name__ == "__main__":
    cleaned_df = clean_data(file)

    with pd.ExcelWriter(
        file,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace"
    ) as writer:
        cleaned_df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

    print(f"Fichier mis à jour : {file}")