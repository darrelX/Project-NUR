# Guide de Démarrage Rapide 🚀

## Installation en 3 étapes

### 1️⃣ Ouvrir PowerShell
```powershell
cd "c:\Users\f50056342\Desktop\computer science\NUR Project Lyne\automate"
```

### 2️⃣ Exécuter le script de démarrage
```powershell
.\start.ps1
```

### 3️⃣ Utiliser l'application
L'application s'ouvre automatiquement dans votre navigateur à : `http://localhost:8501`

---

## Installation manuelle (alternative)

### Créer l'environnement virtuel
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Installer les dépendances
```powershell
pip install -r requirements.txt
```

### Lancer l'application
```powershell
streamlit run app.py
```

---

## Premier traitement

### Étape 1 : Source principale
1. Cliquez sur "Browse files" dans la section **📂 Source principale**
2. Sélectionnez votre fichier Excel principal
3. Choisissez la feuille à traiter dans le menu déroulant
4. (Optionnel) Cochez "Afficher un aperçu des données"

### Étape 2 : Configurer CellDown (exemple)
1. Allez dans la section **📱 CellDown**
2. Uploadez le fichier CellDown (ex: `DAILY_W24_CELLS_DOWN.xlsx`)
3. Sélectionnez la date avec le date picker
4. (Optionnel) Ajustez les paramètres avancés

### Étape 3 : Configurer Ticket (exemple)
1. Allez dans la section **🎫 Ticket**
2. Uploadez le fichier Ticket (ex: `Incident_Ticket.xlsx`)
3. Les paramètres par défaut sont déjà optimisés

### Étape 4 : Configurer OCM RAN (exemple)
1. Allez dans la section **📡 OCM RAN**
2. Uploadez le fichier OCM RAN (ex: `OCM_RAN_INCIDENT.xlsx`)
3. Vérifiez que la feuille cible est "ALL SITES DOWN"

### Étape 5 : Prévisualiser (recommandé)
1. Descendez dans la section **🚀 Exécution**
2. Cliquez sur **🔍 Prévisualiser les résultats**
3. Consultez les statistiques de correspondances

### Étape 6 : Exécuter
1. Cliquez sur **▶ Exécuter les traitements**
2. Suivez la progression en temps réel
3. Consultez les logs détaillés
4. Le fichier source est automatiquement enrichi !

### Étape 7 : Télécharger et consulter les résultats
1. **📥 Télécharger** : Cliquez sur le bouton "Télécharger le fichier Excel enrichi"
   - Le fichier est automatiquement renommé avec un timestamp
   - Exemple : `Book1_enrichi_20260614_153045.xlsx`
2. **👁️ Aperçu** : Ouvrez l'expandeur "Aperçu du résultat"
   - Explorez les nouvelles colonnes ajoutées
   - Utilisez les filtres et la recherche
3. **📂 Fichier local** : Le fichier source original est également modifié sur votre ordinateur

---

## Exemples de fichiers

### Structure du fichier source
```
Codesite | Région   | Vendor | Status
---------|----------|--------|--------
ABC123   | Littoral | Nokia  | Down
ABC124   | Centre   | Huawei | Up
```

### Résultat après traitement
```
Codesite | Région   | Vendor | CellDown        | Ticket      | OCM RAN
---------|----------|--------|-----------------|-------------|-------------
ABC123   | Littoral | Nokia  | Power issue     | INC-001     | GEN FAILURE
ABC124   | Centre   | Huawei | Link down       | INC-002     | Battery Fault
```

---

## Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl + C` | Arrêter l'application (dans le terminal) |
| `Ctrl + R` | Rafraîchir la page (dans le navigateur) |
| `F5` | Recharger l'application |

---

## Fichiers générés

- **temp_uploads/** : Fichiers uploadés temporairement
- **Fichier source** : Modifié avec les nouvelles colonnes

---

## Problèmes courants

### L'application ne démarre pas
**Solution** : Vérifiez que Python 3.8+ est installé : `python --version`

### Erreur "Module not found"
**Solution** : Réinstallez les dépendances : `pip install -r requirements.txt`

### Les colonnes ne sont pas trouvées
**Solution** : Vérifiez les noms de colonnes dans les paramètres avancés

### Le fichier n'est pas modifié
**Solution** : Vérifiez que le fichier source n'est pas ouvert dans Excel

---

## Support

Pour toute question ou problème, consultez le README.md complet ou contactez l'équipe NUR Project Lyne.

---

**Bon traitement ! 🚀**
