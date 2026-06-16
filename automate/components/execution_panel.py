"""
Composant pour le panneau d'exécution des traitements
"""

import streamlit as st
from typing import Dict, List
import time
from datetime import datetime
from pathlib import Path

from services.celldown_service import CellDownService
from services.ticket_service import TicketService
from services.ocm_service import OcmService
from utils.logger import Logger, ProgressTracker


def render_execution_panel(source_config: Dict, 
                          celldown_config: Dict, 
                          ticket_config: Dict, 
                          ocm_config: Dict):
    """
    Affiche le panneau d'exécution avec le bouton principal et les résultats
    
    Args:
        source_config: Configuration de la source principale
        celldown_config: Configuration CellDown
        ticket_config: Configuration Ticket
        ocm_config: Configuration OCM RAN
    """
    st.markdown("---")
    st.markdown("## 🚀 Exécution")
    
    # Résumé de configuration
    st.markdown("### Configuration chargée")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if source_config:
            st.success(f"✓ Source principale : {source_config.get('source_file_path', 'N/A').split('/')[-1].split('\\')[-1]}")
            st.info(f"  → Feuille : {source_config.get('source_sheet_path', 'N/A')}")
        else:
            st.error("✗ Source principale non configurée")
        
        # Vérifier les catégories activées
        categories = []
        
        if celldown_config and celldown_config.get('enabled'):
            file_count = celldown_config.get('count', 0)
            if file_count > 0:
                st.success(f"✓ CellDown : {file_count} fichier(s)")
                categories.append('celldown')
            else:
                st.warning("⊘ CellDown : aucun fichier")
        else:
            st.warning("⊘ CellDown : non configuré")
        
        if ticket_config and ticket_config.get('enabled'):
            file_name = ticket_config.get('target_file_path', 'N/A').split('/')[-1].split('\\')[-1]
            st.success(f"✓ Ticket : {file_name}")
            categories.append('ticket')
        else:
            st.warning("⊘ Ticket : non configuré")
        
        if ocm_config and ocm_config.get('enabled'):
            file_count = ocm_config.get('count', 0)
            if file_count > 0:
                st.success(f"✓ OCM RAN : {file_count} fichier(s)")
                categories.append('ocm')
            else:
                st.warning("⊘ OCM RAN : aucun fichier")
        else:
            st.warning("⊘ OCM RAN : non configuré")
    
    with col2:
        st.metric("Traitements actifs", len(categories))
    
    # Bouton d'exécution
    can_execute = source_config is not None and len(categories) > 0
    
    if not can_execute:
        st.warning("⚠️ Configurez au moins la source principale et une catégorie pour continuer")
    
    # Bouton de prévisualisation
    col_preview, col_execute = st.columns(2)
    
    with col_preview:
        if st.button("🔍 Prévisualiser les résultats", 
                    disabled=not can_execute,
                    use_container_width=True):
            _preview_matches(source_config, celldown_config, ticket_config, ocm_config, categories)
    
    with col_execute:
        execute_button = st.button(
            "▶ Exécuter les traitements",
            type="primary",
            disabled=not can_execute,
            use_container_width=True,
            key="execute_button"
        )
    
    # Exécution
    if execute_button:
        _execute_treatments(source_config, celldown_config, ticket_config, ocm_config, categories)


def _preview_matches(source_config, celldown_config, ticket_config, ocm_config, categories):
    """Prévisualise les correspondances avant exécution"""
    st.markdown("### 🔍 Prévisualisation des correspondances")
    
    logger = Logger()
    
    with st.spinner("Analyse des correspondances..."):
        results = {}
        
        # CellDown (possiblement plusieurs fichiers)
        if 'celldown' in categories and celldown_config.get('files'):
            for file_config in celldown_config['files']:
                service = CellDownService(logger)
                config = {**source_config, **file_config}
                matches = service.preview_matches(config)
                if matches:
                    vendor = file_config.get('reference_name', 'CellDown')
                    results[vendor] = matches
        
        # Ticket
        if 'ticket' in categories:
            service = TicketService(logger)
            config = {**source_config, **ticket_config}
            matches = service.preview_matches(config)
            if matches:
                results['Ticket'] = matches
        
        # OCM RAN (possiblement plusieurs fichiers)
        if 'ocm' in categories and ocm_config.get('files'):
            for file_config in ocm_config['files']:
                service = OcmService(logger)
                config = {**source_config, **file_config}
                matches = service.preview_matches(config)
                if matches:
                    label = file_config.get('result_column_name', 'OCM RAN')
                    results[label] = matches
    
    # Afficher les résultats
    if results:
        # Adapter le nombre de colonnes selon le nombre de résultats
        num_results = len(results)
        cols_per_row = min(3, num_results)
        
        # Créer les lignes nécessaires
        result_items = list(results.items())
        for i in range(0, num_results, cols_per_row):
            cols = st.columns(cols_per_row)
            for j, (category, stats) in enumerate(result_items[i:i+cols_per_row]):
                with cols[j]:
                    st.markdown(f"#### {category}")
                    
                    if 'error' in stats:
                        st.error(stats['error'])
                    else:
                        if isinstance(stats.get('total_matches'), int):
                            st.metric(
                                "Correspondances",
                                f"{stats['total_matches']:,}",
                                delta=f"{stats.get('match_rate', 0):.1f}%" if 'match_rate' in stats else None
                            )
                        else:
                            st.info(f"Correspondances : {stats.get('total_matches', 'N/A')}")
                        
                        if 'source_total' in stats:
                            st.caption(f"Total source : {stats['source_total']:,}")
                        if 'target_total' in stats:
                            st.caption(f"Total cible : {stats['target_total']:,}")


def _execute_treatments(source_config, celldown_config, ticket_config, ocm_config, categories):
    """Exécute les traitements configurés"""
    st.markdown("### ⚙️ Exécution en cours")
    
    # DEBUG: Afficher les configs reçues
    with st.expander("🔍 DEBUG - Configurations reçues", expanded=False):
        st.json({
            "categories": categories,
            "source_config": source_config,
            "celldown_enabled": celldown_config.get('enabled') if celldown_config else False,
            "celldown_files_count": celldown_config.get('count', 0) if celldown_config else 0,
            "ticket_enabled": ticket_config.get('enabled') if ticket_config else False,
            "ticket_config_keys": list(ticket_config.keys()) if ticket_config else [],
            "ocm_enabled": ocm_config.get('enabled') if ocm_config else False,
            "ocm_files_count": ocm_config.get('count', 0) if ocm_config else 0
        })
    
    # Initialiser le logger
    logger = Logger(session_key="execution_logs")
    logger.clear()
    
    # Calculer le nombre total d'étapes
    total_steps = 0
    if 'celldown' in categories and celldown_config.get('files'):
        total_steps += len(celldown_config['files'])
    if 'ticket' in categories:
        total_steps += 1
    if 'ocm' in categories and ocm_config.get('files'):
        total_steps += len(ocm_config['files'])
    
    # Initialiser le tracker de progression
    progress = ProgressTracker(total_steps, session_key="execution_progress")
    progress.reset()
    
    # Placeholders pour mise à jour en temps réel
    progress_placeholder = st.empty()
    log_placeholder = st.empty()
    
    # Résultats
    results = {
        'celldown': [],
        'ticket': None,
        'ocm': []
    }
    
    start_time = time.time()
    
    logger.info("=== Démarrage des traitements ===")
    
    current_step = 0
    
    # Exécuter CellDown (possiblement plusieurs fichiers)
    if 'celldown' in categories and celldown_config.get('files'):
        for file_config in celldown_config['files']:
            current_step += 1
            vendor = file_config.get('reference_name', 'CellDown')
            progress.update(current_step, f"Exécution de {vendor}...")
            
            # Mise à jour de la progression en temps réel
            progress_placeholder.markdown(f"🔄 **Progression** : {progress.get_percentage():.0f}% - {vendor}")
            
            service = CellDownService(logger)
            config = {**source_config, **file_config}
            
            success = service.execute(config)
            results['celldown'].append({'vendor': vendor, 'success': success})
            
            # Mise à jour des logs en temps réel
            with log_placeholder.container():
                st.markdown("#### 📄 Logs en temps réel")
                logger.render()
    
    # Exécuter Ticket
    if 'ticket' in categories:
        current_step += 1
        progress.update(current_step, "Exécution de Ticket...")
        
        # Mise à jour de la progression en temps réel
        progress_placeholder.markdown(f"🔄 **Progression** : {progress.get_percentage():.0f}% - Ticket")
        
        service = TicketService(logger)
        config = {**source_config, **ticket_config}
        
        success = service.execute(config)
        results['ticket'] = success
        
        # Mise à jour des logs en temps réel
        with log_placeholder.container():
            st.markdown("#### 📄 Logs en temps réel")
            logger.render()
    
    # Exécuter OCM RAN (possiblement plusieurs fichiers)
    if 'ocm' in categories and ocm_config.get('files'):
        for file_config in ocm_config['files']:
            current_step += 1
            time_label = file_config.get('result_column_name', 'OCM RAN')
            progress.update(current_step, f"Exécution de {time_label}...")
            
            # Mise à jour de la progression en temps réel
            progress_placeholder.markdown(f"🔄 **Progression** : {progress.get_percentage():.0f}% - {time_label}")
            
            service = OcmService(logger)
            config = {**source_config, **file_config}
            
            success = service.execute(config)
            results['ocm'].append({'label': time_label, 'success': success})
            
            # Mise à jour des logs en temps réel
            with log_placeholder.container():
                st.markdown("#### 📄 Logs en temps réel")
                logger.render()
    
    # Fin
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info(f"=== Traitements terminés en {duration:.1f}s ===")
    
    # Afficher les résultats finaux
    st.markdown("---")
    st.markdown("### ✅ Résultats")
    
    # Afficher les résultats par catégorie
    result_cols = []
    
    if 'celldown' in categories and results['celldown']:
        for result in results['celldown']:
            result_cols.append((result['vendor'], result['success']))
    
    if 'ticket' in categories:
        result_cols.append(('Ticket', results['ticket']))
    
    if 'ocm' in categories and results['ocm']:
        for result in results['ocm']:
            result_cols.append((result['label'], result['success']))
    
    # Afficher en colonnes
    if result_cols:
        cols = st.columns(len(result_cols))
        for idx, (label, success) in enumerate(result_cols):
            with cols[idx]:
                if success:
                    st.success(f"✅ {label}")
                else:
                    st.error(f"❌ {label}")
    
    # Afficher les logs finaux
    st.markdown("#### Logs d'exécution")
    logger.render()
    
    # Message de succès global
    all_success = all([
        all(r['success'] for r in results['celldown']) if results['celldown'] else True,
        results['ticket'] if 'ticket' in categories else True,
        all(r['success'] for r in results['ocm']) if results['ocm'] else True
    ])
    
    if all_success:
        st.balloons()
        st.success(f"🎉 Tous les traitements ont été exécutés avec succès en {duration:.1f}s !")
        st.info(f"📁 Le fichier source a été enrichi : {source_config['source_file_path']}")
        
        # Bouton de téléchargement du fichier Excel enrichi
        st.markdown("---")
        st.markdown("### 📥 Télécharger le résultat")
        
        source_file = Path(source_config['source_file_path'])
        if source_file.exists():
            with open(source_file, 'rb') as f:
                file_data = f.read()
            
            # Générer un nom de fichier avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{source_file.stem}_enrichi_{timestamp}{source_file.suffix}"
            
            st.download_button(
                label="📥 Télécharger le fichier Excel enrichi",
                data=file_data,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            st.caption(f"📝 Nom du fichier : {output_filename}")
        else:
            st.error("❌ Le fichier source est introuvable pour le téléchargement.")
    else:
        st.warning("⚠️ Certains traitements ont échoué. Consultez les logs pour plus de détails.")
