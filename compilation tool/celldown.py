import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import pandas as pd
from datetime import datetime


@dataclass
class CellDown:
    """
    Classe pour manipuler des fichiers Excel : affichage des feuilles,
    filtrage par date, et recherche XLOOKUP-like.
    """

    source_file_path: str
    target_file_path: str
    colown_key_path_source: str   # colonne clé dans la source
    target_value_column: str      # colonne à rapporter depuis la cible
    result_position_column: str   # colonne à remplir dans la source
    source_sheet_path: str = ""   # nom de la feuille source
    selected_date: str = ""       # date éventuellement filtrée

    # Nouveaux attributs pour la recherche croisée
    target_key_column: Optional[str] = None   # colonne clé dans la cible (par défaut = colown_key_path_source)
    target_sheet_name: Optional[str] = None   # nom de la feuille cible (obligatoire pour XLOOKUP)

    # --- NOUVEAUX ATTRIBUTS : paramètres de date et colonne de départ ---
    date_str: str = ""            # Date à rechercher (format jjmmaaaa)
    start_column: str = "C"       # Colonne de départ pour les résultats

    # Chemins internes
    _source_path: Path = field(init=False, repr=False)
    _target_path: Path = field(init=False, repr=False)

    def __post_init__(self):
        """Initialisation après le constructeur automatique."""
        self._source_path = Path(self.source_file_path)
        self._target_path = Path(self.target_file_path)

        # Valeurs par défaut pour la recherche
        if self.target_key_column is None:
            self.target_key_column = self.colown_key_path_source

    # ----------------------------------------------------------------------
    # Méthodes existantes (afficher_feuilles, filtrer_par_date, etc.)
    # ----------------------------------------------------------------------
    def _get_excel_file(self, file_path: Path) -> Optional[pd.ExcelFile]:
        """Retourne un objet ExcelFile ou None en cas d'erreur."""
        if not file_path.exists():
            print(f"Fichier introuvable : {file_path}")
            return None
        try:
            return pd.ExcelFile(file_path)
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier : {e}")
            return None

    def afficher_feuilles(self, nb_lignes_apercu: int = 5) -> None:
        """Affiche les noms des feuilles du fichier source et un aperçu."""
        excel_file = self._get_excel_file(self._source_path)
        if excel_file is None:
            return

        feuilles = excel_file.sheet_names
        print(f"Feuilles disponibles dans '{self._source_path}':")
        for i, feuille in enumerate(feuilles, 1):
            print(f"{i}. {feuille}")

        print("\nAperçu de chaque feuille :")
        for feuille in feuilles:
            print(f"\n=== {feuille} ===")
            try:
                df = pd.read_excel(self._source_path, sheet_name=feuille)
                if df.empty:
                    print("(Feuille vide)")
                else:
                    print(df.head(nb_lignes_apercu))
            except Exception as e:
                print(f"Erreur lors de la lecture de la feuille '{feuille}' : {e}")

    def filtrer_par_date(self, date_str: str) -> List[str]:
        """Filtre les feuilles dont le nom contient la date donnée (format jjmmaaaa)."""
        excel_file = self._get_excel_file(self._source_path)
        if excel_file is None:
            return []

        try:
            date_obj = datetime.strptime(date_str, "%d%m%Y")
            pattern = date_obj.strftime("%d%m%Y")
        except ValueError:
            print("Format de date invalide. Utilisez jjmmaaaa (ex: 12032025).")
            return []

        feuilles_filtrees = [
            feuille for feuille in excel_file.sheet_names
            if pattern in str(feuille)
        ]

        if feuilles_filtrees:
            print(f"Feuilles contenant '{pattern}' : {feuilles_filtrees}")
        else:
            print(f"Aucune feuille ne contient la date '{pattern}'.")

        self.selected_date = date_str
        return feuilles_filtrees
    
    def _col_letter_to_index(self, col: str) -> int:
        """
        Convertit une lettre de colonne Excel (A, B, C, ..., AA, AB, ...) en index (0, 1, 2, ...).
        
        Args:
            col: Lettre de colonne Excel (ex: 'A', 'B', 'AA')
            
        Returns:
            Index de la colonne (0-based)
        """
        col = col.upper().strip()
        result = 0
        for char in col:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1
    
    def _get_column_by_position(self, df: pd.DataFrame, position: str) -> str:
        """
        Retourne le nom de la colonne à partir d'une position (lettre Excel ou numéro).
        
        Args:
            df: DataFrame pandas
            position: Position de la colonne ('A', 'B', '1', '2', etc.)
            
        Returns:
            Nom de la colonne dans le DataFrame
        """
        position = str(position).strip()
        
        # Si c'est un nombre
        if position.isdigit():
            idx = int(position) - 1  # 1-based vers 0-based
            if 0 <= idx < len(df.columns):
                return df.columns[idx]
            raise IndexError(f"Position {position} hors limites (fichier a {len(df.columns)} colonnes)")
        
        # Si c'est une lettre Excel (A, B, AA, etc.)
        if position.isalpha():
            idx = self._col_letter_to_index(position)
            if 0 <= idx < len(df.columns):
                return df.columns[idx]
            raise IndexError(f"Colonne {position} hors limites (fichier a {len(df.columns)} colonnes)")
        
        # Sinon, c'est peut-être déjà un nom de colonne
        if position in df.columns:
            return position
        
        raise KeyError(f"Colonne '{position}' introuvable")
    
    def super_xlookup(self) -> None:
        """
        Effectue une recherche de type XLOOKUP entre un fichier source et un fichier cible.
        Remplit la colonne result_position_column dans le fichier source.
        
        Les colonnes peuvent être spécifiées par:
        - Lettre Excel: 'A', 'B', 'C', ..., 'AA', 'AB', ...
        - Numéro (1-based): '1', '2', '3', ...
        - Nom de l'entête: 'Codesite', 'Nom', ...
        """

        # --- Vérifications de base ---
        if not self.source_file_path or not self.target_file_path:
            raise ValueError("Les chemins source et cible doivent être définis.")

        if not self.colown_key_path_source:
            raise ValueError("La colonne clé source est obligatoire.")

        if not self.target_value_column:
            raise ValueError("La colonne valeur cible est obligatoire.")

        if not self.result_position_column:
            raise ValueError("La colonne de résultat est obligatoire.")

        # --- Chargement des fichiers Excel ---
        df_source = pd.read_excel(self.source_file_path, sheet_name=self.source_sheet_path or 0)
        df_target = pd.read_excel(self.target_file_path, sheet_name=self.target_sheet_name or 0)

        # --- Résolution des positions de colonnes ---
        source_key_col = self._get_column_by_position(df_source, self.colown_key_path_source)
        
        # Par défaut, la clé cible = clé source (même position)
        target_key_input = self.target_key_column or self.colown_key_path_source
        target_key_col = self._get_column_by_position(df_target, target_key_input)
        
        target_value_col = self._get_column_by_position(df_target, self.target_value_column)
        
        # Le nom de la colonne de résultat = nom de la feuille cible
        result_col_name = self.target_sheet_name or "Resultat"

        print(f"📊 Configuration XLOOKUP:")
        print(f"   Source: colonne '{source_key_col}'")
        print(f"   Cible:  clé='{target_key_col}', valeur='{target_value_col}'")
        print(f"   Résultat: colonne '{result_col_name}'")

        # --- Nettoyage des clés (important pour éviter les bugs) ---
        df_source[source_key_col] = df_source[source_key_col].astype(str).str.strip()
        df_target[target_key_col] = df_target[target_key_col].astype(str).str.strip()

        # --- Création du mapping (plus rapide que merge pour XLOOKUP simple) ---
        mapping = dict(zip(df_target[target_key_col], df_target[target_value_col]))

        # --- Application du lookup ---
        df_source[result_col_name] = df_source[source_key_col].map(mapping)

        # --- Statistiques ---
        matched = df_source[result_col_name].notna().sum()
        total = len(df_source)
        print(f"   Correspondances: {matched}/{total}")

        # --- Gestion des valeurs non trouvées ---
        df_source[result_col_name].fillna(" ", inplace=True)

        # --- Sauvegarde du fichier ---
        df_source.to_excel(self.source_file_path, index=False)

        print("✅ XLOOKUP terminé avec succès.")
    
    def _index_to_col_letter(self, idx: int) -> str:
        """
        Convertit un index (0-based) en lettre de colonne Excel (A, B, ..., AA, AB, ...).
        
        Args:
            idx: Index de la colonne (0-based)
            
        Returns:
            Lettre de colonne Excel
        """
        result = ""
        idx += 1  # Convertir en 1-based
        while idx > 0:
            idx, remainder = divmod(idx - 1, 26)
            result = chr(65 + remainder) + result
        return result
    
    def super_xlookup_par_date(self) -> None:
        """
        Filtre les feuilles par date et effectue un XLOOKUP pour chaque feuille trouvée.
        Les résultats sont placés dans des colonnes successives.
        
        Utilise les attributs self.date_str et self.start_column.
        
        Exemple:
            Si date_str = '27032026' retourne 3 feuilles, les résultats seront en colonnes C, D, E
        """
        # --- Vérifier que la date est fournie ---
        if not self.date_str:
            raise ValueError("L'attribut 'date_str' doit être renseigné avant d'appeler cette méthode.")

        # --- Filtrer les feuilles par date dans le fichier cible ---
        excel_file = self._get_excel_file(self._target_path)
        if excel_file is None:
            return
        
        try:
            date_obj = datetime.strptime(self.date_str, "%d%m%Y")
            pattern = date_obj.strftime("%d%m%Y")
        except ValueError:
            print("Format de date invalide. Utilisez jjmmaaaa (ex: 12032025).")
            return
        
        feuilles_filtrees = [
            feuille for feuille in excel_file.sheet_names
            if pattern in str(feuille)
        ]
        
        if not feuilles_filtrees:
            print(f"❌ Aucune feuille ne contient la date '{pattern}' dans {self._target_path}")
            return
        
        print(f"📅 Feuilles trouvées pour la date '{pattern}':")
        for i, feuille in enumerate(feuilles_filtrees, 1):
            print(f"   {i}. {feuille}")
        
        # --- Déterminer la colonne de départ ---
        start_col = str(self.start_column).strip()
        if start_col.isdigit():
            start_idx = int(start_col) - 1  # 1-based vers 0-based
        elif start_col.isalpha():
            start_idx = self._col_letter_to_index(start_col)
        else:
            start_idx = 2  # Par défaut colonne C (index 2)
        
        # --- Charger le fichier source une seule fois ---
        df_source = pd.read_excel(self.source_file_path, sheet_name=self.source_sheet_path or 0)
        source_key_col = self._get_column_by_position(df_source, self.colown_key_path_source)
        
        # Nettoyer la clé source
        df_source[source_key_col] = df_source[source_key_col].astype(str).str.strip()
        
        
        print(f"\n🔄 Exécution des XLOOKUP pour {len(feuilles_filtrees)} feuille(s)...\n")
        
        # --- Pour chaque feuille, faire un XLOOKUP ---
        for i, feuille in enumerate(feuilles_filtrees):
            current_col_idx = start_idx + i
            current_col_letter = self._index_to_col_letter(current_col_idx)
            
            print(f"   [{i+1}/{len(feuilles_filtrees)}] Feuille '{feuille}' → Colonne {current_col_letter}")
            
            try:
                # Charger la feuille cible
                df_target = pd.read_excel(self.target_file_path, sheet_name=feuille)
                
                # Résoudre les colonnes
                target_key_input = self.target_key_column or self.colown_key_path_source
                target_key_col = self._get_column_by_position(df_target, target_key_input)
                target_value_col = self._get_column_by_position(df_target, self.target_value_column)
                
                # Nettoyer la clé cible
                df_target[target_key_col] = df_target[target_key_col].astype(str).str.strip()
                
                # Créer le mapping
                mapping = dict(zip(df_target[target_key_col], df_target[target_value_col]))
                
                # Nom de la colonne = nom de la feuille
                result_col_name = feuille
                
                # Appliquer le lookup
                df_source[result_col_name] = df_source[source_key_col].map(mapping)
                
                # Statistiques
                matched = df_source[result_col_name].notna().sum()
                print(f"      Correspondances: {matched}/{len(df_source)}")
                
                # Remplacer les NaN par vide
                df_source[result_col_name].fillna(" ", inplace=True)
                
            except Exception as e:
                print(f"      ❌ Erreur: {e}")
                df_source[feuille] = "ERREUR"
        
        # --- Sauvegarder le fichier source ---
        df_source.to_excel(self.source_file_path, index=False)
        
        print(f"\n✅ XLOOKUP multiple terminé avec succès!")
        print(f"   Fichier mis à jour: {self.source_file_path}")
        print(f"   Colonnes ajoutées: {self._index_to_col_letter(start_idx)} à {self._index_to_col_letter(start_idx + len(feuilles_filtrees) - 1)}")
    
    def _resolve_result_column(self, df: pd.DataFrame, position: str) -> str:
        """
        Résout le nom de la colonne de résultat.
        Si la position existe, retourne son nom. Sinon, crée un nouveau nom.
        """
        position = str(position).strip()
        
        # Si c'est un numéro ou une lettre et que la colonne existe
        try:
            if position.isdigit() or position.isalpha():
                return self._get_column_by_position(df, position)
        except (IndexError, KeyError):
            pass
        
        # Sinon, utiliser la position comme nom de nouvelle colonne
        return f"Resultat_{position}" if position.isdigit() or position.isalpha() else position
        

# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Exemple d'utilisation avec positions de colonnes Excel
    # A = colonne 1 (Nom du Physique), B = colonne 2 (Codesite)
    
    celldown = CellDown(
        source_file_path="inputs/Book1.xlsx",
        target_file_path="inputs/W18_CELLS_DOWN_NOKIA_2704 AU 29042026 16h30.xlsx",
        colown_key_path_source="B",      # Colonne B dans source (Codesite)
        target_key_column="B",            # Colonne B dans cible (Site code)
        target_value_column="T",          # Colonne T dans cible (Comment)
        result_position_column="C",       # Colonne C pour le résultat
        source_sheet_path="Sheet1",
        date_str="29042026",              # Date à rechercher
        start_column="C"                  # Colonne de départ pour les résultats
    )
    
    print("=" * 60)
    print("TEST SUPER_XLOOKUP_PAR_DATE")
    print("=" * 60)
    
    # Appel sans paramètres : les valeurs sont lues depuis les attributs de l'instance
    celldown.super_xlookup_par_date()
    
    # Afficher le résultat
    import pandas as pd
    df = pd.read_excel("inputs/Book1.xlsx")
    print("\nAperçu du fichier résultat:")
    print(df.head(30))