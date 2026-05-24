import re
import unicodedata
from pathlib import Path

import pandas as pd


# =========================
# FICHIER SOURCE
# =========================
file = Path("inputs/APRIL BREAKDOWN.xlsx")
output_file = Path("inputs/APRIL BREAKDOWN_OUTPUT.xlsx")
sheet_name = "BREAKDOWN"


# =========================
# REFERENTIELS
# =========================
TOPOLOGIES_GRID_ONLY = {
    "Grid Only",
    "Good Grid no GE - 8h",
    "Good Grid no GE - 12h",
    "Good Grid no GE 8H",
    "Solar Only",
    "GridOnly",
}

# Liste initiale des mots-clés de détection du problème "power"
# Tu pourras l'enrichir plus tard.
POWER_KEYWORDS = [
    "power",
    "grid outage",
    "awaiting grid return",
    "ENEO",
    "Plan d'action en cours",
    "baisse de tension",
    "coupure",
    "enoe",
    "grid failure",
    "grid down",
    "power cut",
    "power outage",
    "electricity",
    "mains failure",
    "grid issue",
    "bat GE hs",
    ""
]


# SUB RCA
SUB_RCA = [
    "MPR issue",
    "BSS Hardware issue",
    "Sites strategiques, MLL, Pylone, etc.",
    "AKTIVCO Defaut GE & Power Cabinet",
    "AKTIVCO Coupure ENEO & Baisse de tension",
    "Coupure ENEO & Baisse de tension",
    "Defaut GE & Power Cabinet",
    "Sharing",
    "Sites strategiques & DataCenter",
    "Exclu",
    "SAT",
    "SPARE-ISSUE",
    "Fiber CAMTEL",
    "Fiber AOF",
    "Projet OCM (HUAWEI)",
    "Projet OCM (NOKIA)",
    "ACCESS-ISSUE",
    "Projet OCM (ZTE, NOKIA, autres projets)",
    "No root cause",
    "ODU HS",
    "IP & VLAN",
    "Warehouse HUAWEI",
    "SPARE-HS",
    "Power Telco",
    "no impacts",
]

# MAPPING CATEGORY
CATEGORIES = {
    "MPR issue": "ACTIVE",
    "BSS Hardware issue": "ACTIVE",
    "Sites strategiques, MLL, Pylone, etc.": "PASSIVE",
    "AKTIVCO Defaut GE & Power Cabinet": "PASSIVE",
    "AKTIVCO Coupure ENEO & Baisse de tension": "PASSIVE",
    "Coupure ENEO & Baisse de tension": "PASSIVE",
    "Defaut GE & Power Cabinet": "PASSIVE",
    "Sharing": "PASSIVE",
    "Sites strategiques & DataCenter": "PASSIVE",
    "Exclu": "Exclu",
    "SAT": "ACTIVE",
    "SPARE-ISSUE": "SPARE-ISSUE",
    "Fiber CAMTEL": "ACTIVE",
    "Fiber AOF": "ACTIVE",
    "Projet OCM (HUAWEI)": "PLANNED WORKS",
    "Projet OCM (NOKIA)": "PLANNED WORKS",
    "ACCESS-ISSUE": "ACCESS-ISSUE",
    "Projet OCM (ZTE, NOKIA, autres projets)": "PLANNED WORKS",
    "No root cause": "No root cause",
    "ODU HS": "ACTIVE",
    "IP & VLAN": "ACTIVE",
    "Warehouse HUAWEI": "SPARE-ISSUE",
    "SPARE-HS": "SPARE-ISSUE",
    "Power Telco": "ACTIVE",
    "no impacts": "no impacts",
}

# MAPPING CAUSE
CAUSE = {
    "MPR issue": "TX ISSUE",
    "BSS Hardware issue": "RAN ISSUE",
    "Sites strategiques, MLL, Pylone, etc.": "ENVTECH",
    "AKTIVCO Defaut GE & Power Cabinet": "POWER ISSUE",
    "AKTIVCO Coupure ENEO & Baisse de tension": "POWER ISSUE",
    "Coupure ENEO & Baisse de tension": "POWER ISSUE",
    "Defaut GE & Power Cabinet": "POWER ISSUE",
    "Sharing": "POWER ISSUE",
    "Sites strategiques & DataCenter": "POWER ISSUE",
    "Exclu": "Exclu",
    "SAT": "TX ISSUE",
    "SPARE-ISSUE": "SPARE-ISSUE",
    "Fiber CAMTEL": "TX ISSUE",
    "Fiber AOF": "TX ISSUE",
    "Projet OCM (HUAWEI)": "TRAVAUX-HUAWEI",
    "Projet OCM (NOKIA)": "TRAVAUX-NOKIA",
    "ACCESS-ISSUE": "ACCESS-ISSUE",
    "Projet OCM (ZTE, NOKIA, autres projets)": "TRAVAUX OCM",
    "No root cause": "No root cause",
    "ODU HS": "TX ISSUE",
    "IP & VLAN": "TX ISSUE",
    "Warehouse HUAWEI": "SPARE-ISSUE",
    "SPARE-HS": "SPARE-ISSUE",
    "Power Telco": "RAN ISSUE",
    "no impacts": "no impacts",
}

# MAPPING OCM NOMENCLATURE
OCM_NOMENCLATURE = {
    "MPR issue": "PDH",
    "BSS Hardware issue": "BSS",
    "Sites strategiques, MLL, Pylone, etc.": "ENVTECH",
    "AKTIVCO Defaut GE & Power Cabinet": "AKTIVCO",
    "AKTIVCO Coupure ENEO & Baisse de tension": "AKTIVCO GRID ONLY",
    "Coupure ENEO & Baisse de tension": "IHS GRID ONLY",
    "Defaut GE & Power Cabinet": "IHS",
    "Sharing": "Partners",
    "Sites strategiques & DataCenter": "SST & DC",
    "Exclu": "Exclu",
    "SAT": "SAT",
    "SPARE-ISSUE": "SPARE-ISSUE",
    "Fiber CAMTEL": "TRANS_FO_CAMTEL",
    "Fiber AOF": "Fiber AOF",
    "Projet OCM (HUAWEI)": "TRAVAUX-HUAWEI",
    "Projet OCM (NOKIA)": "TRAVAUX-NOKIA",
    "ACCESS-ISSUE": "ACCESS-ISSUE",
    "Projet OCM (ZTE, NOKIA, autres projets)": "TRAVAUX OCM",
    "No root cause": "No root cause",
    "ODU HS": "PDH",
    "IP & VLAN": "PDH",
    "Warehouse HUAWEI": "SPARE-ISSUE",
    "SPARE-HS": "SPARE-ISSUE",
    "Power Telco": "BSS",
    "no impacts": "no impacts",
}


# =========================
# OUTILS
# =========================
def normalize_text(value) -> str:
    """
    Met le texte en minuscule, enlève les accents, supprime la ponctuation
    et compacte les espaces.
    """
    if pd.isna(value):
        return ""

    text = str(value).lower()

    # Suppression des accents
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))

    # Remplacement de toute ponctuation / symbole par espace
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Compactage des espaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def contains_any_keyword(text: str, keywords: list[str]) -> bool:
    """
    Retourne True si le texte contient au moins un mot-clé.
    La comparaison se fait sur texte normalisé.
    """
    normalized_text = normalize_text(text)
    if not normalized_text:
        return False

    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        if normalized_keyword and normalized_keyword in normalized_text:
            return True
    return False


def detect_power_problem(commentaire) -> bool:
    """
    Détecte si le commentaire parle d'un problème de power.
    Pour le moment : simple détection par mots-clés.
    """
    return contains_any_keyword(commentaire, POWER_KEYWORDS)


def normalize_owner(owner) -> str:
    return normalize_text(owner).upper()


def normalize_topology(topology) -> str:
    return normalize_text(topology)


def is_grid_only_topology(topology) -> bool:
    """
    Vérifie si la topology appartient à la famille Grid Only.
    On compare en version normalisée pour gérer les variations de casse / ponctuation.
    """
    topo_norm = normalize_topology(topology)
    for topo in TOPOLOGIES_GRID_ONLY:
        if normalize_topology(topo) == topo_norm:
            return True
    return False


def is_simple_case(complexity_value) -> bool:
    """
    Filtre les cas simples.
    Adapté pour tolérer des variantes comme:
    - cas simple
    - Cas Simple
    - simple
    """
    txt = normalize_text(complexity_value)
    return "cas simple" in txt or txt == "simple"


def determine_sub_rca(row: pd.Series) -> str | None:
    """
    Détermine le SUB RCA à partir de COMMENTAIRE + Owner + Topology.
    Pour le moment, la logique ne traite que les cas power simples.
    """
    commentaire = row.get("COMMENTAIRE", "")
    owner = row.get("Owner", "")
    topology = row.get("Topolopgy", row.get("Topology", ""))

    if not detect_power_problem(commentaire):
        return None

    owner_norm = normalize_owner(owner)

    if owner_norm == "IHS":
        if is_grid_only_topology(topology):
            return "Coupure ENEO & Baisse de tension"
        return "Defaut GE & Power Cabinet"

    if owner_norm in {"CAMUSAT", "ESCO"}:
        if is_grid_only_topology(topology):
            return "AKTIVCO Coupure ENEO & Baisse de tension"
        return "AKTIVCO Defaut GE & Power Cabinet"

    return None


def build_enrichment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique la logique uniquement sur les cas simples.
    Les autres lignes gardent leur valeur actuelle de SUB RCA.
    """
    df = df.copy()

    # Récupération souple des noms de colonnes selon les variantes
    complexity_col = None
    for candidate in ["Complexity", "complexite", "COMPLEXITY", "complexité"]:
        if candidate in df.columns:
            complexity_col = candidate
            break

    if complexity_col is None:
        raise KeyError("Colonne de complexité introuvable. Attendu: 'Complexity' ou 'complexite'.")

    if "SUB RCA" not in df.columns:
        df["SUB RCA"] = None

    simple_mask = df[complexity_col].apply(is_simple_case)

    # On remplit SUB RCA seulement pour les cas simples
    df.loc[simple_mask, "SUB RCA"] = df.loc[simple_mask].apply(determine_sub_rca, axis=1)

    # Les autres colonnes sont dérivées de SUB RCA
    df["CATEGORY"] = df["SUB RCA"].map(CATEGORIES)
    df["CAUSE"] = df["SUB RCA"].map(CAUSE)
    df["OCM_NOMENCLATURE"] = df["SUB RCA"].map(OCM_NOMENCLATURE)

    return df


def main():
    df = pd.read_excel(file, sheet_name=sheet_name)

    # Sécurité minimale sur les colonnes attendues
    expected_cols = ["COMMENTAIRE", "Owner"]
    for col in expected_cols:
        if col not in df.columns:
            raise KeyError(f"Colonne manquante: {col}")

    df_out = build_enrichment(df)
    df_out.to_excel(output_file, index=False)

    print(f"Fichier généré: {output_file}")


if __name__ == "__main__":
    main()