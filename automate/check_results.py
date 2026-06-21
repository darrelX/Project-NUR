import pandas as pd

# Lire le fichier résultat
df = pd.read_excel(r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx")

# Filtrer les lignes qui ont des commentaires dans "TOP 1906"
if 'TOP 1906' in df.columns:
    lignes_avec_commentaires = df[df['TOP 1906'].notna() & (df['TOP 1906'] != '')]
    
    print(f"✅ Nombre de lignes avec commentaires : {len(lignes_avec_commentaires)}")
    print(f"\n📋 Aperçu des lignes avec commentaires :\n")
    print(lignes_avec_commentaires[['Nom du Physique', 'Codesite', 'TOP 1906']].head(20))
else:
    print("❌ La colonne 'TOP 1906' n'existe pas")

print(f"\n📊 Colonnes disponibles : {list(df.columns)}")
