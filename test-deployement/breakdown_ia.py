# ══════════════════════════════════════════════════════════════
# breakdown_ia.py — Module d'intégration avec le serveur IA RunPod
# À importer dans ton app Flask existante
# ══════════════════════════════════════════════════════════════

import requests

# ⚠️ Remplace par l'URL réelle de ton pod RunPod (onglet Connect)
SERVEUR_IA_URL = "https://xxxxxxxx-8000.proxy.runpod.net"

TIMEOUT_CLASSIFIER = 1800  # 30 min max pour un gros fichier
TIMEOUT_CHAT = 30          # 30s max pour une réponse de chat


def verifier_serveur_ia():
    """Vérifie que le serveur IA est joignable et opérationnel."""
    try:
        r = requests.get(f"{SERVEUR_IA_URL}/health", timeout=5)
        if r.status_code == 200:
            return True, r.json()
        return False, {"erreur": f"Code HTTP {r.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"erreur": str(e)}


def classifier_fichier_excel(chemin_fichier_local):
    """
    Envoie un fichier Excel compilé au serveur IA et récupère
    le fichier enrichi de la cause prédite.

    Retourne : (succes: bool, contenu_bytes_ou_erreur)
    """
    try:
        with open(chemin_fichier_local, "rb") as f:
            fichier = {
                "file": (
                    "fichier.xlsx",
                    f,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            }
            response = requests.post(
                f"{SERVEUR_IA_URL}/classifier",
                files=fichier,
                timeout=TIMEOUT_CLASSIFIER,
            )

        if response.status_code == 200:
            return True, response.content
        else:
            return False, f"Erreur serveur IA ({response.status_code}) : {response.text[:300]}"

    except requests.exceptions.Timeout:
        return False, "Le traitement a dépassé le délai maximal. Réessaie avec un fichier plus petit ou vérifie le serveur."
    except requests.exceptions.RequestException as e:
        return False, f"Impossible de joindre le serveur IA : {e}"


def demander_cause_ia(commentaire, owner="", topology="", vendors=""):
    """
    Envoie un commentaire au modèle pour obtenir la cause prédite.

    Retourne : (succes: bool, dict_resultat_ou_message_erreur)
    """
    try:
        payload = {
            "commentaire": commentaire,
            "owner": owner,
            "topology": topology,
            "vendors": vendors,
        }
        response = requests.post(
            f"{SERVEUR_IA_URL}/chat", json=payload, timeout=TIMEOUT_CHAT
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Erreur serveur IA ({response.status_code}) : {response.text[:300]}"

    except requests.exceptions.Timeout:
        return False, "Le modèle met trop de temps à répondre. Réessaie."
    except requests.exceptions.RequestException as e:
        return False, f"Impossible de joindre le serveur IA : {e}"