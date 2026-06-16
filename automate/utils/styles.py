"""
Styles CSS personnalisés pour l'application Streamlit
Style inspiré de Notion, Airtable, Power BI et Material Design 3
"""

def get_custom_css() -> str:
    """Retourne les styles CSS personnalisés pour l'application"""
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables globales */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #7c3aed;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --info-color: #3b82f6;
        
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-tertiary: #94a3b8;
        
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
    }
    
    /* Reset Streamlit default styles */
    .stApp {
        background-color: var(--bg-secondary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: var(--radius-xl);
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
        color: white;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .main-header p {
        font-size: 1.125rem;
        opacity: 0.95;
        margin-top: 0.5rem;
    }
    
    /* Cards */
    .custom-card {
        background-color: var(--bg-primary);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .card-icon {
        font-size: 1.5rem;
        width: 2.5rem;
        height: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius-md);
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    /* Icônes de catégorie */
    .celldown-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .ticket-icon {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .ocm-icon {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    /* Badges de statut */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        line-height: 1;
    }
    
    .status-success {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-error {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    .status-info {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    /* Section de configuration */
    .config-section {
        background-color: var(--bg-primary);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
    }
    
    .config-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Boutons personnalisés */
    .stButton > button {
        border-radius: var(--radius-md);
        font-weight: 500;
        transition: all 0.2s ease;
        border: none;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    /* Bouton principal d'exécution */
    .execute-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-size: 1.125rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: var(--radius-lg) !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-lg) !important;
        width: 100%;
    }
    
    .execute-button:hover {
        box-shadow: var(--shadow-xl) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Progress bar personnalisée */
    .custom-progress {
        background-color: var(--bg-tertiary);
        border-radius: 9999px;
        height: 1rem;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .custom-progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        transition: width 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Log console */
    .log-console {
        background-color: #1e293b;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: var(--radius-md);
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.875rem;
        max-height: 300px;
        overflow-y: auto;
        margin: 1rem 0;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.2);
    }
    
    .log-entry {
        margin-bottom: 0.25rem;
        display: flex;
        gap: 0.5rem;
    }
    
    .log-time {
        color: #94a3b8;
        font-weight: 500;
    }
    
    .log-message {
        color: #e2e8f0;
    }
    
    .log-success {
        color: #10b981;
    }
    
    .log-error {
        color: #ef4444;
    }
    
    .log-warning {
        color: #f59e0b;
    }
    
    /* DataFrames */
    .dataframe {
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
    }
    
    .dataframe thead tr th {
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: 0.75rem !important;
        border-bottom: 2px solid var(--border-color) !important;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: var(--bg-secondary) !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #e0e7ff !important;
    }
    
    /* Colonnes colorées selon catégorie */
    .column-celldown {
        background-color: #e0e7ff !important;
    }
    
    .column-ticket {
        background-color: #fef3c7 !important;
    }
    
    .column-ocm {
        background-color: #ccfbf1 !important;
    }
    
    /* File uploader */
    .uploadedFile {
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-md);
        padding: 1rem;
        background-color: var(--bg-secondary);
    }
    
    /* Expander personnalisé */
    .streamlit-expanderHeader {
        background-color: var(--bg-tertiary) !important;
        border-radius: var(--radius-md) !important;
        font-weight: 500 !important;
    }
    
    /* Métrics */
    .metric-card {
        background-color: var(--bg-primary);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        text-align: center;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Stats cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--bg-primary);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.875rem;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """


def get_card_html(title: str, icon: str, category: str) -> str:
    """Génère le HTML pour une carte de catégorie"""
    return f"""
    <div class="custom-card fade-in">
        <div class="card-header">
            <div class="card-icon {category}-icon">{icon}</div>
            <h3 class="card-title">{title}</h3>
        </div>
    </div>
    """


def get_header_html() -> str:
    """Génère le HTML pour le header principal"""
    return """
    <div class="main-header fade-in">
        <h1>🚀 Plateforme de Traitement Excel</h1>
        <p>Exécutez vos moteurs CellDown, Ticket et OCM RAN en quelques clics</p>
    </div>
    """


def get_status_badge(status: str, text: str) -> str:
    """Génère un badge de statut coloré"""
    return f'<span class="status-badge status-{status}">{text}</span>'
