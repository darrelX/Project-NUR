import pandas as pd

# Charger le fichier cible
target_file = r"C:\Users\f50056342\Desktop\emails_export\Hourly IHS.xlsx"
df = pd.read_excel(target_file, sheet_name="ALL", engine='openpyxl')

print("📋 Colonnes disponibles dans le fichier CIBLE (Hourly IHS.xlsx) :")
print("=" * 60)
for i, col in enumerate(df.columns, 1):
    print(f"{i:2}. {col}")

print(f"\n📊 Nombre total de colonnes : {len(df.columns)}")
print(f"📊 Nombre de lignes : {len(df)}")

# Afficher quelques lignes pour mieux comprendre
print("\n📄 Aperçu des 5 premières lignes :")
print(df.head())

# Afficher spécifiquement "IHS Site Name" pour voir si elle contient les codes
print("\n🔍 Contenu de 'IHS Site Name' (10 premières valeurs) :")
print("=" * 60)
for i, val in enumerate(df['IHS Site Name'].head(10), 1):
    print(f"{i:2}. {val}")

# Vérifier aussi "Tenant Site ID"
print("\n🔍 Contenu de 'Tenant Site ID' (10 premières valeurs) :")
print("=" * 60)
for i, val in enumerate(df['Tenant Site ID'].head(10), 1):
    print(f"{i:2}. {val}")

# Chercher des codes CTR_, LIT_, etc. dans IHS Site Name
print("\n🔍 Recherche de codes (CTR_, LIT_, etc.) dans 'IHS Site Name' :")
import re
pattern = re.compile(r'(CTR_\d+|LIT_\d+|EST_\d+|OST_\d+|SUO_\d+|SUD_\d+|NOR_\d+|ADM_\d+|OUE_\d+)')
for i, val in enumerate(df['IHS Site Name'].head(20), 1):
    matches = pattern.findall(str(val))
    if matches:
        print(f"{i:2}. {val} -> CODES TROUVÉS: {matches}")
