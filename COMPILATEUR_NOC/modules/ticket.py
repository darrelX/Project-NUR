# ============================================================================
# modules/ticket.py - Module de compilation Ticket
# ============================================================================

import pandas as pd
import re
import streamlit as st
from io import BytesIO

class TicketModule:
    """
    Module de compilation pour les fichiers Ticket.
    1. Extrait les codes sites depuis 'Site ID(Create TT)' avec préfixes
    2. Cherche les colonnes L, W, X, Y, Z, AB (par NOM)
    3. Concatène avec séparateur '..'
    4. Ajoute référence {date ticket}:
    """

    PREFIXES = [
        "CTR_", "SUO_", "SUD_", "NRO_", "ADM_",
        "NRD_", "EXN_", "LIT_", "EST_", "OST_"
    ]

    COLONNES_A_CHERCHER = ["L", "W", "X", "Y", "Z", "AB"]
    SEPARATEUR = ".."

    def __init__(self):
        self.nom = "Ticket"
        self.df_ticket_modifie = None  # Pour export
        self.date_reference = None  # Pour nommer le fichier

    @staticmethod
    def _lettre_excel_vers_index(lettre):
        """Convertit une lettre Excel en index de colonne (0-based)
        A=0, B=1, ..., Z=25, AA=26, AB=27, etc.
        """
        lettre = lettre.upper().strip()
        result = 0
        for char in lettre:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1  # Convertir en 0-based

    def compiler(self, df_principal, fichiers_sources, col_code_principal, date_reference):
        """
        Compile les données TICKET dans le fichier principal.
        """
        df_resultat = df_principal.copy()
        self.date_reference = date_reference  # Sauvegarder pour export

        if "Ticket" not in df_resultat.columns:
            df_resultat["Ticket"] = ""

        for fichier_data in fichiers_sources:
            contenu_binaire = fichier_data["binaire"]
            nom_fichier = fichier_data["nom"]

            try:
                df_ticket = pd.read_excel(BytesIO(contenu_binaire), sheet_name=0)
            except Exception as e:
                st.warning(f"⚠️ Erreur lecture Ticket {nom_fichier}: {str(e)}")
                continue

            # Chercher colonne "Site ID(Create TT)"
            col_site_id = self._trouver_colonne(df_ticket, [
                "site id", "site id(create tt)", "create tt"
            ])
            if col_site_id is None:
                st.warning(f"⚠️ Ticket {nom_fichier}: colonne 'Site ID(Create TT)' non trouvée")
                continue

            # Extraire les codes sites
            df_ticket['Code Site Extrait'] = df_ticket[col_site_id].astype(str).apply(
                self._extraire_code_site
            )

            # Chercher les colonnes L, W, X, Y, Z, AB
            colonnes_trouvees = self._chercher_colonnes(df_ticket, self.COLONNES_A_CHERCHER)
            
            if not colonnes_trouvees:
                st.warning(f"⚠️ Ticket {nom_fichier}: Colonnes L, W, X, Y, Z, AB non trouvées")
                st.info(f"Colonnes disponibles: {list(df_ticket.columns)}")
                continue

            # Afficher les colonnes trouvées
            st.info(f"✅ Ticket {nom_fichier}: Colonnes trouvées aux positions L,W,X,Y,Z,AB: {', '.join(colonnes_trouvees)}")

            # Concaténer les colonnes
            df_ticket['Infos Regroupées'] = df_ticket.apply(
                lambda row: self._concatener_par_index(df_ticket, row.name, self.COLONNES_A_CHERCHER), axis=1
            )

            # Ajouter référence
            df_ticket['Référence'] = f"{date_reference} ticket"

            # Créer la colonne complète pour le fichier principal
            df_ticket['Ticket Complet'] = df_ticket.apply(
                lambda row: f"{{{row['Référence']}}}: {row['Infos Regroupées']}" if row['Infos Regroupées'] else "",
                axis=1
            )

            # Sauvegarder pour export
            self.df_ticket_modifie = df_ticket.copy()

            # Créer une colonne normalisée pour le matching
            df_ticket['Code Site Extrait Normalized'] = df_ticket['Code Site Extrait'].str.strip().str.upper()

            # Afficher aperçu
            st.write(f"📊 Aperçu - Ticket {nom_fichier}:")
            apercu = df_ticket[['Code Site Extrait', 'Infos Regroupées', 'Ticket Complet']].head(10)
            st.dataframe(apercu, use_container_width=True)
            
            # Afficher statistiques d'extraction
            codes_extraits = df_ticket[df_ticket['Code Site Extrait'] != '']
            st.info(f"📍 Codes sites extraits: {len(codes_extraits)}/{len(df_ticket)} lignes")
            if len(codes_extraits) > 0:
                st.write(f"Exemples de codes trouvés: {', '.join(codes_extraits['Code Site Extrait'].unique()[:10].tolist())}")

            # XLOOKUP : pour chaque site du fichier principal
            matches_count = 0
            codes_principal = df_resultat[col_code_principal].astype(str).str.strip().str.upper().unique()
            codes_ticket = df_ticket['Code Site Extrait Normalized'].unique()
            
            # Afficher les codes disponibles pour debugging
            with st.expander("🔍 Debug - Codes sites disponibles"):
                st.write(f"**Codes dans le fichier principal (premiers 10):** {', '.join(sorted(codes_principal)[:10])}")
                st.write(f"**Codes extraits du Ticket (premiers 10):** {', '.join(sorted([c for c in codes_ticket if c])[:10])}")
            
            for idx, row in df_resultat.iterrows():
                code_site = str(row[col_code_principal]).strip().upper()

                # Chercher dans le fichier ticket par code site extrait (case-insensitive)
                ligne = df_ticket[df_ticket['Code Site Extrait Normalized'] == code_site]

                if not ligne.empty:
                    valeur_complete = str(ligne.iloc[0]['Ticket Complet'])
                    
                    if valeur_complete and valeur_complete != "":
                        matches_count += 1
                        if df_resultat.at[idx, "Ticket"]:
                            df_resultat.at[idx, "Ticket"] += " || " + valeur_complete
                        else:
                            df_resultat.at[idx, "Ticket"] = valeur_complete
            
            st.success(f"✅ {matches_count} codes sites du Ticket trouvés et introduits dans le fichier principal")

        return df_resultat

    def _extraire_code_site(self, texte):
        """Extrait le code site (ex: CTR_315) depuis la colonne Site ID(Create TT)
        Normalise le résultat en majuscules et sans espaces
        """
        if not isinstance(texte, str):
            texte = str(texte) if texte is not None else ""
        
        texte = texte.strip().upper()  # Normaliser en majuscules
        pattern = re.compile('|'.join(re.escape(p) for p in self.PREFIXES), re.IGNORECASE)
        match = pattern.search(texte)
        
        if match:
            start = match.start()
            # Extraire les caractères jusqu'au prochain espace ou point
            reste = texte[start:]
            # Chercher jusqu'au prochain espace ou caractère spécial
            code_match = re.match(r'[A-Z_]+\d{3,4}', reste)
            if code_match:
                return code_match.group(0).strip()
            # Fallback : extraire 7 caractères (CTR_315 = 7 chars)
            return reste[:7].strip()
        return ""

    def _chercher_colonnes(self, df, lettres):
        """Cherche les colonnes par INDEX (L, W, X, Y, Z, AB)
        Retourne les noms de colonnes aux positions demandées
        """
        colonnes_trouvees = []
        for lettre in lettres:
            idx = self._lettre_excel_vers_index(lettre)
            if idx < len(df.columns):
                colonnes_trouvees.append(df.columns[idx])
            else:
                st.warning(f"⚠️ Colonne {lettre} (index {idx}) n'existe pas (total: {len(df.columns)} colonnes)")
        return colonnes_trouvees

    def _concatener_par_index(self, df, row_index, lettres):
        """Récupère les colonnes par INDEX et concatène les valeurs avec '..'"""
        valeurs = []
        for lettre in lettres:
            idx = self._lettre_excel_vers_index(lettre)
            if idx < len(df.columns):
                val = df.iloc[row_index, idx]
                if pd.notna(val) and str(val).strip() and str(val).strip().upper() != "NAN":
                    valeurs.append(str(val).strip())
        return self.SEPARATEUR.join(valeurs)

    def _concatener_valeurs(self, row, colonnes):
        """Concatène les valeurs avec '..' (méthode legacy, pas utilisée)"""
        valeurs = []
        for col in colonnes:
            val = row.get(col, "")
            if pd.notna(val) and str(val).strip() and str(val).strip().upper() != "NAN":
                valeurs.append(str(val).strip())
        return self.SEPARATEUR.join(valeurs)

    def _trouver_colonne(self, df, mots_cles):
        """Cherche une colonne contenant un des mots clés"""
        for col in df.columns:
            for mot in mots_cles:
                if mot.lower() in str(col).lower():
                    return col
        return None

    def exporter_ticket(self):
        """Exporte le fichier COMPLET ticket avec les colonnes ajoutées"""
        if self.df_ticket_modifie is None:
            return None, None
        
        # Sélectionner TOUTES les colonnes originales + les nouvelles
        df_export = self.df_ticket_modifie.copy()
        
        # Réorganiser les colonnes : mettre les nouvelles colonnes en début
        colonnes_nouvelles = ['Code Site Extrait', 'Infos Regroupées', 'Référence', 'Ticket Complet']
        colonnes_originales = [c for c in df_export.columns if c not in colonnes_nouvelles]
        
        df_export = df_export[colonnes_nouvelles + colonnes_originales]
        
        # Convertir en bytes
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Ticket Regroupé')
        output.seek(0)
        
        # Créer le nom du fichier avec la date
        nom_fichier = f"TICKET_REGROUPES_{self.date_reference}.xlsx"
        
        return output.getvalue(), nom_fichier