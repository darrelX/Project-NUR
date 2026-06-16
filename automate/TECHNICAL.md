# Documentation Technique 🔧

## Architecture de l'application

L'application suit une architecture modulaire en couches :

```
┌─────────────────────────────────────┐
│         Interface (app.py)          │  ← Streamlit UI
├─────────────────────────────────────┤
│         Components Layer            │  ← Composants d'interface
│  • source_panel                     │
│  • celldown_card                    │
│  • ticket_card                      │
│  • ocm_card                         │
│  • execution_panel                  │
│  • preview_panel                    │
├─────────────────────────────────────┤
│         Services Layer              │  ← Logique métier
│  • celldown_service                 │
│  • ticket_service                   │
│  • ocm_service                      │
├─────────────────────────────────────┤
│         Core Layer                  │  ← Classes existantes
│  • CellDown                         │
│  • Ticket                           │
│  • SuperXlookup                     │
├─────────────────────────────────────┤
│         Utils Layer                 │  ← Utilitaires
│  • logger                           │
│  • styles                           │
│  • excel_utils                      │
└─────────────────────────────────────┘
```

## Flux de données

### 1. Upload et configuration

```
User Upload
    ↓
ExcelFileHandler.save_uploaded_file()
    ↓
Session State (st.session_state)
    ↓
Component Configuration
```

### 2. Prévisualisation

```
Config Dict
    ↓
Service.preview_matches()
    ↓
ExcelFileHandler.analyze_matches()
    ↓
Statistics Display
```

### 3. Exécution

```
Config Dict
    ↓
Service.execute()
    ↓
Core Class (CellDown/Ticket/SuperXlookup)
    ↓
Excel File Modification
    ↓
Logger Output
```

## Composants détaillés

### app.py (Application principale)

**Rôle** : Point d'entrée et orchestration

**Responsabilités** :
- Configuration de la page Streamlit
- Initialisation de la session
- Layout principal
- Coordination des composants

**Session State** :
```python
{
    'source_file_path': str,
    'source_sheet_path': str,
    'source_config': dict,
    'celldown_config': dict,
    'ticket_config': dict,
    'ocm_config': dict,
    'app_logs': list,
    'progress': dict
}
```

### Components Layer

#### source_panel.py

**Rôle** : Configuration de la source principale

**Fonction principale** :
```python
def render_source_panel() -> Optional[Dict]:
    """
    Returns:
        {
            'source_file_path': str,
            'source_sheet_path': str
        }
    """
```

**Features** :
- Upload de fichier
- Détection automatique des feuilles
- Prévisualisation optionnelle
- Statistiques du fichier

#### celldown_card.py, ticket_card.py, ocm_card.py

**Rôle** : Configuration des catégories

**Structure commune** :
```python
def render_[category]_card() -> Optional[Dict]:
    """
    Returns:
        {
            'enabled': bool,
            'target_file_path': str,
            ...paramètres spécifiques...
        }
    """
```

**Paramètres retournés** :
- Configuration complète pour le service
- Flag `enabled` pour savoir si la catégorie est active

#### execution_panel.py

**Rôle** : Exécution et résultats

**Fonctions principales** :
```python
def render_execution_panel(
    source_config: Dict,
    celldown_config: Dict,
    ticket_config: Dict,
    ocm_config: Dict
)

def _preview_matches(...)
def _execute_treatments(...)
```

**Workflow** :
1. Vérification de la configuration
2. Prévisualisation (optionnel)
3. Exécution séquentielle
4. Affichage des résultats

#### preview_panel.py

**Rôle** : Aperçu du fichier enrichi

**Features** :
- Chargement limité (100 lignes)
- Filtrage par colonnes
- Recherche dans les données
- Statistiques de remplissage
- Export CSV

### Services Layer

#### Structure commune des services

```python
class [Category]Service:
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
    
    def execute(self, config: Dict[str, Any]) -> bool:
        """Exécute le traitement"""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """Valide la configuration"""
        pass
    
    def preview_matches(self, config: Dict[str, Any]) -> Optional[Dict]:
        """Prévisualise les correspondances"""
        pass
```

**Responsabilités** :
- Validation des paramètres
- Wrapping des classes Core
- Gestion des erreurs
- Logging

### Utils Layer

#### logger.py

**Classes** :

1. **Logger** : Système de logging
```python
logger = Logger(session_key="app_logs")
logger.info("Message")
logger.success("Message")
logger.warning("Message")
logger.error("Message")
logger.render()  # Affichage dans Streamlit
```

2. **ProgressTracker** : Suivi de progression
```python
progress = ProgressTracker(total_steps=3)
progress.update(1, "Étape 1 en cours...")
progress.render()  # Barre de progression
```

#### styles.py

**Fonctions** :
```python
get_custom_css() -> str          # CSS complet
get_card_html(...) -> str        # HTML de carte
get_header_html() -> str         # Header principal
get_status_badge(...) -> str     # Badge de statut
```

**Variables CSS** :
- Couleurs primaires/secondaires
- Ombres (shadow-sm, md, lg, xl)
- Rayons de bordure (radius-sm, md, lg, xl)
- Couleurs de texte

#### excel_utils.py

**Classe** : ExcelFileHandler

**Méthodes principales** :
```python
get_sheet_names(file_path) -> List[str]
read_excel(file_path, sheet_name, nrows) -> pd.DataFrame
get_file_info(file_path) -> Dict
preview_dataframe(df, title, max_rows)
validate_column_exists(df, column_name) -> bool
find_column_matches(df, column_names) -> Optional[str]
analyze_matches(source_df, target_df, keys) -> Dict
save_uploaded_file(uploaded_file) -> Optional[str]
```

## Étendre l'application

### Ajouter une nouvelle catégorie

#### 1. Créer le service

`services/new_category_service.py` :
```python
from utils.logger import Logger

class NewCategoryService:
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
    
    def execute(self, config: Dict[str, Any]) -> bool:
        try:
            self.logger.info("Démarrage...")
            # Logique de traitement
            self.logger.success("✅ Terminé !")
            return True
        except Exception as e:
            self.logger.error(f"Erreur : {e}")
            return False
    
    def validate_config(self, config) -> tuple[bool, str]:
        # Validation
        return True, None
    
    def preview_matches(self, config) -> Optional[Dict]:
        # Analyse
        return {...}
```

#### 2. Créer le composant

`components/new_category_card.py` :
```python
import streamlit as st

def render_new_category_card() -> Optional[Dict]:
    st.markdown("### 🎯 Nouvelle Catégorie")
    
    with st.container():
        # HTML de la carte
        st.markdown('''
        <div class="custom-card">
            <div class="card-header">
                <div class="card-icon new-icon">🎯</div>
                <h3 class="card-title">Nouvelle Catégorie</h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Upload
        uploaded_file = st.file_uploader(
            "Fichier Excel",
            type=['xlsx', 'xls'],
            key="new_category_file"
        )
        
        config = {}
        
        if uploaded_file:
            # Configuration
            config['target_file_path'] = save_file(uploaded_file)
            config['enabled'] = True
            
            # Paramètres avancés
            with st.expander("⚙️ Paramètres avancés"):
                # Vos paramètres
                pass
            
            st.session_state['new_category_config'] = config
            return config
        else:
            config['enabled'] = False
            st.session_state['new_category_config'] = config
    
    return None
```

#### 3. Ajouter un style

`utils/styles.py` - Ajouter au CSS :
```css
.new-icon {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    color: white;
}
```

#### 4. Intégrer dans app.py

```python
from components.new_category_card import render_new_category_card
from services.new_category_service import NewCategoryService

# Dans initialize_session_state()
if 'new_category_config' not in st.session_state:
    st.session_state['new_category_config'] = {'enabled': False}

# Dans main(), ajouter une colonne
col1, col2, col3, col4 = st.columns(4)
# ... autres cartes ...
with col4:
    new_category_config = render_new_category_card()

# Dans render_execution_panel()
if 'new_category' in categories:
    service = NewCategoryService(logger)
    config = {**source_config, **new_category_config}
    success = service.execute(config)
    results['new_category'] = success
```

### Personnaliser les styles

#### Changer les couleurs

`utils/styles.py` :
```css
:root {
    --primary-color: #votre-couleur;
    --secondary-color: #votre-couleur;
}
```

#### Ajouter des animations

```css
@keyframes votre-animation {
    from { ... }
    to { ... }
}

.votre-classe {
    animation: votre-animation 1s ease;
}
```

### Ajouter des graphiques

`components/preview_panel.py` :
```python
import plotly.express as px

# Créer un graphique
fig = px.bar(df, x='col1', y='col2', title='Titre')
st.plotly_chart(fig, use_container_width=True)
```

## Gestion d'erreurs

### Pattern recommandé

```python
try:
    # Code à risque
    result = operation_risquee()
    logger.success("✅ Succès")
    return True
except FileNotFoundError as e:
    logger.error(f"Fichier introuvable : {e}")
    st.error("Fichier introuvable")
    return False
except KeyError as e:
    logger.error(f"Colonne manquante : {e}")
    st.error(f"Colonne '{e}' non trouvée")
    return False
except Exception as e:
    logger.error(f"Erreur inattendue : {e}")
    st.error("Une erreur est survenue")
    return False
```

### Validation des entrées

```python
# Vérifier les fichiers
if not Path(file_path).exists():
    return False, "Fichier introuvable"

# Vérifier les colonnes
if column not in df.columns:
    return False, f"Colonne '{column}' introuvable"

# Vérifier les types
if not isinstance(param, str):
    return False, "Paramètre invalide"
```

## Performance

### Optimisations appliquées

1. **Lecture limitée** : `nrows` pour la prévisualisation
2. **Caching** : Fichiers sauvegardés localement
3. **Session State** : Évite les rechargements
4. **Lazy Loading** : Composants chargés à la demande

### Recommandations

- Limiter les DataFrames affichés (< 1000 lignes)
- Utiliser `use_container_width=True` pour les tableaux
- Éviter les boucles dans le code Streamlit
- Utiliser `@st.cache_data` pour les données lourdes

## Sécurité

### Points de vigilance

1. **Fichiers temporaires** : Nettoyés après usage
2. **Validation des entrées** : Toujours valider les chemins
3. **Permissions** : Vérifier les droits d'écriture
4. **Données sensibles** : Ne pas logger de données confidentielles

### Bonnes pratiques

```python
# Valider les chemins
file_path = Path(user_input).resolve()
if not file_path.is_relative_to(allowed_dir):
    raise SecurityError("Chemin non autorisé")

# Nettoyer les inputs
clean_input = str(user_input).strip()

# Limiter les tailles de fichiers
if file.size > MAX_FILE_SIZE:
    raise ValueError("Fichier trop volumineux")
```

## Tests

### Tester un composant

```python
# test_component.py
def test_render_source_panel():
    config = render_source_panel()
    assert config is not None
    assert 'source_file_path' in config
```

### Tester un service

```python
# test_service.py
def test_celldown_service():
    logger = Logger()
    service = CellDownService(logger)
    
    config = {...}
    result = service.execute(config)
    
    assert result is True
```

## Déploiement

### Option 1 : Local
```powershell
streamlit run app.py
```

### Option 2 : Streamlit Cloud
1. Pusher le code sur GitHub
2. Connecter à Streamlit Cloud
3. Sélectionner le repo et `app.py`

### Option 3 : Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## Maintenance

### Logs à surveiller

- Erreurs de fichiers (FileNotFoundError)
- Erreurs de colonnes (KeyError)
- Erreurs de mémoire (MemoryError)

### Mises à jour

1. Tester en local
2. Vérifier les dépendances
3. Mettre à jour `requirements.txt`
4. Documenter les changements

---

**Dernière mise à jour** : 14 juin 2026  
**Version** : 1.0
