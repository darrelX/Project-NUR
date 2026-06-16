# 🎯 Compilateur NOC

Outil de compilation et de traitement de données pour les rapports NOC (Network Operations Center).

## 📋 Fonctionnalités

### Modules de compilation
- **Cells DOWN**: Traitement des cellules hors service
- **OCM RAN Incident**: Gestion des incidents RAN
- **Hourly IHS**: Rapports IHS horaires
- **Ticket**: Gestion des tickets
- **Retour IHS**: Retours d'information IHS
- **Retour CAMUSAT**: Retours CAMUSAT
- **Dashboard Cell**: Dashboards par cellule
- **Top Offenders**: Identification des principaux problèmes

### Composants
- ✅ Upload multi-fichiers
- ✅ Sélection des sheets
- ✅ Filtrage par date (auto-détection)
- ✅ Sélection des colonnes
- ✅ Aperçu des données
- ✅ Export en Excel

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Installation des dépendances
```bash
pip install -r requirements.txt
```

## 📖 Utilisation

### Lancer l'application
```bash
streamlit run app.py
```

L'application s'ouvrira dans votre navigateur à `http://localhost:8501`

### Workflow de base
1. **Upload** des fichiers Excel/CSV
2. **Sélection** des sheets à traiter
3. **Filtrage** par date (optionnel)
4. **Sélection** des colonnes pertinentes
5. **Aperçu** des données
6. **Compilation** via les modules
7. **Téléchargement** des résultats

## 📁 Structure du projet

```
COMPILATEUR_NOC/
├── app.py                    # Interface principale (Streamlit)
├── config.py                 # Configuration globale
├── utils.py                  # Utilitaires et fonctions
├── requirements.txt          # Dépendances Python
├── README.md                 # Documentation
│
├── modules/                  # Modules de compilation
│   ├── __init__.py
│   ├── cells_down.py
│   ├── ocm_ran_incident.py
│   ├── hourly_ihs.py
│   ├── ticket.py
│   ├── retour_ihs.py
│   ├── retour_camusat.py
│   ├── dashboard_cell.py
│   └── top_offenders.py
│
├── components/               # Composants réutilisables
│   ├── __init__.py
│   ├── file_uploader.py
│   ├── date_filter.py
│   ├── sheet_selector.py
│   ├── column_selector.py
│   └── preview_table.py
│
├── data/                     # Fichiers temporaires
│   └── uploaded/
│
└── output/                   # Fichiers de sortie
    └── compilations/
```

## 🔧 Configuration

Éditer `config.py` pour modifier:
- Les répertoires
- Les formats acceptés
- Les colonnes communes
- La configuration des modules

## 📝 Notes de développement

### Dépendances principales
- **Streamlit**: Framework d'interface web
- **Pandas**: Manipulation de données
- **openpyxl**: Lecture/écriture Excel

### Extensions futures
- [ ] Support de bases de données
- [ ] Export en PDF
- [ ] Graphiques de visualisation
- [ ] API REST
- [ ] Authentification utilisateur

## 👨‍💻 Auteur

NOC Team

## 📄 Licence

Propriétaire

---

**Version**: 1.0.0  
**Dernière mise à jour**: 2026-05-17
