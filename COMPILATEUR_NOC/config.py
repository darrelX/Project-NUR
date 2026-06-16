# ============================================================================
# config.py - Configuration globale du compilateur NOC
# ============================================================================

# Colonne clé dans le fichier principal
COL_CODE_SITE = "Code site"

# Formats de date acceptés
DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y",
    "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y",
]

# ============================================================================
# CONFIGURATION DES SOURCES
# ============================================================================

SOURCES = {
    "incident": {
        "nom": "INCIDENT",
        "colonne_cle": "Code ID",
        "colonnes_disponibles": ["root cause"],
        "filtre_date": False,
    },
    "top_offenders": {
        "nom": "Top Offenders",
        "colonne_cle": "Code ID",
        "colonnes_disponibles": ["Comment"],
        "filtre_date": False,
    },
    "retour_camusat": {
        "nom": "RETOUR CAMUSAT",
        "colonne_cle": "Code ID",
        "colonnes_disponibles": ["CAMUSAT Feedback"],
        "filtre_date": False,
    },
    "retour_ihs": {
        "nom": "RETOUR IHS",
        "colonne_cle": "Code ID",
        "colonnes_disponibles": ["Owner"],
        "filtre_date": False,
    },
    "hourly_ihs": {
        "nom": "Hourly IHS",
        "colonne_cle": "Code ID",
        "colonnes_disponibles": ["Event time", "Duration", "CMS", "Last Timeline Message"],
        "filtre_date": False,
    },
    "cells_down": {
        "nom": "Cells DOWN",
        "colonne_cle": "Code ID",
        "colonnes_disponibles": ["Comment", "Action Plan"],
        "filtre_date": True,
    },
    "ocm_ran": {
        "nom": "OCM RAN Incident",
        "colonne_cle": "Site ID",
        "colonnes_disponibles": ["Actions en cours"],
        "filtre_date": False,
    },
    "ticket": {
        "nom": "Ticket",
        "colonne_cle": "Site ID(Create TT)",
        "colonnes_disponibles": ["L", "W", "X", "Y", "Z", "AB"],
        "filtre_date": False,
    },
    "dashboard_cell": {
        "nom": "Dashbord Cell",
        "colonne_cle": "Code ID",
        "colonnes_disponibles": ["Comment"],
        "filtre_date": False,
    },
}

# Ordre des colonnes dans le fichier final
ORDRE_COLONNES = [
    "INCIDENT",
    "top offenders",
    "RETOUR CAMUSAT",
    "RETOUR IHS",
    "Hourly IHS",
    # Cells DOWN (colonnes dynamiques)
    # OCM RAN (colonnes dynamiques)
    "Ticket",
    "Dashbord suivi TOP OFFENDERS",
]