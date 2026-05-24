"""
Gestionnaire d'évaluation pour le modèle fine-tuné
"""

import pandas as pd
import time
from typing import Dict, Any, List, Tuple
from collections import Counter, defaultdict
from ..utils.helpers import propre, est_impacte, extraire_site_impactant
from ..utils.constants import CATEGORIES


class Evaluator:
    """
    Classe pour évaluer les performances du modèle
    """
    
    def __init__(self, predictor):
        """
        Initialise l'évaluateur
        
        Args:
            predictor: Instance de Predictor pour faire les prédictions
        """
        self.predictor = predictor
        self.resultats = []
        
    def evaluer_fichier_test(self, chemin_test: str, 
                            col_commentaire: str = "Verifications",
                            col_codesite: str = "Codesite",
                            col_owner: str = None,
                            col_topology: str = None,
                            col_vendors: str = None) -> pd.DataFrame:
        """
        Évalue le modèle sur un fichier de test
        
        Args:
            chemin_test: Chemin vers le fichier Excel de test
            col_commentaire: Nom de la colonne contenant les commentaires
            col_codesite: Nom de la colonne contenant les codes sites
            col_owner: Nom de la colonne owner (optionnel)
            col_topology: Nom de la colonne topology (optionnel)
            col_vendors: Nom de la colonne vendors (optionnel)
            
        Returns:
            DataFrame avec les résultats
        """
        print(f"\n📂 Chargement du fichier de test : {chemin_test}")
        df = pd.read_excel(chemin_test, dtype=str)
        
        print(f"   Lignes totales : {len(df)}")
        
        # Initialiser les colonnes de résultats
        df["TYPE_CAS"] = ""
        df["ANALYSE"] = ""
        df["JUSTIFICATION"] = ""
        df["CAUSE_PREDITE"] = ""
        df["SITE_IMPACTANT"] = ""
        df["TEMPS_S"] = 0.0
        
        # Classifier les lignes
        idx_no_root = []
        idx_impactes = []
        idx_normaux = []
        dict_causes_par_site = {}
        
        print("\n🔍 Classification des lignes...")
        
        for idx, row in df.iterrows():
            com = propre(str(row.get(col_commentaire, "")))
            
            if not com:
                df.at[idx, "TYPE_CAS"] = "NO_ROOT_CAUSE"
                df.at[idx, "CAUSE_PREDITE"] = "no root cause"
                df.at[idx, "ANALYSE"] = "Aucun commentaire disponible"
                df.at[idx, "JUSTIFICATION"] = "Pas d'information sur l'incident"
                idx_no_root.append(idx)
            elif est_impacte(com):
                df.at[idx, "TYPE_CAS"] = "IMPACTE"
                idx_impactes.append(idx)
            else:
                df.at[idx, "TYPE_CAS"] = "NORMAL"
                idx_normaux.append(idx)
        
        print(f"   No root cause : {len(idx_no_root)}")
        print(f"   Cas normaux   : {len(idx_normaux)}")
        print(f"   Cas impactés  : {len(idx_impactes)}")
        
        # Traiter les cas normaux
        print(f"\n🤖 Traitement des cas normaux...")
        t_debut = time.time()
        
        for i, idx in enumerate(idx_normaux):
            row = df.loc[idx]
            com = propre(str(row.get(col_commentaire, "")))
            own = propre(str(row.get(col_owner, ""))) if col_owner else ""
            top = propre(str(row.get(col_topology, ""))) if col_topology else ""
            ven = propre(str(row.get(col_vendors, ""))) if col_vendors else ""
            
            t0 = time.time()
            try:
                analyse, cause_norm, justif = self.predictor.predire(
                    com, own, top, ven
                )
            except Exception as e:
                cause_norm = "ERREUR"
                justif = str(e)[:80]
                analyse = com[:150]
            
            df.at[idx, "CAUSE_PREDITE"] = cause_norm
            df.at[idx, "ANALYSE"] = analyse
            df.at[idx, "JUSTIFICATION"] = justif
            df.at[idx, "TEMPS_S"] = round(time.time() - t0, 2)
            
            # Enregistrer pour résolution des cas impactés
            codesite = propre(str(row.get(col_codesite, ""))).upper()
            if codesite and cause_norm not in ["ERREUR", ""]:
                dict_causes_par_site[codesite] = {
                    "cause": cause_norm,
                    "justification": justif,
                    "analyse": analyse,
                }
            
            if (i + 1) % 50 == 0:
                elapsed = time.time() - t_debut
                vitesse = (i + 1) / elapsed if elapsed > 0 else 0
                restant = (len(idx_normaux) - i - 1) / vitesse if vitesse > 0 else 0
                print(f"   {i+1}/{len(idx_normaux)} | {vitesse:.2f} ligne/s | ETA {restant/60:.1f} min")
        
        print(f"   ✅ {len(idx_normaux)} cas normaux traités")
        
        # Traiter les cas impactés
        print(f"\n🔗 Traitement des cas impactés...")
        resolus = 0
        non_resolus = 0
        
        for idx in idx_impactes:
            row = df.loc[idx]
            com = propre(str(row.get(col_commentaire, "")))
            
            code_impactant = extraire_site_impactant(com)
            df.at[idx, "SITE_IMPACTANT"] = code_impactant or "non trouvé"
            
            if code_impactant and code_impactant.upper() in dict_causes_par_site:
                info = dict_causes_par_site[code_impactant.upper()]
                df.at[idx, "CAUSE_PREDITE"] = info["cause"]
                df.at[idx, "ANALYSE"] = (
                    f"Site impacté par {code_impactant}. "
                    f"Cause héritée du site impactant."
                )
                df.at[idx, "JUSTIFICATION"] = (
                    f"Ce site est impacté par {code_impactant} "
                    f"dont la cause est : {info['cause']}"
                )
                resolus += 1
            else:
                df.at[idx, "CAUSE_PREDITE"] = "SITE_IMPACTANT_NON_RESOLU"
                df.at[idx, "ANALYSE"] = (
                    f"Site impacté détecté. Site impactant : {code_impactant or 'non trouvé'}."
                )
                df.at[idx, "JUSTIFICATION"] = (
                    f"Site impactant ({code_impactant or 'inconnu'}) absent du fichier."
                )
                non_resolus += 1
        
        print(f"   ✅ Résolus     : {resolus}")
        print(f"   ⚠️  Non résolus : {non_resolus}")
        
        return df
    
    def evaluer_avec_validation(self, df_test: pd.DataFrame, 
                                chemin_valid: str,
                                col_cause: str = "CAUSE",
                                col_codesite: str = "Codesite") -> Dict[str, Any]:
        """
        Évalue les performances avec un fichier de validation
        
        Args:
            df_test: DataFrame des résultats de test
            chemin_valid: Chemin vers le fichier de validation
            col_cause: Nom de la colonne contenant les causes réelles
            col_codesite: Nom de la colonne contenant les codes sites
            
        Returns:
            Dictionnaire avec les métriques de performance
        """
        print(f"\n📊 Évaluation avec fichier de validation : {chemin_valid}")
        
        df_valid = pd.read_excel(chemin_valid, dtype=str)
        print(f"   Lignes validation : {len(df_valid)}")
        
        # Normaliser les codes sites
        df_valid[col_codesite] = df_valid[col_codesite].str.strip().str.upper()
        df_test["Codesite_upper"] = df_test["Codesite"].str.strip().str.upper()
        
        # Fusion
        df_merge = df_valid.merge(
            df_test[["Codesite_upper", "CAUSE_PREDITE", "ANALYSE", 
                    "JUSTIFICATION", "TYPE_CAS"]].rename(
                columns={"Codesite_upper": col_codesite}
            ),
            on=col_codesite,
            how="left"
        )
        
        df_merge[col_cause] = df_merge[col_cause].fillna("").str.strip()
        df_merge["CAUSE_PREDITE"] = df_merge["CAUSE_PREDITE"].fillna("").str.strip()
        
        # Filtrer sur les catégories entraînées
        cat_lower = [c.lower() for c in CATEGORIES]
        df_eval = df_merge[
            df_merge[col_cause].str.lower().isin(cat_lower)
        ].copy()
        
        print(f"   Lignes évaluables : {len(df_eval)}")
        
        # Calculer les métriques
        df_eval["CORRECT"] = (
            df_eval["CAUSE_PREDITE"].str.lower() == df_eval[col_cause].str.lower()
        )
        
        total = len(df_eval)
        correct = int(df_eval["CORRECT"].sum())
        acc = correct / total * 100 if total > 0 else 0
        
        print(f"\n   Total évalué : {total}")
        print(f"   ✓ Corrects   : {correct} ({acc:.1f}%)")
        print(f"   ✗ Incorrects : {total - correct} ({100-acc:.1f}%)")
        
        # Métriques par catégorie
        erreurs_par_cat = self._calculer_metriques_par_categorie(
            df_eval, col_cause
        )
        
        return {
            "total": total,
            "correct": correct,
            "accuracy": acc,
            "df_eval": df_eval,
            "erreurs_par_cat": erreurs_par_cat
        }
    
    def _calculer_metriques_par_categorie(self, df_eval: pd.DataFrame, 
                                          col_cause: str) -> Dict:
        """
        Calcule les métriques par catégorie
        
        Args:
            df_eval: DataFrame évalué
            col_cause: Nom de la colonne contenant les causes
            
        Returns:
            Dictionnaire des métriques par catégorie
        """
        erreurs_par_cat = defaultdict(
            lambda: {"correct": 0, "total": 0, "erreurs": []}
        )
        
        for _, row in df_eval.iterrows():
            cat = row[col_cause]
            erreurs_par_cat[cat]["total"] += 1
            if row["CORRECT"]:
                erreurs_par_cat[cat]["correct"] += 1
            else:
                erreurs_par_cat[cat]["erreurs"].append(row["CAUSE_PREDITE"])
        
        return dict(erreurs_par_cat)
    
    def generer_rapport_excel(self, df_eval: pd.DataFrame, 
                              erreurs_par_cat: Dict,
                              chemin_sortie: str,
                              metriques_globales: Dict):
        """
        Génère un rapport Excel détaillé
        
        Args:
            df_eval: DataFrame évalué
            erreurs_par_cat: Métriques par catégorie
            chemin_sortie: Chemin du fichier Excel de sortie
            metriques_globales: Métriques globales
        """
        print(f"\n💾 Génération du rapport : {chemin_sortie}")
        
        with pd.ExcelWriter(chemin_sortie, engine='openpyxl') as writer:
            # Feuille 1 : Résumé global
            self._creer_feuille_resume_global(
                writer, metriques_globales, erreurs_par_cat
            )
            
            # Feuille 2 : Par catégorie
            self._creer_feuille_par_categorie(writer, erreurs_par_cat)
            
            # Feuille 3 : Détails
            df_eval[["Codesite", "CAUSE", "CAUSE_PREDITE", "CORRECT", 
                    "ANALYSE", "JUSTIFICATION"]].to_excel(
                writer, sheet_name="Détails", index=False
            )
        
        print(f"   ✅ Rapport sauvegardé : {chemin_sortie}")
    
    def _creer_feuille_resume_global(self, writer, metriques, erreurs_par_cat):
        """Crée la feuille de résumé global"""
        data = {
            "Indicateur": [
                "Total évalué",
                "✓ Corrects",
                "✗ Incorrects",
                "Accuracy (%)",
                "Catégories ≥80%",
                "Catégories 50-79%",
                "Catégories <50%",
            ],
            "Valeur": [
                metriques["total"],
                metriques["correct"],
                metriques["total"] - metriques["correct"],
                f"{metriques['accuracy']:.1f}%",
                sum(1 for s in erreurs_par_cat.values()
                    if s["total"] > 0 and s["correct"]/s["total"] >= 0.8),
                sum(1 for s in erreurs_par_cat.values()
                    if s["total"] > 0 and 0.5 <= s["correct"]/s["total"] < 0.8),
                sum(1 for s in erreurs_par_cat.values()
                    if s["total"] > 0 and s["correct"]/s["total"] < 0.5),
            ]
        }
        pd.DataFrame(data).to_excel(
            writer, sheet_name="Résumé global", index=False
        )
    
    def _creer_feuille_par_categorie(self, writer, erreurs_par_cat):
        """Crée la feuille par catégorie"""
        resume = []
        for cat in sorted(erreurs_par_cat.keys()):
            s = erreurs_par_cat[cat]
            a = s["correct"] / s["total"] * 100 if s["total"] > 0 else 0
            top = Counter(s["erreurs"]).most_common(1)
            resume.append({
                "Catégorie": cat,
                "✓ Corrects": s["correct"],
                "Total": s["total"],
                "✗ Incorrects": s["total"] - s["correct"],
                "Accuracy (%)": round(a, 1),
                "Statut": "✅" if a >= 80 else ("⚠️" if a >= 50 else "❌"),
                "Erreur principale": top[0][0] if top else "—",
                "Nb erreur princ.": top[0][1] if top else 0,
            })
        pd.DataFrame(resume).to_excel(
            writer, sheet_name="Par catégorie", index=False
        )
    
    def __repr__(self) -> str:
        """Représentation textuelle"""
        return f"Evaluator(predictor={self.predictor})"
