"""Tests pour les fonctions de la classe CellDown."""
import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celldown.main import CellDown


def test_get_excel_file():
    """Test de la méthode _get_excel_file."""
    print("=" * 50)
    print("TEST: _get_excel_file")
    print("=" * 50)
    
    # Test avec un fichier existant
    celldown = CellDown(
        source_file_path="inputs/Book1.xlsx",
        target_file_path="inputs/Book1_resultat.xlsx",
        colown_key_path_source="A",
        target_value_column="B",
        result_position_column="C"
    )
    
    excel_file = celldown._get_excel_file()
    if excel_file is not None:
        print(f"✓ Fichier ouvert avec succès")
        print(f"  Feuilles trouvées: {excel_file.sheet_names}")
    else:
        print("✗ Échec de l'ouverture du fichier")
    
    # Test avec un fichier inexistant
    print("\nTest avec fichier inexistant:")
    celldown_bad = CellDown(
        source_file_path="inputs/fichier_inexistant.xlsx",
        target_file_path="inputs/Book1_resultat.xlsx",
        colown_key_path_source="A",
        target_value_column="B",
        result_position_column="C"
    )
    
    excel_file_bad = celldown_bad._get_excel_file()
    if excel_file_bad is None:
        print("✓ Retourne None correctement pour fichier inexistant")
    else:
        print("✗ Devrait retourner None")


def test_afficher_feuilles():
    """Test de la méthode afficher_feuilles."""
    print("\n" + "=" * 50)
    print("TEST: afficher_feuilles")
    print("=" * 50)
    
    celldown = CellDown(
        source_file_path="inputs/Book1.xlsx",
        target_file_path="inputs/Book1_resultat.xlsx",
        colown_key_path_source="A",
        target_value_column="B",
        result_position_column="C"
    )
    
    print("\nAffichage avec 3 lignes d'aperçu:")
    celldown.afficher_feuilles(nb_lignes_apercu=3)


def test_filtrer_par_date():
    """Test de la méthode filtrer_par_date."""
    print("\n" + "=" * 50)
    print("TEST: filtrer_par_date")
    print("=" * 50)
    
    # Utiliser le fichier avec une date dans le nom des feuilles
    celldown = CellDown(
        source_file_path="inputs/DAILY_W13_CELLS_DOWN_HUAWEI_27032026 17h.xlsx",
        target_file_path="inputs/Book1_resultat.xlsx",
        colown_key_path_source="A",
        target_value_column="B",
        result_position_column="C"
    )
    
    # Test avec une date valide
    print("\nRecherche de feuilles avec date '27032026':")
    result = celldown.filtrer_par_date("27032026")
    print(f"  Résultat: {result}")
    
    # Test avec une date invalide (format)
    print("\nTest avec format de date invalide:")
    result_bad = celldown.filtrer_par_date("2703")
    print(f"  Résultat: {result_bad}")
    
    # Test avec une date qui n'existe pas
    print("\nRecherche de feuilles avec date '01012000':")
    result_none = celldown.filtrer_par_date("01012000")
    print(f"  Résultat: {result_none}")


if __name__ == "__main__":
    test_get_excel_file()
    test_afficher_feuilles()
    test_filtrer_par_date()
    print("\n" + "=" * 50)
    print("TESTS TERMINÉS")
    print("=" * 50)
