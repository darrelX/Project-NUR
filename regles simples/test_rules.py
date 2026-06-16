"""
Tests unitaires pour le module rules.py
Démontre la flexibilité du système avec différentes sources de données.
"""

import unittest
import pandas as pd
from pathlib import Path
from rules import (
    process_breakdown_data,
    detect_power_problem,
    is_grid_only_topology,
    determine_sub_rca,
    normalize_text,
    contains_any_keyword,
)


class TestNormalizationFunctions(unittest.TestCase):
    """Tests des fonctions de normalisation de texte"""
    
    def test_normalize_text_basic(self):
        """Test normalisation basique"""
        self.assertEqual(normalize_text("Hello World"), "hello world")
        self.assertEqual(normalize_text("UPPERCASE"), "uppercase")
    
    def test_normalize_text_accents(self):
        """Test suppression des accents"""
        self.assertEqual(normalize_text("café"), "cafe")
        self.assertEqual(normalize_text("été"), "ete")
    
    def test_normalize_text_punctuation(self):
        """Test suppression de la ponctuation"""
        self.assertEqual(normalize_text("hello, world!"), "hello world")
        self.assertEqual(normalize_text("test-case"), "test case")
    
    def test_normalize_text_empty(self):
        """Test avec valeurs vides"""
        self.assertEqual(normalize_text(None), "")
        self.assertEqual(normalize_text(""), "")


class TestKeywordDetection(unittest.TestCase):
    """Tests de détection de mots-clés"""
    
    def test_contains_any_keyword_simple(self):
        """Test détection simple de mots-clés"""
        keywords = ["power", "grid"]
        self.assertTrue(contains_any_keyword("power failure", keywords))
        self.assertTrue(contains_any_keyword("grid outage", keywords))
        self.assertFalse(contains_any_keyword("fiber issue", keywords))
    
    def test_detect_power_problem(self):
        """Test détection de problèmes de power"""
        self.assertTrue(detect_power_problem("Grid outage at site"))
        self.assertTrue(detect_power_problem("ENEO power cut"))
        self.assertTrue(detect_power_problem("Awaiting grid return"))
        self.assertFalse(detect_power_problem("Fiber connection issue"))
        self.assertFalse(detect_power_problem("BSS hardware failure"))


class TestTopologyDetection(unittest.TestCase):
    """Tests de détection de topologie"""
    
    def test_is_grid_only_topology(self):
        """Test identification topologie Grid Only"""
        self.assertTrue(is_grid_only_topology("Grid Only"))
        self.assertTrue(is_grid_only_topology("GridOnly"))
        self.assertTrue(is_grid_only_topology("Good Grid no GE - 8h"))
        self.assertTrue(is_grid_only_topology("Solar Only"))
        self.assertFalse(is_grid_only_topology("Solar Hybrid"))
        self.assertFalse(is_grid_only_topology("GE + Grid"))


class TestSubRCADetermination(unittest.TestCase):
    """Tests de détermination du SUB RCA"""
    
    def test_determine_sub_rca_ihs_grid_only(self):
        """Test IHS avec Grid Only"""
        row = pd.Series({
            "COMMENTAIRE": "Grid outage at site",
            "Owner": "IHS",
            "Topology": "Grid Only"
        })
        result = determine_sub_rca(row)
        self.assertEqual(result, "Coupure ENEO & Baisse de tension")
    
    def test_determine_sub_rca_ihs_hybrid(self):
        """Test IHS avec topologie hybride"""
        row = pd.Series({
            "COMMENTAIRE": "Power failure",
            "Owner": "IHS",
            "Topology": "Solar Hybrid"
        })
        result = determine_sub_rca(row)
        self.assertEqual(result, "Defaut GE & Power Cabinet")
    
    def test_determine_sub_rca_camusat_grid_only(self):
        """Test CAMUSAT avec Grid Only"""
        row = pd.Series({
            "COMMENTAIRE": "ENEO power cut",
            "Owner": "CAMUSAT",
            "Topology": "Grid Only"
        })
        result = determine_sub_rca(row)
        self.assertEqual(result, "AKTIVCO Coupure ENEO & Baisse de tension")
    
    def test_determine_sub_rca_camusat_hybrid(self):
        """Test CAMUSAT avec topologie hybride"""
        row = pd.Series({
            "COMMENTAIRE": "GE failure",
            "Owner": "CAMUSAT",
            "Topology": "GE + Grid"
        })
        result = determine_sub_rca(row)
        self.assertEqual(result, "AKTIVCO Defaut GE & Power Cabinet")
    
    def test_determine_sub_rca_no_power_issue(self):
        """Test sans problème de power"""
        row = pd.Series({
            "COMMENTAIRE": "Fiber connection issue",
            "Owner": "IHS",
            "Topology": "Grid Only"
        })
        result = determine_sub_rca(row)
        self.assertIsNone(result)


class TestProcessBreakdownData(unittest.TestCase):
    """Tests de la fonction principale de traitement"""
    
    def setUp(self):
        """Préparation des données de test"""
        self.sample_data = pd.DataFrame({
            "COMMENTAIRE": [
                "Grid outage at site XYZ",
                "Power cut due to ENEO",
                "BSS hardware issue",
                "Fiber connection problem",
            ],
            "Owner": ["IHS", "CAMUSAT", "OPERATOR", "IHS"],
            "Topology": ["Grid Only", "Grid Only", "Solar Hybrid", "Grid Only"],
            "Complexity": ["Cas Simple", "Cas Simple", "Cas Simple", "Cas Complexe"]
        })
    
    def test_process_breakdown_data_basic(self):
        """Test traitement basique"""
        result = process_breakdown_data(self.sample_data)
        
        # Vérifier que les colonnes sont ajoutées
        self.assertIn("SUB RCA", result.columns)
        self.assertIn("CATEGORY", result.columns)
        self.assertIn("CAUSE", result.columns)
        self.assertIn("OCM_NOMENCLATURE", result.columns)
    
    def test_process_breakdown_data_cas_simples_only(self):
        """Test que seuls les cas simples sont traités"""
        result = process_breakdown_data(self.sample_data)
        
        # Ligne 0 : Cas simple + power issue IHS Grid Only
        self.assertEqual(result.loc[0, "SUB RCA"], "Coupure ENEO & Baisse de tension")
        
        # Ligne 1 : Cas simple + power issue CAMUSAT Grid Only
        self.assertEqual(result.loc[1, "SUB RCA"], "AKTIVCO Coupure ENEO & Baisse de tension")
        
        # Ligne 2 : Cas simple mais pas power issue
        self.assertIsNone(result.loc[2, "SUB RCA"])
        
        # Ligne 3 : Cas complexe (ne devrait pas être traité)
        self.assertIsNone(result.loc[3, "SUB RCA"])
    
    def test_process_breakdown_data_enrichment(self):
        """Test enrichissement des colonnes dérivées"""
        result = process_breakdown_data(self.sample_data)
        
        # Vérifier l'enrichissement pour la première ligne
        self.assertEqual(result.loc[0, "CATEGORY"], "PASSIVE")
        self.assertEqual(result.loc[0, "CAUSE"], "POWER ISSUE")
        self.assertEqual(result.loc[0, "OCM_NOMENCLATURE"], "IHS GRID ONLY")
    
    def test_process_breakdown_data_missing_columns(self):
        """Test avec colonnes manquantes"""
        bad_data = pd.DataFrame({
            "COMMENTAIRE": ["test"],
            # Manque "Owner"
        })
        
        with self.assertRaises(KeyError):
            process_breakdown_data(bad_data)
    
    def test_process_breakdown_data_flexibility(self):
        """Test flexibilité avec différentes variantes de colonnes"""
        # Test avec "complexite" au lieu de "Complexity"
        data_variant = self.sample_data.copy()
        data_variant.rename(columns={"Complexity": "complexite"}, inplace=True)
        
        result = process_breakdown_data(data_variant)
        self.assertIsNotNone(result)
        self.assertIn("SUB RCA", result.columns)


class TestFlexibleDataSources(unittest.TestCase):
    """Tests démontrant la flexibilité des sources de données"""
    
    def test_from_dict(self):
        """Test avec données depuis dictionnaire"""
        data_dict = {
            "COMMENTAIRE": ["Grid outage"],
            "Owner": ["IHS"],
            "Topology": ["Grid Only"],
            "Complexity": ["Cas Simple"]
        }
        
        df = pd.DataFrame(data_dict)
        result = process_breakdown_data(df)
        
        self.assertEqual(result.loc[0, "SUB RCA"], "Coupure ENEO & Baisse de tension")
    
    def test_from_list_of_records(self):
        """Test avec liste d'enregistrements"""
        records = [
            {
                "COMMENTAIRE": "Power failure",
                "Owner": "CAMUSAT",
                "Topology": "Solar Hybrid",
                "Complexity": "Cas Simple"
            },
            {
                "COMMENTAIRE": "ENEO cut",
                "Owner": "ESCO",
                "Topology": "Grid Only",
                "Complexity": "Cas Simple"
            }
        ]
        
        df = pd.DataFrame.from_records(records)
        result = process_breakdown_data(df)
        
        self.assertEqual(len(result), 2)
        self.assertIsNotNone(result.loc[0, "SUB RCA"])
    
    def test_from_api_simulation(self):
        """Test simulant données d'une API"""
        # Simuler réponse JSON d'une API
        api_response = [
            {"COMMENTAIRE": "grid down", "Owner": "IHS", "Topology": "Grid Only", "Complexity": "Cas Simple"},
            {"COMMENTAIRE": "power out", "Owner": "CAMUSAT", "Topology": "Grid Only", "Complexity": "Cas Simple"},
        ]
        
        df = pd.DataFrame(api_response)
        result = process_breakdown_data(df)
        
        # Vérifier que les deux lignes sont traitées
        self.assertEqual(result["SUB RCA"].notna().sum(), 2)
    
    def test_empty_dataframe(self):
        """Test avec DataFrame vide"""
        df = pd.DataFrame(columns=["COMMENTAIRE", "Owner", "Topology", "Complexity"])
        result = process_breakdown_data(df)
        
        self.assertEqual(len(result), 0)
        self.assertIn("SUB RCA", result.columns)


class TestEdgeCases(unittest.TestCase):
    """Tests des cas limites"""
    
    def test_null_values(self):
        """Test avec valeurs nulles"""
        data = pd.DataFrame({
            "COMMENTAIRE": [None, "power failure"],
            "Owner": ["IHS", None],
            "Topology": ["Grid Only", "Grid Only"],
            "Complexity": ["Cas Simple", "Cas Simple"]
        })
        
        result = process_breakdown_data(data)
        # Le code devrait gérer les valeurs nulles sans crasher
        self.assertIsNotNone(result)
    
    def test_mixed_case_topology(self):
        """Test avec topologies en différentes casses"""
        data = pd.DataFrame({
            "COMMENTAIRE": ["grid outage", "power cut"],
            "Owner": ["IHS", "IHS"],
            "Topology": ["GRID ONLY", "grid only"],
            "Complexity": ["Cas Simple", "Cas Simple"]
        })
        
        result = process_breakdown_data(data)
        # Les deux devraient être détectés comme Grid Only
        self.assertEqual(result.loc[0, "SUB RCA"], "Coupure ENEO & Baisse de tension")
        self.assertEqual(result.loc[1, "SUB RCA"], "Coupure ENEO & Baisse de tension")


def run_tests():
    """Exécute tous les tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    print("=" * 70)
    print("TESTS UNITAIRES - MODULE RULES")
    print("Démonstration de la flexibilité du système")
    print("=" * 70)
    print()
    
    run_tests()
