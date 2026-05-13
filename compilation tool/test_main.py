import pandas as pd
from celldown import CellDown   # import de la classe (pas du module)
from super_xlookup import SuperXlookup   # import de la classe (pas du module)

if __name__ == "__main__":
        # Exemple fourni par l'utilisateur (chemins à adapter)
    xl = SuperXlookup(
        source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx", 
        target_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\OCM RAN INCIDENT FOLOW-UP 28-04-2026 19H UTC.xlsx",
        source_key_column="B",           # Codesite en B
        target_key_column="D",           # colonne clé cible
        target_value_column="J",         # valeur à rapporter (colonne J)
        result_position_column="C",      # position en colonne C
        result_column_name="Commentaire",# nom personnalisé
        source_sheet_name="Sheet1",
        target_sheet_name="ALL SITES DOWN"
    )

    print("=" * 60)
    print("TEST XLOOKUP (position fixe C)")
    print("=" * 60)
    xl.run()

    # Test avec "last_free"
    print("\n" + "=" * 60)
    print("TEST XLOOKUP (dernière colonne libre)")
    print("=" * 60)
    xl2 = SuperXlookup(
        source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx", 
        target_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\OCM RAN INCIDENT FOLOW-UP 28-04-2026 19H UTC.xlsx",
        source_key_column="B",
        target_key_column="D",
        target_value_column="J",
        result_position_column="last_free",
        result_column_name="Résultat auto",
        source_sheet_name="Sheet1",
        target_sheet_name="ALL SITES DOWN"
    )
    xl2.run()

    # Affichage du résultat final
    df = pd.read_excel(r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx")
    print("\n📄 Aperçu du fichier source après exécution :")
    print(df.head(30))
    
    # Création d'une instance de CellDown
    # Attention : utilisez un nom de variable différent pour éviter de masquer la classe
    mon_celldown = CellDown(
        source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx",
        target_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\W18_CELLS_DOWN_NOKIA_2704 AU 29042026 16h30.xlsx",
        colown_key_path_source="B",
        target_key_column="B",
        target_value_column="T",
        result_position_column="C",
        source_sheet_path="Sheet1",
        date_str="29042026",
        start_column="C"
    )
    
    print("=" * 60)
    print("TEST SUPER_XLOOKUP_PAR_DATE")
    print("=" * 60)
    
    mon_celldown.super_xlookup_par_date()
    
    df = pd.read_excel("inputs/Book1.xlsx")
    print("\nAperçu du fichier résultat:")
    print(df.head(30))