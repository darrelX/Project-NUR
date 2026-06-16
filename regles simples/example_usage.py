"""
Exemples d'utilisation du module rules.py avec différentes configurations.
"""

from pathlib import Path
import pandas as pd
from rules import process_breakdown_data, load_data_from_config, save_data, main


# =========================
# EXEMPLE 1: Utilisation avec configuration Excel par défaut
# =========================
def example_default_config():
    """Utilise la configuration par défaut définie dans rules.py"""
    print("=== Exemple 1: Configuration par défaut ===")
    main()
    print()


# =========================
# EXEMPLE 2: Configuration personnalisée depuis Excel
# =========================
def example_custom_excel():
    """Charge depuis un fichier Excel différent"""
    print("=== Exemple 2: Configuration Excel personnalisée ===")
    
    config = {
        "source_type": "excel",
        "input_file": Path("inputs/CUSTOM_BREAKDOWN.xlsx"),
        "output_file": Path("outputs/CUSTOM_OUTPUT.xlsx"),
        "sheet_name": "Sheet1",
    }
    
    try:
        main(config)
    except FileNotFoundError:
        print("Fichier non trouvé (exemple)")
    print()


# =========================
# EXEMPLE 3: Configuration CSV
# =========================
def example_csv_config():
    """Charge depuis un fichier CSV"""
    print("=== Exemple 3: Configuration CSV ===")
    
    config = {
        "source_type": "csv",
        "input_file": Path("inputs/breakdown.csv"),
        "output_file": Path("outputs/breakdown_output.csv"),
        "csv_encoding": "utf-8",
        "csv_separator": ",",
    }
    
    try:
        main(config)
    except FileNotFoundError:
        print("Fichier CSV non trouvé (exemple)")
    print()


# =========================
# EXEMPLE 4: Utilisation directe avec DataFrame
# =========================
def example_direct_dataframe():
    """Utilisation directe de la fonction de traitement avec un DataFrame"""
    print("=== Exemple 4: Utilisation directe avec DataFrame ===")
    
    # Créer un DataFrame exemple
    data = {
        "COMMENTAIRE": [
            "Grid outage at site",
            "Power cut due to ENEO failure",
            "BSS hardware issue"
        ],
        "Owner": ["IHS", "CAMUSAT", "OPERATOR"],
        "Topology": ["Grid Only", "Solar Hybrid", "Grid Only"],
        "Complexity": ["Cas Simple", "Cas Simple", "Cas Complexe"]
    }
    
    df = pd.DataFrame(data)
    
    # Traitement direct
    df_enriched = process_breakdown_data(df)
    
    print("Données enrichies:")
    print(df_enriched[["COMMENTAIRE", "Owner", "SUB RCA", "CATEGORY", "CAUSE"]])
    print()


# =========================
# EXEMPLE 5: Pipeline personnalisé
# =========================
def example_custom_pipeline():
    """Pipeline personnalisé avec pré-traitement et post-traitement"""
    print("=== Exemple 5: Pipeline personnalisé ===")
    
    try:
        # 1. Chargement
        config = {
            "source_type": "excel",
            "input_file": Path("inputs/APRIL BREAKDOWN.xlsx"),
            "sheet_name": "BREAKDOWN",
        }
        df = load_data_from_config(config)
        
        # 2. Pré-traitement personnalisé (optionnel)
        print(f"Nombre de lignes avant traitement: {len(df)}")
        
        # 3. Traitement principal
        df_enriched = process_breakdown_data(df)
        
        # 4. Post-traitement personnalisé (optionnel)
        # Par exemple, filtrer uniquement les cas simples traités
        df_filtered = df_enriched[df_enriched["SUB RCA"].notna()]
        print(f"Nombre de lignes enrichies: {len(df_filtered)}")
        
        # 5. Sauvegarde
        output_path = Path("outputs/PIPELINE_OUTPUT.xlsx")
        save_data(df_enriched, output_path)
        print(f"Fichier sauvegardé: {output_path}")
        
    except Exception as e:
        print(f"Erreur: {e}")
    print()


# =========================
# EXEMPLE 6: Traitement par lots
# =========================
def example_batch_processing():
    """Traiter plusieurs fichiers en lot"""
    print("=== Exemple 6: Traitement par lots ===")
    
    files_to_process = [
        {
            "source_type": "excel",
            "input_file": Path("inputs/APRIL BREAKDOWN.xlsx"),
            "output_file": Path("outputs/APRIL_OUTPUT.xlsx"),
            "sheet_name": "BREAKDOWN",
        },
        # Ajoutez d'autres fichiers ici
    ]
    
    for i, config in enumerate(files_to_process, 1):
        print(f"Traitement du fichier {i}/{len(files_to_process)}: {config['input_file']}")
        try:
            main(config)
        except Exception as e:
            print(f"  Erreur: {e}")
    print()


# =========================
# EXEMPLE 7: Utilisation programmatique pour intégration
# =========================
def example_api_integration():
    """
    Exemple d'intégration dans une API ou application.
    La fonction peut recevoir des données de n'importe quelle source.
    """
    print("=== Exemple 7: Intégration API ===")
    
    # Simuler des données reçues d'une API
    api_data = {
        "COMMENTAIRE": ["Power failure", "Grid down"],
        "Owner": ["IHS", "CAMUSAT"],
        "Topology": ["Grid Only", "Grid Only"],
        "Complexity": ["Cas Simple", "Cas Simple"]
    }
    
    # Créer DataFrame
    df = pd.DataFrame(api_data)
    
    # Traiter
    df_result = process_breakdown_data(df)
    
    # Retourner au format JSON pour API
    result_json = df_result.to_dict(orient='records')
    print(f"Résultat pour API: {len(result_json)} enregistrements traités")
    print()


if __name__ == "__main__":
    print("DÉMONSTRATION DES DIFFÉRENTES CONFIGURATIONS\n")
    print("=" * 60)
    
    # Exécuter tous les exemples
    example_default_config()
    example_custom_excel()
    example_csv_config()
    example_direct_dataframe()
    example_custom_pipeline()
    example_batch_processing()
    example_api_integration()
    
    print("=" * 60)
    print("Démonstration terminée!")
