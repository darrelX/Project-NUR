"""
Composant pour la prévisualisation des résultats
"""

import streamlit as st
import pandas as pd
from typing import Dict, Optional
from utils.excel_utils import ExcelFileHandler


def render_preview_panel(source_config: Optional[Dict]):
    """
    Affiche le panneau de prévisualisation du fichier final
    
    Args:
        source_config: Configuration de la source principale
    """
    if not source_config:
        return
    
    st.markdown("---")
    st.markdown("## 👁️ Aperçu du résultat")
    
    with st.expander("Afficher l'aperçu du fichier traité", expanded=False):
        with st.spinner("Chargement des données..."):
            # Lire le fichier source
            df = ExcelFileHandler.read_excel(
                source_config['source_file_path'],
                source_config['source_sheet_path'],
                nrows=100  # Limiter à 100 lignes pour la performance
            )
            
            if df is not None:
                # Informations générales
                st.markdown("### Informations générales")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Lignes totales", f"{len(df):,}")
                with col2:
                    st.metric("Colonnes", len(df.columns))
                with col3:
                    st.metric("Aperçu", "100 lignes")
                with col4:
                    file_size = pd.Series(df.memory_usage(deep=True)).sum() / (1024 * 1024)
                    st.metric("Taille", f"{file_size:.1f} MB")
                
                # Afficher les colonnes
                st.markdown("### Colonnes disponibles")
                
                # Séparer les colonnes originales et les nouvelles
                all_columns = df.columns.tolist()
                
                # Essayer de détecter les nouvelles colonnes
                # (celles qui contiennent "CellDown", "Ticket", "OCM" dans leur nom)
                new_columns = [col for col in all_columns 
                             if any(keyword in str(col) for keyword in ['CellDown', 'Ticket', 'OCM', 'RAN'])]
                original_columns = [col for col in all_columns if col not in new_columns]
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown("**Colonnes originales**")
                    st.caption(f"{len(original_columns)} colonnes")
                    with st.expander("Voir la liste"):
                        for col in original_columns:
                            st.text(f"• {col}")
                
                with col_info2:
                    st.markdown("**Nouvelles colonnes**")
                    st.caption(f"{len(new_columns)} colonnes")
                    if new_columns:
                        with st.expander("Voir la liste"):
                            for col in new_columns:
                                st.text(f"• {col}")
                    else:
                        st.info("Aucune nouvelle colonne détectée")
                
                # Afficher le DataFrame
                st.markdown("### Données")
                
                # Options de filtrage
                col_filter1, col_filter2 = st.columns(2)
                
                with col_filter1:
                    # Filtre par colonne
                    selected_columns = st.multiselect(
                        "Sélectionner les colonnes à afficher",
                        options=all_columns,
                        default=all_columns[:10] if len(all_columns) > 10 else all_columns,
                        key="preview_columns"
                    )
                
                with col_filter2:
                    # Recherche
                    search_term = st.text_input(
                        "Rechercher dans les données",
                        key="preview_search",
                        placeholder="Entrez un terme de recherche..."
                    )
                
                # Appliquer les filtres
                display_df = df.copy()
                
                if selected_columns:
                    display_df = display_df[selected_columns]
                
                if search_term:
                    # Recherche dans toutes les colonnes
                    mask = display_df.astype(str).apply(
                        lambda row: row.str.contains(search_term, case=False, na=False).any(),
                        axis=1
                    )
                    display_df = display_df[mask]
                    st.info(f"Résultats trouvés : {len(display_df)} lignes")
                
                # Afficher le DataFrame avec style
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=500
                )
                
                # Statistiques
                st.markdown("### Statistiques")
                
                # Compter les valeurs non-nulles dans les nouvelles colonnes
                if new_columns:
                    stats_cols = st.columns(len(new_columns))
                    
                    for idx, col in enumerate(new_columns):
                        with stats_cols[idx]:
                            non_null_count = df[col].notna().sum()
                            null_count = df[col].isna().sum()
                            
                            st.metric(
                                col,
                                f"{non_null_count:,}",
                                delta=f"{(non_null_count / len(df) * 100):.1f}% rempli"
                            )
                            st.caption(f"Vides : {null_count:,}")
                
                # Bouton de téléchargement
                st.markdown("### Téléchargement")
                
                col_download1, col_download2 = st.columns(2)
                
                with col_download1:
                    # Télécharger CSV
                    csv = display_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇ Télécharger en CSV",
                        data=csv,
                        file_name=f"resultat_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col_download2:
                    st.info("📄 Le fichier Excel original a été modifié directement")
                
            else:
                st.error("Impossible de charger le fichier")


def render_statistics_dashboard(df: pd.DataFrame, new_columns: list):
    """
    Affiche un tableau de bord de statistiques
    
    Args:
        df: DataFrame avec les données
        new_columns: Liste des nouvelles colonnes ajoutées
    """
    st.markdown("### 📊 Tableau de bord")
    
    # Résumé général
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sites totaux", f"{len(df):,}")
    
    with col2:
        if new_columns:
            avg_fill = sum(df[col].notna().sum() for col in new_columns) / (len(new_columns) * len(df)) * 100
            st.metric("Taux moyen de remplissage", f"{avg_fill:.1f}%")
        else:
            st.metric("Taux moyen de remplissage", "N/A")
    
    with col3:
        total_enriched = sum(df[col].notna().any() for _, row in df.iterrows() for col in new_columns if col in df.columns)
        st.metric("Lignes enrichies", f"{total_enriched:,}")
    
    with col4:
        st.metric("Nouvelles colonnes", len(new_columns))
    
    # Graphiques (si plotly est disponible)
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        
        st.markdown("#### Répartition des correspondances")
        
        if new_columns:
            # Créer un DataFrame pour le graphique
            match_data = {
                'Catégorie': new_columns,
                'Correspondances': [df[col].notna().sum() for col in new_columns]
            }
            
            chart_df = pd.DataFrame(match_data)
            
            # Graphique en barres
            fig = px.bar(
                chart_df,
                x='Catégorie',
                y='Correspondances',
                color='Catégorie',
                title="Nombre de correspondances par catégorie"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Graphique circulaire
            fig_pie = px.pie(
                chart_df,
                values='Correspondances',
                names='Catégorie',
                title="Répartition des correspondances"
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
    
    except ImportError:
        st.info("📊 Installez plotly pour voir les graphiques : `pip install plotly`")
