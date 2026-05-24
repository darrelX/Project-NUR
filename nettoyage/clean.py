import pandas as pd
import re
from pathlib import Path

# =====================================================
# VARIABLES GLOBALES
# =====================================================
SHEET_NAME = "daily break down"
COMMENT_COLUMN = "Verifications 29/04/2026"
CLEAN_COLUMN = "cleaning comment"

# Fichier source
file = Path("inputs\\file-RAG2.xlsx")


def clean_comment(text):
    """
    Nettoyage léger des commentaires terrain
    sans détruire le sens métier.
    """

    if pd.isna(text):
        return ""

    text = str(text)

    # =====================================================
    # SUPPRESSION DES BLOCS DUPLIQUÉS
    # =====================================================
    parts = [p.strip() for p in text.split(";..;..;")]
    unique_parts = []

    for part in parts:
        if part not in unique_parts:
            unique_parts.append(part)

    text = " ; ".join(unique_parts)

    # =====================================================
    # SUPPRESSION DES TICKETS
    # =====================================================
    text = re.sub(
        r"\b[A-Z]{2,10}-\d{8}-\d{6,12}\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # =====================================================
    # SUPPRESSION DES PARENTHÈSES CONTENANT
    # OCM RAN / TICKET / OWS / CELLDOWN / CELLDOWNS / HOURLY
    # =====================================================
    text = re.sub(
        r"\([^()]*\b(?:ocm\s+ran|ticket|ows|celldown|celldowns|hourly)\b[^()]*\)",
        "",
        text,
        flags=re.IGNORECASE
    )

    # =====================================================
    # SUPPRESSION DES BLOCS TECHNIQUES INUTILES
    # =====================================================
    useless_patterns = [
        r"FME\s+\w+\s+activer",
        r"Action en cours avec le lkevel\s*\d+",
        r"Power status check ongoing\.\.;\.\.",
        r"Others Transmission equipement fault"
    ]

    for pattern in useless_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # =====================================================
    # UNIFORMISATION
    # =====================================================
    text = text.replace("\n", " ")
    text = text.replace("||", " || ")
    text = re.sub(r"\|\|\s*\|\|", " || ", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"\s*:\s*", " : ", text)
    text = re.sub(r"(^|[.!?]\s+)[^\w\s]+", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()

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