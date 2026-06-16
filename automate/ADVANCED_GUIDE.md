# Guide d'Utilisation Avancée 🚀

## Nouvelles fonctionnalités (Version 1.1)

### 📦 Support multi-fichiers

L'application supporte maintenant **plusieurs fichiers par catégorie**, conformément à vos besoins réels.

---

## 📱 CellDown Multi-Vendors

### Cas d'usage
Vous avez plusieurs fichiers CellDown, un par vendor (Nokia, Huawei, ZTE).

### Utilisation

1. **Uploadez plusieurs fichiers** dans la section CellDown
   - `DAILY_W24_CELLS_DOWN_NOKIA_...xlsx`
   - `DAILY_W24_CELLS_DOWN_HUAWEI_...xlsx`
   - `DAILY_W24_CELLS_DOWN_ZTE_...xlsx`

2. **La date est commune** à tous les fichiers CellDown
   - Une seule sélection de date
   - Une seule date de référence

3. **Configuration automatique par fichier**
   - Le **vendor est détecté automatiquement** du nom de fichier
   - Le **nom de référence** est auto-généré : `CellDown Nokia`, `CellDown Huawei`, etc.
   - Chaque fichier a ses propres paramètres avancés (modifiables)

4. **Exécution**
   - Tous les fichiers CellDown sont traités séquentiellement
   - Une barre de progression par fichier
   - Logs détaillés pour chaque vendor

### Exemple de configuration auto-détectée

**Fichier** : `DAILY_W24_CELLS_DOWN_NOKIA_13062026.xlsx`

```
✓ Vendor détecté : Nokia
✓ Nom de référence : CellDown Nokia
✓ Colonnes clés cibles : Site Code, SITE_CODE, site code, Code Site
✓ Colonnes valeurs : Comment, COMMENT, comment
```

---

## 📡 OCM RAN Multi-Horaires

### Cas d'usage
Vous avez plusieurs fichiers OCM RAN pris à différentes heures (18H UTC, 13H UTC, 11H UTC).

### Utilisation

1. **Uploadez plusieurs fichiers** dans la section OCM RAN
   - `OCM RAN INCIDENT FOLOW-UP 12-06-2026 18H UTC.xlsx`
   - `OCM RAN INCIDENT FOLOW-UP 12-06-2026 13H UTC.xlsx`
   - `OCM RAN INCIDENT FOLOW-UP 12-06-2026 11H UTC.xlsx`

2. **Configuration automatique par fichier**
   - L'**heure UTC est détectée automatiquement** du nom de fichier
   - Le **nom de colonne résultat** est auto-généré : `OCM RAN 18H UTC`, `OCM RAN 13H UTC`, etc.
   - Chaque fichier a ses propres paramètres avancés

3. **Exécution**
   - Tous les fichiers OCM RAN sont traités séquentiellement
   - Chaque fichier crée sa propre colonne dans le fichier source
   - Logs détaillés pour chaque horaire

### Exemple de configuration auto-détectée

**Fichier** : `OCM RAN INCIDENT FOLOW-UP 12-06-2026 18H UTC.xlsx`

```
✓ Horaire détecté : 18H UTC
✓ Nom de colonne : OCM RAN 18H UTC
✓ Colonnes clés cibles : Site ID, SITE_ID, site id, Site Code
✓ Colonnes valeurs : Actions en cours, Action en cours, Actions
✓ Feuille cible : ALL SITES DOWN
```

---

## 🎫 Ticket (Configuration améliorée)

### Paramètres par défaut basés sur l'usage réel

#### Colonnes à concaténer (TEXTJOIN)
**Nouveau format** : Colonnes avec alternatives

```
Ticket ID | Ticket ID(Create TT)
Description | Description(Process TT)
Solution | Solution(Process TT)
Root Cause | Root Cause(Process TT)
Incident Reason | Incident Reason Detail(Process TT)
```

Chaque ligne représente un groupe de colonnes alternatives. Le système cherchera la première correspondance.

#### Colonnes d'extraction
**Nouveau format** : Liste d'alternatives

```
Site Name
Site ID
SITE_ID
site id
site_code
site code
```

Le système cherchera la première colonne correspondante pour extraire les codes sites.

#### Paramètres par défaut

```
✓ Colonne clé source : Codesite (au lieu de "B")
✓ Séparateur : .. (inchangé)
✓ Ignorer cellules vides : Oui (inchangé)
✓ Nom de référence : Ticket (inchangé)
```

---

## 🔧 Workflow complet avec multi-fichiers

### Exemple réel

#### 1. Source principale
```
Fichier : Book1.xlsx
Feuille : Sheet1
```

#### 2. CellDown (3 fichiers)
```
✓ DAILY_W24_CELLS_DOWN_NOKIA_13062026.xlsx → CellDown Nokia
✓ DAILY_W24_CELLS_DOWN_HUAWEI_13062026.xlsx → CellDown Huawei
✓ DAILY_W24_CELLS_DOWN_ZTE_13062026.xlsx → CellDown ZTE

Date commune : 12/06/2026
```

#### 3. Ticket (1 fichier)
```
✓ Incident Ticket_20260614162016.xlsx → Ticket
```

#### 4. OCM RAN (3 fichiers)
```
✓ OCM RAN INCIDENT ... 18H UTC.xlsx → OCM RAN 18H UTC
✓ OCM RAN INCIDENT ... 13H UTC.xlsx → OCM RAN 13H UTC
✓ OCM RAN INCIDENT ... 11H UTC.xlsx → OCM RAN 11H UTC
```

#### 5. Résultat
Le fichier `Book1.xlsx` contiendra **7 nouvelles colonnes** :

```
Colonnes originales...
+ CellDown Nokia
+ CellDown Huawei
+ CellDown ZTE
+ Ticket
+ OCM RAN 18H UTC
+ OCM RAN 13H UTC
+ OCM RAN 11H UTC
```

---

## 📊 Prévisualisation

La prévisualisation s'adapte au nombre de fichiers :

### Exemple avec 7 traitements

```
CellDown Nokia     Ticket           OCM RAN 18H UTC
1250 matchs        1187 matchs      1193 matchs
95% couverture     89% couverture   91% couverture

CellDown Huawei    OCM RAN 13H UTC  OCM RAN 11H UTC
1180 matchs        1205 matchs      1198 matchs
93% couverture     92% couverture   91% couverture

CellDown ZTE
1225 matchs
94% couverture
```

---

## 🎯 Progression

La barre de progression s'adapte :

**Exemple** : 3 CellDown + 1 Ticket + 3 OCM RAN = **7 étapes**

```
[████████-----] 70% - OCM RAN 13H UTC

[10:25:12] Chargement du fichier source
[10:25:14] Exécution CellDown Nokia
[10:25:20] CellDown Nokia terminé
[10:25:21] Exécution CellDown Huawei
[10:25:28] CellDown Huawei terminé
[10:25:29] Exécution CellDown ZTE
[10:25:35] CellDown ZTE terminé
[10:25:36] Exécution Ticket
[10:25:43] Ticket terminé
[10:25:44] Exécution OCM RAN 18H UTC
[10:25:50] OCM RAN 18H UTC terminé
...
```

---

## ✅ Résultats

Affichage détaillé par traitement :

```
✅ CellDown Nokia    ✅ Ticket           ✅ OCM RAN 18H UTC
✅ CellDown Huawei   ✅ OCM RAN 13H UTC  ✅ OCM RAN 11H UTC
✅ CellDown ZTE
```

### 📥 Téléchargement du fichier enrichi

Après une exécution réussie, un **bouton de téléchargement** apparaît automatiquement :

```
🎉 Tous les traitements ont été exécutés avec succès en 52.3s !
📁 Le fichier source a été enrichi : C:\...\Book1.xlsx

-------------------
### 📥 Télécharger le résultat

[📥 Télécharger le fichier Excel enrichi]

📝 Nom du fichier : Book1_enrichi_20260614_153045.xlsx
```

**Format du nom** : `{NomOriginal}_enrichi_{AAAAMMJJ_HHMMSS}.xlsx`

**Exemple** :
- Fichier source : `Book1.xlsx`
- Fichier téléchargé : `Book1_enrichi_20260614_153045.xlsx`

**Avantages** :
- ✅ Timestamp unique (pas de conflit de noms)
- ✅ Traçabilité (savoir quand le fichier a été généré)
- ✅ Conservation du fichier original intact
- ✅ Format Excel natif (.xlsx)

---

## 💡 Conseils d'utilisation

### Pour CellDown
- **Nommez vos fichiers clairement** avec le vendor : `..._NOKIA_...`, `..._HUAWEI_...`, `..._ZTE_...`
- La détection est automatique mais vous pouvez modifier le nom de référence dans les paramètres avancés
- La date est commune : tous les CellDown utilisent la même date

### Pour OCM RAN
- **Incluez l'heure dans le nom** : `...18H UTC...`, `...13H UTC...`
- Chaque fichier crée une colonne distincte
- Utile pour suivre l'évolution dans le temps

### Pour Ticket
- **Utilisez le format avec alternatives** pour les colonnes : `Nom1 | Nom2 | Nom3`
- Le système trouvera automatiquement la première colonne existante
- Plus robuste face aux variations de nommage

---

## 🔄 Comparaison Ancien vs Nouveau

### Ancien système (v1.0)

```
CellDown : 1 fichier uniquement
OCM RAN  : 1 fichier uniquement
Ticket   : 1 fichier

Total    : 3 colonnes ajoutées
```

### Nouveau système (v1.1)

```
CellDown : Plusieurs fichiers (multi-vendors)
OCM RAN  : Plusieurs fichiers (multi-horaires)
Ticket   : 1 fichier (inchangé)

Total    : N colonnes ajoutées (flexible)
```

---

## 🐛 Dépannage

### Les fichiers multiples ne sont pas détectés
**Solution** : Vérifiez que vous utilisez bien le mode **"accept_multiple_files"** dans l'upload

### Le vendor n'est pas détecté correctement
**Solution** : Le système cherche `NOKIA`, `HUAWEI`, `ZTE`, etc. dans le nom de fichier. Si absent, utilisez les paramètres avancés pour modifier manuellement.

### L'heure UTC n'est pas détectée
**Solution** : Le système cherche le pattern `XXH UTC` (ex: `18H UTC`). Si absent, modifiez manuellement dans les paramètres avancés.

### Trop de traitements en même temps
**Solution** : C'est normal ! Le système exécute séquentiellement. Suivez la barre de progression et les logs.

---

## 📈 Performance

### Temps d'exécution estimé

**Par traitement** : ~5-10 secondes (selon taille fichier)

**Exemple** :
```
3 CellDown + 1 Ticket + 3 OCM RAN = 7 traitements
7 × 7s = ~49 secondes
```

### Optimisations
- Les traitements sont **séquentiels** (pas de parallélisation pour garantir l'intégrité)
- Les fichiers source sont **modifiés in-place** (pas de copie)
- Les logs sont **streamés en temps réel**

---

## 🎓 Exemples de cas d'usage

### Cas 1 : Opération télécoms quotidienne
```
Source : Rapport quotidien des sites
CellDown : Nokia + Huawei + ZTE (3 vendors)
Ticket : Incidents du jour
OCM RAN : Suivi multi-horaires (18H, 13H, 11H)

Résultat : Vue consolidée avec 7 colonnes enrichies
```

### Cas 2 : Analyse hebdomadaire
```
Source : Compilation hebdomadaire
CellDown : Tous les vendors
OCM RAN : Points clés de la semaine (plusieurs horaires)

Résultat : Analyse détaillée avec historique
```

### Cas 3 : Audit ponctuel
```
Source : Export système
Ticket : Tous les tickets ouverts
OCM RAN : État actuel

Résultat : Rapport d'audit complet
```

---

## 🚀 Évolutions futures

### Complétées ✅
- [x] Export Excel avec téléchargement automatique (v1.1.1)

### Planifiées pour v1.2
- [ ] Export multi-formats (CSV, JSON)
- [ ] Sauvegarde de configurations multi-fichiers
- [ ] Templates de traitements récurrents

### Planifiées pour v2.0
- [ ] Exécution parallélisée (optionnelle)
- [ ] Historique des traitements
- [ ] Comparaison avant/après

---

**Version** : 1.1  
**Date** : 14 juin 2026  
**Auteur** : NUR Project Lyne

---

**Bonne utilisation ! 🎉**
