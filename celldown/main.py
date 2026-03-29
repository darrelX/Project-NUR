import os
import pandas as pd
from datetime import datetime


class CellDown:
    def __init__(self, cell, chemin_fichier):
        self.cell = cell
        self.chemin_fichier = chemin_fichier

    def run(self):
        # Implement the logic to handle the cell down event
        print(f"Cell {self.cell} is down.")
        
    def afficher_feuilles(self):
        """
        Affiche les feuilles du fichier Excel et un aperçu de chaque feuille.
        """
        if not os.path.exists(self.chemin_fichier):
            print(f"Fichier introuvable: {self.chemin_fichier}")
            return
        try:
            excel_file = pd.ExcelFile(self.chemin_fichier)
            print(f"Feuilles disponibles dans '{self.chemin_fichier}':")
            for i, feuille in enumerate(excel_file.sheet_names, 1):
                print(f"{i}. {feuille}")
            print("\nAperçu de chaque feuille:")
            for feuille in excel_file.sheet_names:
                print(f"\n=== {feuille} ===")
                df = pd.read_excel(self.chemin_fichier, sheet_name=feuille)
                print(df.head())
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {e}")

    def filtrer_par_date(self, date_str):
        """
        Filtre les feuilles correspondant à une date donnée (format ddmmyyyy).
        Args:
            date_str (str): Date recherchée au format ddmmyyyy
        Returns:
            list: Liste des noms de feuilles correspondant à la date
        """
        try:
            excel_file = pd.ExcelFile(self.chemin_fichier)
            # Normaliser la date recherchée au format ddmmyyyy
            try:
                date_obj = datetime.strptime(date_str, "%d%m%Y")
                date_pattern = date_obj.strftime("%d%m%Y")
            except ValueError:
                print("Format de date invalide. Utilisez ddmmyyyy.")
                return []
            self.feuilles_filtrées = []
            for feuille in excel_file.sheet_names:
                # S'assure que feuille est une chaîne avant la recherche
                feuille_str = str(feuille)
                if date_pattern in feuille_str:
                    self.feuilles_filtrées.append(feuille)
            return self.feuilles_filtrées
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {e}")
            return []
        
    
  


