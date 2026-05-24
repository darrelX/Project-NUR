"""
Gestionnaire de prédiction pour le modèle fine-tuné
"""

import torch
from typing import Tuple, Optional
from utils.constants import SYSTEM_PROMPT, GENERATION_CONFIG
from utils.helpers import (
    construire_prompt_utilisateur,
    extraire_cause_de_reponse,
    normaliser_cause,
    creer_analyse_resume
)


class Predictor:
    """
    Classe pour effectuer des prédictions avec le modèle fine-tuné
    """
    
    def __init__(self, model, tokenizer):
        """
        Initialise le prédicteur
        
        Args:
            model: Modèle fine-tuné
            tokenizer: Tokenizer
        """
        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()
        
    def predire(self, commentaire: str, owner: str = "", 
                topology: str = "", vendors: str = "") -> Tuple[str, str, str]:
        """
        Effectue une prédiction sur un commentaire
        
        Args:
            commentaire: Commentaire de l'incident
            owner: Gestionnaire du site (optionnel)
            topology: Configuration électrique (optionnel)
            vendors: Équipementier radio (optionnel)
            
        Returns:
            Tuple (analyse, cause_normalisee, justification)
            - analyse: Résumé du commentaire
            - cause_normalisee: Cause prédite normalisée
            - justification: Réponse brute du modèle
        """
        # Construire le prompt
        user_content = construire_prompt_utilisateur(
            commentaire, owner, topology, vendors
        )
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
        
        # Appliquer le chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokeniser
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Générer
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=GENERATION_CONFIG["max_new_tokens"],
                do_sample=GENERATION_CONFIG["do_sample"],
                temperature=GENERATION_CONFIG["temperature"],
                repetition_penalty=GENERATION_CONFIG["repetition_penalty"],
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        # Décoder la réponse
        reponse = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        ).strip()
        
        # Extraire la cause
        cause_brute = extraire_cause_de_reponse(reponse)
        
        # Normaliser vers une catégorie officielle
        cause_norm = normaliser_cause(cause_brute)
        
        # Créer l'analyse (résumé du commentaire)
        analyse = creer_analyse_resume(commentaire, max_len=250)
        
        return analyse, cause_norm, cause_brute
    
    def predire_batch(self, commentaires: list, owners: list = None,
                     topologies: list = None, vendors_list: list = None) -> list:
        """
        Effectue des prédictions sur un batch de commentaires
        
        Args:
            commentaires: Liste de commentaires
            owners: Liste des owners (optionnel)
            topologies: Liste des topologies (optionnel)
            vendors_list: Liste des vendors (optionnel)
            
        Returns:
            Liste de tuples (analyse, cause_normalisee, justification)
        """
        n = len(commentaires)
        
        if owners is None:
            owners = [""] * n
        if topologies is None:
            topologies = [""] * n
        if vendors_list is None:
            vendors_list = [""] * n
        
        resultats = []
        
        for i, (com, own, top, ven) in enumerate(zip(
            commentaires, owners, topologies, vendors_list
        )):
            try:
                analyse, cause_norm, justif = self.predire(com, own, top, ven)
                resultats.append((analyse, cause_norm, justif))
            except Exception as e:
                # En cas d'erreur, retourner une erreur
                analyse = creer_analyse_resume(com, max_len=150)
                resultats.append((analyse, "ERREUR", str(e)[:80]))
            
            if (i + 1) % 10 == 0:
                print(f"   Traité {i+1}/{n} commentaires")
        
        return resultats
    
    def predire_avec_contexte(self, commentaire: str, 
                             contexte: dict = None) -> Tuple[str, str, str]:
        """
        Effectue une prédiction avec un contexte sous forme de dictionnaire
        
        Args:
            commentaire: Commentaire de l'incident
            contexte: Dictionnaire contenant owner, topology, vendors
            
        Returns:
            Tuple (analyse, cause_normalisee, justification)
        """
        if contexte is None:
            contexte = {}
        
        owner = contexte.get("owner", "")
        topology = contexte.get("topology", "")
        vendors = contexte.get("vendors", "")
        
        return self.predire(commentaire, owner, topology, vendors)
    
    def evaluer_confiance(self, justification: str) -> str:
        """
        Évalue la confiance de la prédiction (simple heuristique)
        
        Args:
            justification: Justification de la prédiction
            
        Returns:
            Niveau de confiance ("élevé", "moyen", "faible")
        """
        # Heuristique simple basée sur la présence de "Cause :"
        if "Cause :" in justification or "Cause:" in justification:
            return "élevé"
        elif len(justification) > 20:
            return "moyen"
        else:
            return "faible"
    
    def __repr__(self) -> str:
        """Représentation textuelle"""
        return f"Predictor(model={self.model.__class__.__name__}, device={self.model.device})"
