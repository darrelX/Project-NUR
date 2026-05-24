"""
Constantes globales pour le projet de fine-tuning
"""

# ══════════════════════════════════════════════════════════════
# CATÉGORIES OFFICIELLES
# ══════════════════════════════════════════════════════════════

CATEGORIES = [
    "MPR issue",
    "BSS Hardware issue",
    "AKTIVCO Defaut GE & Power Cabinet",
    "AKTIVCO Coupure ENEO & Baisse de tension",
    "Coupure ENEO & Baisse de tension",
    "Defaut GE & Power Cabinet",
    "Sharing",
    "SPARE-ISSUE",
    "Fiber AOF",
    "Projet OCM (HUAWEI)",
    "ACCESS-ISSUE",
    "Projet OCM (ZTE, NOKIA, autres projets)",
    "ODU HS",
    "IP & VLAN",
    "Warehouse HUAWEI",
]

# ══════════════════════════════════════════════════════════════
# SYSTEM PROMPT
# ══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Tu es un expert en analyse d'incidents réseau télécom au monde.

Tu reçois un commentaire d'incident. Selon le type d'incident, tu peux aussi recevoir :
- Owner : le gestionnaire du site
- Topology : la configuration électrique du site,l'entreprise qui s'occupe de l'energie sur le site
- Vendors : l'équipementier radio (ZTE, HUAWEI, NOKIA)
je veux que tu analyse le commentaire , que tu le comprenne , que tu raisonne que tu comprenne si l'incident est cloturer ou si il est encore en cours.
Tu dois identifier la cause racine parmi ces 15 catégories EXACTES :
1. MPR issue
2. BSS Hardware issue
3. AKTIVCO Defaut GE & Power Cabinet
4. AKTIVCO Coupure ENEO & Baisse de tension
5. Coupure ENEO & Baisse de tension
6. Defaut GE & Power Cabinet
7. Sharing
8. SPARE-ISSUE
9. Fiber AOF
10. Projet OCM (HUAWEI)
11. ACCESS-ISSUE
12. Projet OCM (ZTE, NOKIA, autres projets)
13. ODU HS
14. IP & VLAN
15. Warehouse HUAWEI

Réponds UNIQUEMENT avec : Cause : [la cause exacte de la liste ci-dessus]"""

# ══════════════════════════════════════════════════════════════
# CATÉGORIES NÉCESSITANT DES CHAMPS SPÉCIFIQUES
# ══════════════════════════════════════════════════════════════

BESOIN_OWNER_TOPOLOGY = {
    "AKTIVCO Defaut GE & Power Cabinet",
    "AKTIVCO Coupure ENEO & Baisse de tension",
    "Defaut GE & Power Cabinet",
    "Coupure ENEO & Baisse de tension",
    "Sharing",
}

BESOIN_VENDORS = {
    "Projet OCM (HUAWEI)",
    "Projet OCM (ZTE, NOKIA, autres projets)",
}

# ══════════════════════════════════════════════════════════════
# PATTERNS REGEX POUR L'ANALYSE
# ══════════════════════════════════════════════════════════════

import re

# Mots-clés pour détecter les sites impactés
MOTS_CLES_IMPACT = [
    r"indisponibilit[eé] des services? voix\s*[&et]+\s*data dans la localit[eé] de",
    r"impacted?\s+by",
    r"impact[eé]r?\s+par",
    r"incident\s+at",
    r"probabl[e]?\s+probl[eè]me\s+de\s+.{0,30}\s+sur le site\s+de",
    r"affect(?:ed)?\s+by",
]

PATTERN_IMPACT = re.compile(
    "|".join(MOTS_CLES_IMPACT),
    re.IGNORECASE
)

# Pattern pour extraire code site (ex: LIT_123, CTR_456, SUO_789)
PATTERN_CODE_SITE = re.compile(
    r'\b([A-Z]{2,4}_\d{3,4})\b',
    re.IGNORECASE
)

# ══════════════════════════════════════════════════════════════
# PARAMÈTRES MODÈLE
# ══════════════════════════════════════════════════════════════

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

# ══════════════════════════════════════════════════════════════
# PARAMÈTRES GÉNÉRATION
# ══════════════════════════════════════════════════════════════

GENERATION_CONFIG = {
    "max_new_tokens": 80,
    "do_sample": False,
    "temperature": 1.0,
    "repetition_penalty": 1.1,
}
