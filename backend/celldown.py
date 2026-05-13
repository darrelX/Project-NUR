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
    reference_name: str = ""      # nom de référence pour les résultats

    # Nouveaux attributs pour la recherche croisée
    target_key_column: Optional[str] = None   # colonne clé dans la cible
    target_sheet_name: Optional[str] = None

    # Paramètres de date et colonne de départ
    date_str: str = ""
    start_column: str = "C"

    _source_path: Path = field(init=False, repr=False)
    _target_path: Path = field(init=False, repr=False)

    def __post_init__(self):
        self._source_path = Path(self.source_file_path)
        self._target_path = Path(self.target_file_path)
        if self.target_key_column is None:
            self.target_key_column = self.colown_key_path_source

    # ----------------------------------------------------------------------
    # Utilitaires
    # ----------------------------------------------------------------------
    def _col_letter_to_index(self, col: str) -> int:
        col = col.upper().strip()
        result = 0
        for char in col:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1

    def _get_column_by_position(self, df: pd.DataFrame, position: str) -> str:
        position = str(position).strip()
        
        # 1. Vérifier si c'est un index numérique (1, 2, 3...)
        if position.isdigit():
            idx = int(position) - 1
            if 0 <= idx < len(df.columns):
                return df.columns[idx]
            raise IndexError(f"Position {position} hors limites")
        
        # 2. Vérifier si c'est un NOM de colonne existant (priorité sur lettre)
        if position in df.columns:
            return position
        
        # 3. Vérifier si c'est une lettre de colonne (A, B, C...)
        # Uniquement si 1-2 caractères pour éviter de confondre avec des noms
        if position.isalpha() and len(position) <= 2:
            idx = self._col_letter_to_index(position)
            if 0 <= idx < len(df.columns):
                return df.columns[idx]
            raise IndexError(f"Colonne {position} hors limites")
        
        # 4. Si rien ne correspond
        raise KeyError(f"Colonne '{position}' introuvable")

    def _index_to_col_letter(self, idx: int) -> str:
        result = ""
        idx += 1
        while idx > 0:
            idx, remainder = divmod(idx - 1, 26)
            result = chr(65 + remainder) + result
        return result

    def _read_sheet_safe(self, file_path: str, sheet_name: str) -> pd.DataFrame:
        """
        Lit une feuille Excel de manière robuste face aux filtres invalides.
        On force dtype=str pour éviter les erreurs de validation des filtres.
        """
        return pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            engine='openpyxl',
            dtype=str,
            keep_default_na=False,
            na_values=['']
        )

    # ----------------------------------------------------------------------
    # Méthode principale optimisée
    # ----------------------------------------------------------------------
    def super_xlookup_par_date(self) -> None:
        """
        Filtre les feuilles par date et effectue un XLOOKUP pour chaque feuille.
        Lit uniquement les feuilles nécessaires (pas de chargement complet du fichier).
        Ajoute le préfixe "[reference_name - date_aujourd'hui] " devant chaque texte.
        """
        if not self.date_str:
            raise ValueError("L'attribut 'date_str' doit être renseigné.")

        # --- Récupérer les noms des feuilles (rapide, pas de données) ---
        try:
            excel_file = pd.ExcelFile(self.target_file_path, engine='openpyxl')
            all_sheets = excel_file.sheet_names
        except Exception as e:
            print(f"❌ Impossible de lire les feuilles du fichier cible : {e}")
            return

        # --- Filtrer par date ---
        try:
            date_obj = datetime.strptime(self.date_str, "%d%m%Y")
            pattern = date_obj.strftime("%d%m%Y")
        except ValueError:
            print("Format de date invalide. Utilisez jjmmaaaa (ex: 12032025).")
            return

        feuilles_filtrees = [s for s in all_sheets if pattern in str(s)]

        if not feuilles_filtrees:
            print(f"❌ Aucune feuille ne contient la date '{pattern}' dans {self.target_file_path}")
            return

        print(f"📅 Feuilles trouvées pour la date '{pattern}':")
        for i, feuille in enumerate(feuilles_filtrees, 1):
            print(f"   {i}. {feuille}")

        # --- Déterminer la colonne de départ ---
        start_col = str(self.start_column).strip()
        if start_col.isdigit():
            start_idx = int(start_col) - 1
        elif start_col.isalpha():
            start_idx = self._col_letter_to_index(start_col)
        else:
            start_idx = 2  # par défaut colonne C

        # --- Charger le fichier source (une seule fois) ---
        df_source = self._read_sheet_safe(self.source_file_path, sheet_name=self.source_sheet_path or 0)
        source_key_col = self._get_column_by_position(df_source, self.colown_key_path_source)
        df_source[source_key_col] = df_source[source_key_col].astype(str).str.strip()

        # Préfixe commun (utilisé pour chaque feuille)
        prefix = ""
        if self.reference_name:
            today_str = datetime.now().strftime("%d/%m/%Y")
            prefix = f"[{self.reference_name} - {today_str}] "

        # --- Parcourir chaque feuille filtrée (lecture à la demande) ---
        for i, feuille in enumerate(feuilles_filtrees):
            current_col_idx = start_idx + i
            current_col_letter = self._index_to_col_letter(current_col_idx)

            print(f"   [{i+1}/{len(feuilles_filtrees)}] Feuille '{feuille}' → Colonne {current_col_letter}")

            try:
                df_target = self._read_sheet_safe(self.target_file_path, sheet_name=feuille)
            except Exception as e:
                print(f"      ❌ Erreur de lecture de la feuille : {e}")
                df_source[feuille] = "ERREUR_LECTURE"
                continue

            if df_target.empty:
                print("      ⚠️ Feuille vide, colonne remplie avec chaînes vides.")
                df_source[feuille] = ""
                continue

            # Résolution des colonnes cibles
            target_key_input = self.target_key_column or self.colown_key_path_source
            target_key_col = self._get_column_by_position(df_target, target_key_input)
            target_value_col = self._get_column_by_position(df_target, self.target_value_column)

            df_target[target_key_col] = df_target[target_key_col].astype(str).str.strip()
            mapping = dict(zip(df_target[target_key_col], df_target[target_value_col]))

            # XLOOKUP
            df_source[feuille] = df_source[source_key_col].map(mapping).fillna("")

            # Ajout du préfixe si demandé
            if prefix:
                df_source[feuille] = df_source[feuille].apply(lambda x: f"{prefix}{x}" if x != "" else "")

            matched = (df_source[feuille] != "").sum()
            print(f"      Correspondances (non vides) : {matched}/{len(df_source)}")

        # --- Sauvegarde ---
        df_source.to_excel(self.source_file_path, index=False)
        print(f"\n✅ Mise à jour terminée : {self.source_file_path}")
        print(f"   Colonnes ajoutées : {self._index_to_col_letter(start_idx)} à {self._index_to_col_letter(start_idx + len(feuilles_filtrees) - 1)}")


if __name__ == "__main__":
    celldown = CellDown(
        source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx",
        target_file_path=r"C:\Users\f50056342\Desktop\my work\cellsdow files\celldown Huawei\DAILY_W20_CELLS_DOWN_HUAWEI_11052026 16h.xlsx",
        colown_key_path_source="B",
        target_key_column="B",
        target_value_column="T",
        result_position_column="last_column",
        source_sheet_path="Sheet1",
        date_str="11052026",
        start_column="C",
        reference_name="CellDown Huawei"
    )
    celldown.super_xlookup_par_date()

    # Affichage du résultat
    df = pd.read_excel(r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx")
    print("\nAperçu du fichier résultat :")
    print(df.head(30))