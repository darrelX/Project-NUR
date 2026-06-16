import re
import unicodedata
from pathlib import Path
from datetime import datetime
import pandas as pd


# =========================
# PARAMÈTRES GÉNÉRAUX
# =========================
INPUT_FILE = r"C:\Users\f50056342\Desktop\my work\REPETITIVES\STATUT DES SITES JOURNALIERS\statut.xlsx"
OUTPUT_FILE = r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\outputs\resultat_synthese.xlsx"

TARGET_DATE = ["14/6/2026", "15/6/2026"]   # Liste des dates à exploiter
VALID_STATUTS = {"OPERATIONNEL", "INSECURITE"}
VALID_VENDORS = {"ZTE", "HUAWEI", "NOKIA"}


# Capitale de chaque région
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


def find_date_column(df: pd.DataFrame, target_date: str):
    """
    Trouve la colonne correspondant à la date cible.
    target_date au format: "7/5/2026" (jour/mois/année).
    Retourne l'objet colonne (datetime ou string).
    """
    parts = target_date.split('/')
    if len(parts) != 3:
        raise ValueError(f"Format de date invalide : {target_date}")

    day_fr = int(parts[0])
    month_fr = int(parts[1])
    year_fr = int(parts[2])

    # Stratégie 1: format français (jour/mois/année)
    for col in df.columns:
        if isinstance(col, (pd.Timestamp, datetime)):
            if col.year == year_fr and col.month == month_fr and col.day == day_fr:
                return col
        elif isinstance(col, str):
            if col.strip() == target_date:
                return col

    # Stratégie 2: format américain (mois/jour/année)
    for col in df.columns:
        if isinstance(col, (pd.Timestamp, datetime)):
            if col.year == year_fr and col.month == day_fr and col.day == month_fr:
                return col

    raise ValueError(f"Colonne date introuvable : {target_date}")


def prepare_dataframe(path: str, sheet_name: str):
    """
    Lit le fichier, nettoie les colonnes, filtre les lignes selon les statuts valides.
    Retourne (df, date_columns) où date_columns est un dict {target_date: column_object}.
    """
    df = pd.read_excel(path, header=1, sheet_name=sheet_name)

    # Nettoyage des noms de colonnes (garder les datetime)
    cleaned_cols = []
    for c in df.columns:
        if isinstance(c, (pd.Timestamp, datetime)):
            cleaned_cols.append(c)
        else:
            cleaned_cols.append(str(c).strip())
    df.columns = cleaned_cols

    # Colonnes obligatoires
    required_cols = ["Region", "Ville", "VENDOR", "STATUT"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le fichier : {missing}")

    # Normalisation des champs utiles
    df["_REGION_N"] = df["Region"].map(normalize_text)
    df["_VILLE_N"] = df["Ville"].map(normalize_text)
    df["_VENDOR_N"] = df["VENDOR"].map(normalize_text)
    df["_STATUT_N"] = df["STATUT"].map(normalize_text)

    # Filtre statut
    df = df[df["_STATUT_N"].isin(VALID_STATUTS)].copy()

    # Construction du mapping date -> colonne
    date_columns = {}
    for date_str in TARGET_DATE:
        col = find_date_column(df, date_str)
        date_columns[date_str] = col

    return df, date_columns


def mask_city_vendor(df, city: str, vendor: str) -> pd.Series:
    return (df["_VILLE_N"] == normalize_text(city)) & (df["_VENDOR_N"] == normalize_text(vendor))


def mask_region_vendor(df, region: str, vendor: str, exclude_capital: bool = True) -> pd.Series:
    region_n = normalize_text(region)
    vendor_n = normalize_text(vendor)
    mask = (df["_REGION_N"] == region_n) & (df["_VENDOR_N"] == vendor_n)
    if exclude_capital and region_n in CAPITALS_BY_REGION:
        mask &= (df["_VILLE_N"] != normalize_text(CAPITALS_BY_REGION[region_n]))
    return mask


def mask_region(df, region: str, exclude_capital: bool = True) -> pd.Series:
    region_n = normalize_text(region)
    mask = (df["_REGION_N"] == region_n)
    if exclude_capital and region_n in CAPITALS_BY_REGION:
        mask &= (df["_VILLE_N"] != normalize_text(CAPITALS_BY_REGION[region_n]))
    return mask


def mask_region_all_except_vendor(df, region: str, exclude_vendor: str, exclude_capital: bool = True) -> pd.Series:
    region_n = normalize_text(region)
    exclude_vendor_n = normalize_text(exclude_vendor)
    mask = (df["_REGION_N"] == region_n) & (df["_VENDOR_N"] != exclude_vendor_n)
    if exclude_capital and region_n in CAPITALS_BY_REGION:
        mask &= (df["_VILLE_N"] != normalize_text(CAPITALS_BY_REGION[region_n]))
    return mask


def mask_city_all_vendors(df, city: str, exclude_vendor: str = None) -> pd.Series:
    mask = df["_VILLE_N"] == normalize_text(city)
    if exclude_vendor:
        mask &= df["_VENDOR_N"] != normalize_text(exclude_vendor)
    return mask


def summarize_targets(df: pd.DataFrame, date_columns: dict) -> pd.DataFrame:
    """
    Calcule pour chaque cible :
      - NB_LIGNES (indépendant de la date)
      - SOMME pour chaque date cible (à partir de la colonne correspondante)
    """
    targets = [
        # Ville + vendor
        ("DOUALA ZTE", lambda x: mask_city_vendor(x, "DOUALA", "ZTE")),
        ("YAOUNDE ZTE", lambda x: mask_city_vendor(x, "YAOUNDE", "ZTE")),
        ("CENTRE ZTE", lambda x: mask_region_vendor(x, "CENTRE", "ZTE", exclude_capital=True)),
        ("LITTORAL ZTE", lambda x: mask_region_vendor(x, "LITTORAL", "ZTE", exclude_capital=True)),
        ("ADAMAOUA HUAWEI", lambda x: mask_region_vendor(x, "ADAMAOUA", "HUAWEI", exclude_capital=True)),
        ("BAFOUSSAM HUAWEI", lambda x: mask_city_vendor(x, "BAFOUSSAM", "HUAWEI")),
        ("EXTREME NORD HUAWEI", lambda x: mask_region_vendor(x, "EXTREME NORD", "HUAWEI", exclude_capital=True)),
        ("GAROUA HUAWEI", lambda x: mask_city_vendor(x, "GAROUA", "HUAWEI")),
        ("MAROUA HUAWEI", lambda x: mask_city_vendor(x, "MAROUA", "HUAWEI")),
        ("NORD HUAWEI", lambda x: mask_region_vendor(x, "NORD", "HUAWEI", exclude_capital=True)),
        ("NGAOUNDERE HUAWEI", lambda x: mask_city_vendor(x, "NGAOUNDERE", "HUAWEI")),
        ("OUEST HUAWEI", lambda x: mask_city_vendor(x, "BAFOUSSAM", "HUAWEI")),
        ("NORD OUEST - HUAWEI", lambda x: mask_city_vendor(x, "BAMENDA", "HUAWEI")),
        ("SUD OUEST HUAWEI", lambda x: mask_city_vendor(x, "BUEA", "HUAWEI")),

        ("BAFOUSSAM", lambda x: mask_city_all_vendors(x, "BAFOUSSAM", exclude_vendor="HUAWEI")),
        ("ADAMAOUA", lambda x: mask_region_all_except_vendor(x, "ADAMAOUA", "HUAWEI", exclude_capital=True)),
        # Région + vendor
        ("CENTRE", lambda x: mask_region_vendor(x, "CENTRE", "ZTE", exclude_capital=True)),
        
        ("DOUALA", lambda x: mask_city_all_vendors(x, "DOUALA", exclude_vendor="ZTE")),
        ("EXTREME-NORD", lambda x: mask_region(x, "EXTREME NORD", exclude_capital=True)),        
        ("GAROUA", lambda x: mask_city_all_vendors(x, "GAROUA", exclude_vendor="HUAWEI")),
        ("LITTORAL", lambda x: mask_region(x, "LITTORAL", exclude_capital=True)),
        ("MAROUA", lambda x: mask_city_all_vendors(x, "MAROUA", exclude_vendor="HUAWEI")),
        ("NGAOUNDERE", lambda x: mask_city_all_vendors(x, "NGAOUNDERE", exclude_vendor="HUAWEI")),
        ("NORD", lambda x: mask_region(x, "NORD", exclude_capital=True)),
        ("NORD-OUEST", lambda x: mask_region(x, "NORD OUEST", exclude_capital=True)),
        ("OUEST", lambda x: mask_region(x, "OUEST", exclude_capital=True)),
        ("SUD-OUEST", lambda x: mask_region(x, "SUD OUEST", exclude_capital=False)),
        ("YAOUNDE", lambda x: mask_city_all_vendors(x, "YAOUNDE", exclude_vendor="ZTE")),
    ]

    rows = []
    for label, rule in targets:
        mask = rule(df)
        subset = df[mask]
        nb_lignes = int(subset.shape[0])

        # Dictionnaire des sommes pour chaque date
        sums = {}
        for date_str, col in date_columns.items():
            # Convertir la colonne en numérique, valeurs manquantes -> 0
            values = pd.to_numeric(subset[col], errors="coerce").fillna(0)
            sums[f"SOMME_{date_str}"] = float(values.sum())

        row = {"CIBLE": label, "NB_LIGNES": nb_lignes}
        row.update(sums)
        rows.append(row)

    return pd.DataFrame(rows)


def display_summary(summary_df: pd.DataFrame):
    """Affiche le tableau de synthèse dans le terminal."""
    print("\n" + "="*80)
    print("SYNTHÈSE DES RÉSULTATS (multi-dates)")
    print("="*80)
    print(summary_df.to_string(index=False))
    print("="*80 + "\n")


def main():
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {input_path}")

    df, date_columns = prepare_dataframe(str(input_path), sheet_name="SITE")
    summary = summarize_targets(df, date_columns)

    display_summary(summary)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="Synthese")
        df.to_excel(writer, index=False, sheet_name="Donnees_filtrees")

    print(f"Terminé. Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()