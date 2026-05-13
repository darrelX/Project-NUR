# 📊 Interface Streamlit - Suite d'Opérations Excel

## 🎯 Vue d'ensemble

Cette interface Streamlit permet d'exécuter **séquentiellement** trois opérations Excel sur un même fichier source :

1. **CellDown** : XLOOKUP multiple sur des feuilles filtrées par date
2. **Super XLOOKUP** : XLOOKUP simple avec préfixe [nom - date]
3. **Ticket** : XLOOKUP avec extraction de codes sites et concaténation multi-colonnes (TEXTJOIN)

## 🚀 Lancement

### Méthode 1 : Depuis le terminal
```bash
cd "C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\backend"
streamlit run stream.py
```

### Méthode 2 : Script PowerShell (recommandé)
Double-cliquez sur `start_stream.ps1` dans le dossier backend

## 📋 Guide d'utilisation

### 1️⃣ Fichier Source Commun
- Spécifiez le chemin du fichier Excel qui sera modifié par **toutes** les opérations
- Le fichier est traité **séquentiellement** : chaque opération travaille sur les résultats de la précédente
- Un aperçu s'affiche automatiquement pour vérifier les colonnes disponibles

### 2️⃣ Configuration des Opérations

#### 🔽 CellDown
Active cette opération si vous voulez :
- Filtrer plusieurs feuilles par date dans un fichier cible
- Effectuer un XLOOKUP pour chaque feuille filtrée
- Ajouter les résultats dans des colonnes successives (C, D, E, ...)

**Paramètres principaux :**
- **Fichier cible** : fichier avec plusieurs feuilles (ex: DAILY_CELLS_DOWN.xlsx)
- **Date de filtrage** : format `jjmmaaaa` (ex: 12052026)
- **Colonne de départ** : première colonne où écrire les résultats (ex: C)
- **Nom de référence** : pour le préfixe `[NOM - date]`

#### 🔍 Super XLOOKUP
Active cette opération si vous voulez :
- Faire un XLOOKUP simple entre source et cible
- Ajouter un préfixe `[nom - date]` devant chaque valeur trouvée
- Choisir la position exacte de la colonne résultat

**Paramètres principaux :**
- **Fichier cible** : fichier Excel à consulter
- **Colonnes clés** : colonnes de correspondance (source et cible)
- **Colonne valeur** : colonne à rapporter depuis la cible
- **Position résultat** : où écrire (ex: "last_free" pour ajouter à la fin)

#### 🎫 Ticket (Multi-Column XLOOKUP)
Active cette opération si vous voulez :
- Extraire automatiquement des codes sites (CTR_, SUO_, etc.)
- Concaténer plusieurs colonnes avec TEXTJOIN
- Mapper les résultats dans le fichier source

**Paramètres principaux :**
- **Colonnes à concaténer** : liste séparée par virgules (ex: L,W,X,Y,Z)
- **Séparateur** : caractère(s) de jonction (ex: ..)
- **Colonne extraction** : où chercher les codes sites dans la cible

### 3️⃣ Exécution

1. Cochez les opérations que vous souhaitez activer (✅)
2. Remplissez les paramètres pour chaque opération activée
3. Cliquez sur **🚀 Exécuter Toutes les Opérations**

**Ordre d'exécution :**
```
Fichier Source
    ↓
[1] CellDown (si activé)
    ↓
[2] Super XLOOKUP (si activé)
    ↓
[3] Ticket (si activé)
    ↓
Fichier Source (modifié)
```

### 4️⃣ Journal d'Exécution

Après l'exécution, consultez :
- ✅ **Succès** : opérations réussies avec détails
- ❌ **Erreurs** : problèmes rencontrés avec traces complètes
- 👁️ **Aperçu final** : visualisation du fichier après traitement

## 💡 Exemples de Cas d'Usage

### Cas 1 : Analyse complète d'un rapport de sites
```
1. CellDown : récupère les états de cellules pour plusieurs dates
2. Super XLOOKUP : ajoute les commentaires d'incidents
3. Ticket : ajoute les numéros de tickets concaténés
```

### Cas 2 : Enrichissement simple
```
1. Super XLOOKUP activé uniquement : ajoute une colonne depuis une source externe
```

### Cas 3 : Suivi temporel
```
1. CellDown activé uniquement : génère un historique multi-dates dans des colonnes successives
```

## ⚠️ Points d'Attention

1. **Sauvegarde** : Le fichier source est **modifié directement**. Faites une copie avant traitement!
2. **Ordre** : Les opérations s'exécutent dans l'ordre CellDown → SuperXlookup → Ticket
3. **Colonnes** : Utilisez des lettres (A, B), des numéros (1, 2) ou des noms de colonnes
4. **Position "last_free"** : Ajoute toujours la colonne à la fin (pratique pour éviter les conflits)
5. **Filtres Excel** : Les filtres sont automatiquement supprimés pour éviter les bugs

## 🐛 Dépannage

### Problème : "Fichier introuvable"
- Vérifiez que le chemin est complet et entre guillemets si nécessaire
- Utilisez des `\` doubles ou des raw strings : `r"C:\Users\..."`

### Problème : "Colonne introuvable"
- Consultez l'aperçu du fichier pour voir les noms exacts des colonnes
- Les colonnes peuvent être spécifiées par lettre (B), numéro (2), ou nom ("Codesite")

### Problème : "Aucune feuille trouvée" (CellDown)
- Vérifiez le format de la date : `jjmmaaaa` (ex: 12052026)
- Assurez-vous que les noms des feuilles contiennent bien cette date

### Problème : "Erreur d'extraction de code site" (Ticket)
- Vérifiez que la colonne d'extraction contient bien des codes CTR_, SUO_, etc.
- Les préfixes par défaut sont : CTR_, SUO_, SUD_, NRO_, ADM_, NRD_, EXN_, LIT_, EST_, OST_

## 📞 Support

Pour toute question ou amélioration, consultez les fichiers sources :
- [celldown.py](./celldown.py)
- [super_xlookup.py](./super_xlookup.py)
- [ticket.py](./ticket.py)
