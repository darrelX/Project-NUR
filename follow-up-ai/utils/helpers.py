"""
Fonctions utilitaires pour le projet de fine-tuning
"""

import os
import gc
import torch
from typing import Optional
from .constants import PATTERN_IMPACT, PATTERN_CODE_SITE, CATEGORIES


def propre(v) -> str:
    """
    Nettoie une valeur en supprimant les espaces et les valeurs vides
    
    Args:
        v: Valeur à nettoyer
        
    Returns:
        Chaîne nettoyée ou chaîne vide si la valeur est invalide
    """
    s = str(v).strip()
    return "" if s.lower() in ["nan", "n/a", "none", "", "-"] else s


def est_impacte(commentaire: str) -> bool:
    """
    Détecte si un commentaire indique qu'un site est impacté par un autre
    
    Args:
        commentaire: Texte du commentaire
        
    Returns:
        True si le site est impacté par un autre site
    """
    return bool(PATTERN_IMPACT.search(commentaire))


def extraire_site_impactant(commentaire: str) -> Optional[str]:
    """
    Extrait le code du site qui cause l'impact depuis le commentaire
    
    Args:
        commentaire: Texte du commentaire
        
    Returns:
        Code du site impactant (ex: 'LIT_123') ou None
    """
    codes = PATTERN_CODE_SITE.findall(commentaire)
    if codes:
        return codes[0].upper()
    return None


def normaliser_cause(cause_brute: str) -> str:
    """
    Normalise une cause prédite vers une catégorie officielle
    
    Args:
        cause_brute: Cause retournée par le modèle
        
    Returns:
        Catégorie officielle correspondante ou la cause brute si pas trouvée
    """
    cause_norm = cause_brute.strip()
    for cat in CATEGORIES:
        if cat.lower() in cause_norm.lower():
            return cat
    return cause_norm


def extraire_cause_de_reponse(reponse: str) -> str:
    """
    Extrait la cause depuis la réponse du modèle
    
    Args:
        reponse: Réponse complète du modèle
        
    Returns:
        Cause extraite
    """
    cause = ""
    if "Cause :" in reponse:
        cause = reponse.split("Cause :")[-1].strip().split("\n")[0].strip()
    elif "Cause:" in reponse:
        cause = reponse.split("Cause:")[-1].strip().split("\n")[0].strip()
    else:
        cause = reponse[:100].strip()
    return cause


def nettoyer_memoire():
    """
    Libère la mémoire GPU et RAM
    """
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def afficher_info_gpu():
    """
    Affiche les informations GPU disponibles
    """
    if torch.cuda.is_available():
        print(f"GPU : {torch.cuda.get_device_name(0)}")
        print(f"VRAM totale : {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f} GB")
        print(f"VRAM allouée : {torch.cuda.memory_allocated()/1024**3:.1f} GB")
    else:
        print("⚠️  Aucun GPU disponible")


def creer_dossier(chemin: str):
    """
    Crée un dossier s'il n'existe pas
    
    Args:
        chemin: Chemin du dossier à créer
    """
    os.makedirs(chemin, exist_ok=True)


def construire_prompt_utilisateur(commentaire: str, owner: str = "", 
                                   topology: str = "", vendors: str = "") -> str:
    """
    Construit le prompt utilisateur avec les informations contextuelles
    
    Args:
        commentaire: Commentaire de l'incident
        owner: Gestionnaire du site (optionnel)
        topology: Configuration électrique du site (optionnel)
        vendors: Équipementier radio (optionnel)
        
    Returns:
        Prompt formaté pour l'utilisateur
    """
    user = f"Commentaire : {commentaire.strip()}"
    if propre(owner):
        user += f"\nOwner : {propre(owner)}"
    if propre(topology):
        user += f"\nTopology : {propre(topology)}"
    if propre(vendors):
        user += f"\nVendors : {propre(vendors)}"
    return user


def creer_analyse_resume(commentaire: str, max_len: int = 250) -> str:
    """
    Crée un résumé d'analyse à partir d'un commentaire
    
    Args:
        commentaire: Commentaire complet
        max_len: Longueur maximale du résumé
        
    Returns:
        Résumé du commentaire
    """
    analyse = commentaire[:max_len].replace("\n", " ").strip()
    if len(commentaire) > max_len:
        analyse += "..."
    return analyse
