"""
Démonstration de la fonction create_dataframe_from_comments
Cette fonction permet de créer rapidement un DataFrame à partir d'une liste de commentaires.
"""

from rules import create_dataframe_from_comments, process_breakdown_data


def demo_basic_usage():
    """Utilisation basique avec valeurs par défaut"""
    print("=" * 70)
    print("EXEMPLE 1 : Utilisation basique avec valeurs par défaut")
    print("=" * 70)
    
    comments = [
        "Grid outage at site ABC",
        "Power cut due to ENEO",
        "Coupure grid",
    ]
    
    # Création du DataFrame avec valeurs par défaut
    # Owner = "IHS", Topology = "Grid Only", Complexity = "Cas Simple"
    df = create_dataframe_from_comments(comments)
    
    print("\nDataFrame créé:")
    print(df.to_string())
    
    # Traitement avec la logique métier
    result = process_breakdown_data(df)
    
    print("\nRésultat après traitement:")
    print(result[['COMMENTAIRE', 'Owner', 'SUB RCA', 'CATEGORY', 'CAUSE']].to_string())
    print()


def demo_with_different_owners():
    """Utilisation avec différents owners"""
    print("=" * 70)
    print("EXEMPLE 2 : Avec différents owners")
    print("=" * 70)
    
    comments = [
        "Power failure at site",
        "GE not working",
        "Grid down",
    ]
    
    owners = ["IHS", "CAMUSAT", "ESCO"]
    
    df = create_dataframe_from_comments(comments, owners=owners)
    
    print("\nDataFrame créé:")
    print(df.to_string())
    
    result = process_breakdown_data(df)
    
    print("\nRésultat après traitement:")
    print(result[['COMMENTAIRE', 'Owner', 'SUB RCA', 'OCM_NOMENCLATURE']].to_string())
    print()


def demo_with_different_topologies():
    """Utilisation avec différentes topologies"""
    print("=" * 70)
    print("EXEMPLE 3 : Avec différentes topologies")
    print("=" * 70)
    
    comments = [
        "ENEO power cut",
        "GE battery failure",
        "Grid outage",
    ]
    
    owners = ["IHS", "IHS", "CAMUSAT"]
    topologies = ["Grid Only", "Solar Hybrid", "Grid Only"]
    
    df = create_dataframe_from_comments(comments, owners=owners, topologies=topologies)
    
    print("\nDataFrame créé:")
    print(df.to_string())
    
    result = process_breakdown_data(df)
    
    print("\nRésultat après traitement:")
    print(result[['COMMENTAIRE', 'Owner', 'Topology', 'SUB RCA']].to_string())
    print()


def demo_with_single_values():
    """Utilisation avec une valeur unique pour tous"""
    print("=" * 70)
    print("EXEMPLE 4 : Avec une valeur unique pour tous les commentaires")
    print("=" * 70)
    
    comments = [
        "Power cabinet issue",
        "GE failure detected",
        "Battery not charging",
    ]
    
    # Même owner et topology pour tous
    df = create_dataframe_from_comments(
        comments,
        owners="CAMUSAT",
        topologies="Solar Hybrid"
    )
    
    print("\nDataFrame créé:")
    print(df.to_string())
    
    result = process_breakdown_data(df)
    
    print("\nRésultat après traitement:")
    print(result[['COMMENTAIRE', 'SUB RCA', 'CATEGORY', 'CAUSE']].to_string())
    print()


def demo_api_simulation():
    """Simulation d'intégration avec une API"""
    print("=" * 70)
    print("EXEMPLE 5 : Simulation d'intégration API")
    print("=" * 70)
    
    # Simuler des données reçues d'une API
    api_response = {
        "incidents": [
            {"description": "Grid failure at BTS001", "site_owner": "IHS"},
            {"description": "Power outage ENEO", "site_owner": "CAMUSAT"},
            {"description": "GE not functioning", "site_owner": "ESCO"},
        ]
    }
    
    # Extraire les données
    comments = [incident["description"] for incident in api_response["incidents"]]
    owners = [incident["site_owner"] for incident in api_response["incidents"]]
    
    # Créer le DataFrame
    df = create_dataframe_from_comments(comments, owners=owners)
    
    print("\nDonnées reçues de l'API:")
    print(df.to_string())
    
    # Traiter
    result = process_breakdown_data(df)
    
    print("\nRésultat enrichi pour renvoyer à l'API:")
    print(result[['COMMENTAIRE', 'Owner', 'SUB RCA', 'CATEGORY', 'CAUSE']].to_string())
    
    # Convertir en JSON pour API
    json_result = result[['COMMENTAIRE', 'Owner', 'SUB RCA', 'CATEGORY']].to_dict(orient='records')
    print(f"\nFormat JSON : {len(json_result)} enregistrements prêts")
    print()


def demo_batch_processing():
    """Traitement par lots de plusieurs listes"""
    print("=" * 70)
    print("EXEMPLE 6 : Traitement par lots")
    print("=" * 70)
    
    # Plusieurs lots de commentaires à traiter
    batches = [
        {
            "name": "Batch IHS Sites",
            "comments": ["Grid outage site A", "Power cut site B"],
            "owner": "IHS",
        },
        {
            "name": "Batch CAMUSAT Sites",
            "comments": ["GE failure site C", "ENEO cut site D"],
            "owner": "CAMUSAT",
        },
    ]
    
    all_results = []
    
    for batch in batches:
        print(f"\nTraitement : {batch['name']}")
        df = create_dataframe_from_comments(
            batch["comments"],
            owners=batch["owner"]
        )
        result = process_breakdown_data(df)
        all_results.append(result)
        print(result[['COMMENTAIRE', 'SUB RCA', 'CATEGORY']].to_string())
    
    print(f"\n{len(all_results)} lots traités avec succès!")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "DÉMONSTRATION - create_dataframe_from_comments" + " " * 11 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Exécuter toutes les démos
    demo_basic_usage()
    demo_with_different_owners()
    demo_with_different_topologies()
    demo_with_single_values()
    demo_api_simulation()
    demo_batch_processing()
    
    print("=" * 70)
    print("FIN DES DÉMONSTRATIONS")
    print("=" * 70)
    print()
    print("💡 Utilisez cette fonction pour créer rapidement des DataFrames")
    print("   à partir de listes de commentaires, peu importe leur provenance:")
    print("   - APIs REST")
    print("   - Bases de données")
    print("   - Fichiers texte")
    print("   - Flux de données")
    print("   - Tests unitaires")
