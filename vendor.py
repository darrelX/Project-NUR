import re
import unicodedata
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.utils import column_index_from_string

import pandas as pd


# =========================
# PARAMÈTRES GÉNÉRAUX
# =========================
INPUT_FILE = r"C:\Users\f50056342\Desktop\my work\REPETITIVES\STATUT DES SITES JOURNALIERS\statut.xlsx"
OUTPUT_FILE = r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\outputs\resultat_synthese.xlsx"

TARGET_DATE = "22/5/2026"   # colonne à exploiter
VALID_STATUTS = {"OPERATIONNEL", "INSECURITE"}
VALID_VENDORS = {"ZTE", "HUAWEI", "NOKIA"}


# Capitale de chaque région
# (utilisé pour exclure la capitale quand on veut la "région")
CAPITALS_BY_REGION = {
    "ADAMAOUA": "NGAOUNDERE",
    "CENTRE": "YAOUNDE",
    "EST": "BERTOUA",
    "LITTORAL": "DOUALA",
    "NORD": "GAROUA",
    "OUEST": "BAFOUSSAM",
    "EXTREME NORD": "MAROUA",
    "NORD OUEST": "BAMENDA",
    "SUD OUEST": "BUEA",
    "SUD": "EBOLOWA",
}

def col_letter_to_index(letter):
    """Convertit une lettre de colonne Excel en index (0-based)"""
    result = 0
    for char in letter:
        result = result * 26 + (ord(char.upper()) - ord('A') + 1)
    return result - 1


# =========================
# OUTILS
# =========================
def normalize_text(value) -> str:
    """Met en majuscules, enlève les accents, remplace tirets/underscores par espaces, compacte les espaces."""
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[-_]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_date_column(df: pd.DataFrame, target_date: str) -> str:
    """
    Trouve la colonne correspondant à la date cible.
    target_date au format: "7/5/2026" qui peut signifier:
    - Format français jour/mois/année: 7 Mai 2026 -> cherche datetime(2026, 5, 7)
    - Ou bien la valeur affichée "07/05" dans Excel qui correspond à datetime(2026, 7, 5)
    
    On essaie les deux interprétations.
    """
    # Parser la date target en format français (jour/mois/année)
    parts = target_date.split('/')
    if len(parts) == 3:
        day_fr = int(parts[0])
        month_fr = int(parts[1])
        year_fr = int(parts[2])
        
        # Stratégie 1: Format français (jour/mois/année)
        # Chercher datetime(year, month, day)
        for col in df.columns:
            if isinstance(col, (pd.Timestamp, datetime)):
                if col.year == year_fr and col.month == month_fr and col.day == day_fr:
                    return col
            # Aussi vérifier les colonnes string
            elif isinstance(col, str):
                if col.strip() == target_date:
                    return col
        
        # Stratégie 2: "7/5/2026" pourrait correspondre à datetime(2026, 7, 5)
        # si Excel affiche en format MM/DD (mois avant jour)
        for col in df.columns:
            if isinstance(col, (pd.Timestamp, datetime)):
                # Si le mois du datetime = premier chiffre ET jour = deuxième chiffre
                if col.year == year_fr and col.month == day_fr and col.day == month_fr:
                    return col
    
    raise ValueError(f"Colonne date introuvable : {target_date}")


def prepare_dataframe(path: str) -> pd.DataFrame:
    # header=1 => l'en-tête est sur la 2e ligne
    df = pd.read_excel(path, header=1, sheet_name=1)

    # Nettoyage des noms de colonnes (mais garder les datetime comme datetime)
    cleaned_cols = []
    for c in df.columns:
        if isinstance(c, (pd.Timestamp, datetime)):
            cleaned_cols.append(c)  # Garder les datetime tels quels
        else:
            cleaned_cols.append(str(c).strip())  # Nettoyer les strings
    df.columns = cleaned_cols

    # Colonnes obligatoires
    required_cols = ["Region", "Ville", "VENDOR", "STATUT"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le fichier : {missing}")

    # Trouver la colonne date
    date_col = find_date_column(df, TARGET_DATE)

    # Normalisation des champs utiles
    df["_REGION_N"] = df["Region"].map(normalize_text)
    df["_VILLE_N"] = df["Ville"].map(normalize_text)
    df["_VENDOR_N"] = df["VENDOR"].map(normalize_text)
    df["_STATUT_N"] = df["STATUT"].map(normalize_text)

    # Valeurs numériques sur la colonne date
    df["_VALUE"] = pd.to_numeric(df[date_col], errors="coerce").fillna(0)

    # Filtre statut
    df = df[df["_STATUT_N"].isin(VALID_STATUTS)].copy()

    return df


def mask_city_vendor(df, city: str, vendor: str) -> pd.Series:
    return (df["_VILLE_N"] == normalize_text(city)) & (df["_VENDOR_N"] == normalize_text(vendor))


def mask_region_vendor(df, region: str, vendor: str, exclude_capital: bool = True) -> pd.Series:
    region_n = normalize_text(region)
    vendor_n = normalize_text(vendor)
    mask = (df["_REGION_N"] == region_n) & (df["_VENDOR_N"] == vendor_n)
    if exclude_capital and region_n in CAPITALS_BY_REGION:
        mask &= (df["_VILLE_N"] != normalize_text(CAPITALS_BY_REGION[region_n]))
    return mask


def mask_region_all_except_zte(df, region: str, exclude_capital: bool = True) -> pd.Series:
    region_n = normalize_text(region)
    mask = (df["_REGION_N"] == region_n) & (df["_VENDOR_N"] != "ZTE")
    if exclude_capital and region_n in CAPITALS_BY_REGION:
        mask &= (df["_VILLE_N"] != normalize_text(CAPITALS_BY_REGION[region_n]))
    return mask


def mask_city_all_vendors(df, city: str) -> pd.Series:
    return df["_VILLE_N"] == normalize_text(city)


def summarize_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Les règles ci-dessous reprennent ta logique :
    - ville + vendor : ville précise, vendor précis
    - région + vendor : toute la région, capital exclue, vendor précis
    - région seule : toute la région, capital exclue, vendors sauf ZTE
    - ville seule : ville précise, tous vendors
    """

    targets = [
        # Ville + vendor
        ("DOUALA ZTE", lambda x: mask_city_vendor(x, "DOUALA", "ZTE")),
        ("YAOUNDE ZTE", lambda x: mask_city_vendor(x, "YAOUNDE", "ZTE")),
        ("ADAMAOUA HUAWEI", lambda x: mask_city_vendor(x, "NGAOUNDERE", "HUAWEI")),
        ("BAFOUSSAM HUAWEI", lambda x: mask_city_vendor(x, "BAFOUSSAM", "HUAWEI")),
        ("EXTREME NORD HUAWEI", lambda x: mask_city_vendor(x, "MAROUA", "HUAWEI")),
        ("GAROUA HUAWEI", lambda x: mask_city_vendor(x, "GAROUA", "HUAWEI")),
        ("MAROUA HUAWEI", lambda x: mask_city_vendor(x, "MAROUA", "HUAWEI")),
        ("NORD HUAWEI", lambda x: mask_city_vendor(x, "GAROUA", "HUAWEI")),
        ("NGAOUNDERE HUAWEI", lambda x: mask_city_vendor(x, "NGAOUNDERE", "HUAWEI")),
        ("OUEST HUAWEI", lambda x: mask_city_vendor(x, "BAFOUSSAM", "HUAWEI")),
        ("NORD OUEST - HUAWEI", lambda x: mask_city_vendor(x, "BAMENDA", "HUAWEI")),
        ("SUD OUEST HUAWEI", lambda x: mask_city_vendor(x, "BUEA", "HUAWEI")),

        # Région + vendor
        ("CENTRE ZTE", lambda x: mask_region_vendor(x, "CENTRE", "ZTE", exclude_capital=True)),
        ("LITTORAL ZTE", lambda x: mask_region_vendor(x, "LITTORAL", "ZTE", exclude_capital=True)),

        # Région seule = région complète sauf capitale, et sans ZTE
        ("ADAMAOUA", lambda x: mask_region_all_except_zte(x, "ADAMAOUA", exclude_capital=True)),
        ("CENTRE", lambda x: mask_region_all_except_zte(x, "CENTRE", exclude_capital=True)),
        ("EXTREME-NORD", lambda x: mask_region_all_except_zte(x, "EXTREME NORD", exclude_capital=True)),
        ("LITTORAL", lambda x: mask_region_all_except_zte(x, "LITTORAL", exclude_capital=True)),
        ("NORD", lambda x: mask_region_all_except_zte(x, "NORD", exclude_capital=True)),
        ("NORD-OUEST", lambda x: mask_region_all_except_zte(x, "NORD OUEST", exclude_capital=True)),
        ("OUEST", lambda x: mask_region_all_except_zte(x, "OUEST", exclude_capital=True)),
        ("SUD-OUEST", lambda x: mask_region_all_except_zte(x, "SUD OUEST", exclude_capital=True)),

        # Ville seule = ville précise, tous vendors
        ("BAFOUSSAM", lambda x: mask_city_all_vendors(x, "BAFOUSSAM")),
        ("DOUALA", lambda x: mask_city_all_vendors(x, "DOUALA")),
        ("GAROUA", lambda x: mask_city_all_vendors(x, "GAROUA")),
        ("MAROUA", lambda x: mask_city_all_vendors(x, "MAROUA")),
        ("NGAOUNDERE", lambda x: mask_city_all_vendors(x, "NGAOUNDERE")),
        ("YAOUNDE", lambda x: mask_city_all_vendors(x, "YAOUNDE")),
    ]

    rows = []
    for label, rule in targets:
        mask = rule(df)
        subset = df[mask]
        rows.append({
            "CIBLE": label,
            "NB_LIGNES": int(subset.shape[0]),
            "SOMME_7_5_2026": float(subset["_VALUE"].sum()),
        })

    return pd.DataFrame(rows)


def main():
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {input_path}")

    df = prepare_dataframe(str(input_path))
    summary = summarize_targets(df)

    # Export Excel
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="Synthese")
        df.to_excel(writer, index=False, sheet_name="Donnees_filtrees")

    print(f"Terminé. Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()