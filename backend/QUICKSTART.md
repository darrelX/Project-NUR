# 🚀 Guide de Démarrage Rapide - Interface Streamlit

## ⚡ Installation (Une seule fois)

### 1. Installer les dépendances

Ouvrez PowerShell dans le dossier `backend` et exécutez :

```powershell
pip install -r requirements_stream.txt
```

Ou installation manuelle :
```powershell
pip install streamlit pandas openpyxl
```

## 🎯 Lancement Rapide

### Méthode 1 : Double-clic (Recommandé)
1. Allez dans le dossier `backend`
2. Double-cliquez sur **`start_stream.ps1`**
3. L'interface s'ouvre automatiquement dans votre navigateur

### Méthode 2 : Terminal
```powershell
cd "C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\backend"
streamlit run stream.py
```

L'interface sera accessible à : **http://localhost:8501**

## 📝 Utilisation en 5 Étapes

### Étape 1 : Fichier Source
```
Entrez le chemin de votre fichier Excel principal (celui qui sera modifié)
Exemple : C:\Users\...\Book1.xlsx
```

### Étape 2 : Choisir les Opérations
Cochez les opérations que vous voulez exécuter :
- ✅ **CellDown** : Pour traiter plusieurs feuilles par date
- ✅ **Super XLOOKUP** : Pour un XLOOKUP simple avec préfixe
- ✅ **Ticket** : Pour concaténer plusieurs colonnes et extraire des codes

### Étape 3 : Configurer les Paramètres
Pour chaque opération activée, remplissez :
- Fichier cible (où chercher les données)
- Colonnes clés (pour faire la correspondance)
- Position des résultats

### Étape 4 : Exécuter
Cliquez sur **🚀 Exécuter Toutes les Opérations**

### Étape 5 : Vérifier
Consultez le journal d'exécution et l'aperçu du fichier modifié

## 💡 Exemples de Configuration

### Exemple 1 : CellDown seul
```
✅ CellDown activé
    - Fichier cible : C:\...\DAILY_CELLS_DOWN.xlsx
    - Date : 12052026
    - Colonne source clé : B
    - Colonne cible clé : B
    - Colonne valeur : T
    - Colonne départ : C
    - Référence : CellDown ZTE
```

### Exemple 2 : Super XLOOKUP seul
```
✅ Super XLOOKUP activé
    - Fichier cible : C:\...\Incident.xlsx
    - Feuille source : Sheet1
    - Feuille cible : ALL SITES DOWN
    - Colonne source clé : B
    - Colonne cible clé : D
    - Colonne valeur : J
    - Position résultat : last_free
    - Nom résultat : Commentaire
    - Référence : NOKIA
```

### Exemple 3 : Ticket seul
```
✅ Ticket activé
    - Fichier cible : C:\...\Incident_Ticket.xlsx
    - Colonne source clé : B
    - Colonne extraction : T
    - Colonnes à joindre : L,W,X,Y,Z
    - Séparateur : ..
    - Position résultat : last_free
    - Nom résultat : Ticket
    - Référence : Ticket
```

### Exemple 4 : Tout activé (traitement complet)
```
✅ CellDown activé
✅ Super XLOOKUP activé
✅ Ticket activé

Ordre d'exécution :
1. CellDown ajoute des colonnes C, D, E... avec états par date
2. Super XLOOKUP ajoute une colonne "Commentaire" à la fin
3. Ticket ajoute une colonne "Ticket" à la fin

Résultat : Fichier enrichi avec toutes les informations
```

## ⚠️ Conseils Importants

### ✅ À FAIRE
- Faire une **copie de sauvegarde** de votre fichier source avant traitement
- Vérifier que tous les chemins de fichiers sont corrects
- Consulter l'aperçu du fichier pour connaître les noms des colonnes
- Utiliser "last_free" pour ajouter les colonnes à la fin (évite les conflits)

### ❌ À ÉVITER
- Ne lancez pas l'exécution sans vérifier les chemins de fichiers
- N'utilisez pas la même position de colonne pour plusieurs opérations
- Ne modifiez pas le fichier source dans Excel pendant que l'interface tourne

## 🛠️ Raccourcis Utiles

### Positions de colonnes
```
"A" ou "1"        → Première colonne
"B" ou "2"        → Deuxième colonne
"last_free"       → Ajoute à la fin (recommandé)
"Nom_Colonne"     → Utilise une colonne existante par son nom
```

### Formats de date (CellDown)
```
12052026  → 12 mai 2026
09052026  → 09 mai 2026
```

### Codes sites (Ticket)
```
Préfixes reconnus automatiquement :
CTR_, SUO_, SUD_, NRO_, ADM_, NRD_, EXN_, LIT_, EST_, OST_
```

## 🆘 Problèmes Fréquents

### L'interface ne se lance pas
```powershell
# Réinstaller streamlit
pip uninstall streamlit
pip install streamlit
```

### "Module not found: celldown/super_xlookup/ticket"
```powershell
# Vérifier que vous êtes dans le bon dossier
cd "C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\backend"
```

### "Fichier introuvable"
- Vérifiez le chemin complet du fichier
- Utilisez `\` au lieu de `/` sous Windows
- Exemple correct : `C:\Users\...\Book1.xlsx`

### Aucune feuille trouvée (CellDown)
- Vérifiez le format de date : `jjmmaaaa`
- Assurez-vous que les feuilles cibles contiennent bien cette date dans leur nom

## 📚 Documentation Complète

Pour plus de détails :
- **Guide complet** : [STREAM_README.md](./STREAM_README.md)
- **Architecture** : [ARCHITECTURE_STREAM.md](./ARCHITECTURE_STREAM.md)
- **Code source** : [stream.py](./stream.py)

## ✨ C'est parti !

Vous êtes prêt à utiliser l'interface. Bonne manipulation ! 🎉
