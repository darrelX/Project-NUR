import pandas as pd

target_file = r"C:\Users\f50056342\Desktop\my work\cellsdow files\Dashbord suivi TOP OFFENDERS 19-06-2026.xlsx"

# Lire les feuilles
excel_file = pd.ExcelFile(target_file, engine='openpyxl')

for sheet_name in ['TOP 1906', 'Break 1906']:
    print(f"\n{'='*60}")
    print(f"Feuille : {sheet_name}")
    print(f"{'='*60}")
    
    try:
        df = pd.read_excel(target_file, sheet_name=sheet_name, engine='openpyxl')
        print(f"\nNombre de colonnes : {len(df.columns)}")
        print(f"\nListe des colonnes :")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\nPremières lignes :")
        print(df.head(3))
    except Exception as e:
        print(f"Erreur : {e}")
