import re
import unicodedata
from pathlib import Path

import pandas as pd


# =========================
# CONFIGURATION
# =========================
CONFIG = {
    "source_type": "excel",  # Options: "excel", "csv", "dataframe"
    "input_file": Path("inputs/APRIL BREAKDOWN.xlsx"),
    "output_file": Path("inputs/APRIL BREAKDOWN_OUTPUT.xlsx"),
    "sheet_name": "BREAKDOWN",
    # Pour CSV
    "csv_encoding": "utf-8",
    "csv_separator": ",",
}


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
    "ge"
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


# =========================
# CRÉATION DE DATAFRAME DEPUIS LISTE
# =========================
def create_dataframe_from_comments(
    comments: list[str],
    owners: list[str] | str | None = None,
    topologies: list[str] | str | None = None,
) -> pd.DataFrame:
    """
    Crée un DataFrame à partir d'une liste de commentaires.
    
    Cette fonction est utile pour créer rapidement des données de test
    ou pour intégrer des données provenant d'autres sources (API, base de données, etc.).
    La complexité est automatiquement définie à "Cas Simple" pour tous les commentaires.
    
    Args:
        comments: Liste de commentaires (obligatoire)
        owners: Owner(s) - peut être:
            - None: utilise "IHS" par défaut pour tous
            - str: même valeur pour tous les commentaires
            - list[str]: une valeur par commentaire (doit avoir même longueur que comments)
        topologies: Topologie(s) - peut être:
            - None: utilise "Grid Only" par défaut pour tous
            - str: même valeur pour tous les commentaires
            - list[str]: une valeur par commentaire (doit avoir même longueur que comments)
    
    Returns:
        DataFrame avec les colonnes COMMENTAIRE, Owner, Topology, Complexity (= "Cas Simple")
    
    Examples:
        >>> # Utilisation basique avec valeurs par défaut
        >>> comments = ["Grid outage", "Power cut", "ENEO failure"]
        >>> df = create_dataframe_from_comments(comments)
        
        >>> # Avec owners spécifiques
        >>> df = create_dataframe_from_comments(
        ...     comments=["Grid outage", "Power cut"],
        ...     owners=["IHS", "CAMUSAT"]
        ... )
        
        >>> # Avec une valeur unique pour tous
        >>> df = create_dataframe_from_comments(
        ...     comments=["Grid outage", "Power cut"],
        ...     owners="CAMUSAT",
        ...     topologies="Grid Only"
        ... )
    """
    n = len(comments)
    
    if n == 0:
        raise ValueError("La liste de commentaires ne peut pas être vide")
    
    # Gestion des owners
    if owners is None:
        owners_list = ["IHS"] * n
    elif isinstance(owners, str):
        owners_list = [owners] * n
    elif isinstance(owners, list):
        if len(owners) != n:
            raise ValueError(
                f"La liste owners doit avoir la même longueur que comments "
                f"({len(owners)} != {n})"
            )
        owners_list = owners
    else:
        raise TypeError("owners doit être None, str, ou list[str]")
    
    # Gestion des topologies
    if topologies is None:
        topologies_list = ["Grid Only"] * n
    elif isinstance(topologies, str):
        topologies_list = [topologies] * n
    elif isinstance(topologies, list):
        if len(topologies) != n:
            raise ValueError(
                f"La liste topologies doit avoir la même longueur que comments "
                f"({len(topologies)} != {n})"
            )
        topologies_list = topologies
    else:
        raise TypeError("topologies doit être None, str, ou list[str]")
    
    # Création du DataFrame (Complexity toujours "Cas Simple")
    df = pd.DataFrame({
        "COMMENTAIRE": comments,
        "Owner": owners_list,
        "Topology": topologies_list,
        "Complexity": ["Cas Simple"] * n,
    })
    
    return df


# =========================
# CHARGEMENT DES DONNÉES
# =========================
def load_data_from_excel(file_path: Path, sheet_name: str) -> pd.DataFrame:
    """Charge les données depuis un fichier Excel."""
    return pd.read_excel(file_path, sheet_name=sheet_name)


def load_data_from_csv(file_path: Path, encoding: str = "utf-8", separator: str = ",") -> pd.DataFrame:
    """Charge les données depuis un fichier CSV."""
    return pd.read_csv(file_path, encoding=encoding, sep=separator)


def load_data_from_config(config: dict) -> pd.DataFrame:
    """
    Charge les données selon la configuration spécifiée.
    
    Args:
        config: Dictionnaire de configuration contenant:
            - source_type: Type de source ("excel", "csv", "dataframe")
            - input_file: Chemin du fichier (pour excel/csv)
            - sheet_name: Nom de la feuille (pour excel)
            - csv_encoding: Encodage (pour csv)
            - csv_separator: Séparateur (pour csv)
    
    Returns:
        DataFrame chargé
    """
    source_type = config.get("source_type", "excel")
    
    if source_type == "excel":
        return load_data_from_excel(
            config["input_file"],
            config["sheet_name"]
        )
    elif source_type == "csv":
        return load_data_from_csv(
            config["input_file"],
            encoding=config.get("csv_encoding", "utf-8"),
            separator=config.get("csv_separator", ",")
        )
    else:
        raise ValueError(f"Type de source non supporté: {source_type}")


# =========================
# TRAITEMENT PRINCIPAL
# =========================
def process_breakdown_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction principale de traitement des données de breakdown.
    
    Cette fonction applique la logique d'enrichissement sur un DataFrame:
    - Détection des cas simples
    - Détermination du SUB RCA basé sur le commentaire, owner et topology
    - Enrichissement avec CATEGORY, CAUSE et OCM_NOMENCLATURE
    
    Args:
        df: DataFrame contenant les colonnes requises (COMMENTAIRE, Owner, etc.)
    
    Returns:
        DataFrame enrichi avec les colonnes SUB RCA, CATEGORY, CAUSE, OCM_NOMENCLATURE
    """
    df = df.copy()

    # Sécurité minimale sur les colonnes attendues
    expected_cols = ["COMMENTAIRE", "Owner"]
    for col in expected_cols:
        if col not in df.columns:
            raise KeyError(f"Colonne manquante: {col}")

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


def save_data(df: pd.DataFrame, output_path: Path, output_format: str = "excel"):
    """
    Sauvegarde le DataFrame dans le format spécifié.
    
    Args:
        df: DataFrame à sauvegarder
        output_path: Chemin du fichier de sortie
        output_format: Format de sortie ("excel" ou "csv")
    """
    if output_format == "excel":
        df.to_excel(output_path, index=False)
    elif output_format == "csv":
        df.to_csv(output_path, index=False, encoding="utf-8")
    else:
        raise ValueError(f"Format de sortie non supporté: {output_format}")


def main(config: dict = None):
    """
    Fonction principale orchestrant le chargement, traitement et sauvegarde des données.
    
    Args:
        config: Dictionnaire de configuration optionnel. Si None, utilise CONFIG global.
    """
    if config is None:
        config = CONFIG
    
    # Chargement des données selon la configuration
    df = load_data_from_config(config)
    
    # Traitement des données
    df_out = process_breakdown_data(df)
    
    # Sauvegarde
    output_file = config.get("output_file", Path("output.xlsx"))
    save_data(df_out, output_file)
    
    print(f"Fichier généré: {output_file}")


if __name__ == "__main__":
    main()