"""
Composant pour le panneau d'exécution des traitements
"""

import streamlit as st
from typing import Dict, List, Optional
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
                          ocm_config: Dict,
                          dashboard_celldown_config: Optional[Dict] = None,
                          hourly_ihs_config: Optional[Dict] = None,
                          personalized_xlookup_config: Optional[Dict] = None):
    """
    Affiche le panneau d'exécution avec le bouton principal et les résultats
    
    Args:
        source_config: Configuration de la source principale
        celldown_config: Configuration CellDown
        ticket_config: Configuration Ticket
        ocm_config: Configuration OCM RAN
        dashboard_celldown_config: Configuration Dashboard Celldown
        hourly_ihs_config: Configuration Hourly IHS
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
        
        # Dashboard Celldown
        if dashboard_celldown_config and dashboard_celldown_config.get('enabled'):
            st.success(f"✓ Dashboard Celldown : {dashboard_celldown_config.get('date_str', 'N/A')}")
            categories.append('dashboard_celldown')
        else:
            st.warning("⊘ Dashboard Celldown : non configuré")
        
        # Hourly IHS
        if hourly_ihs_config and hourly_ihs_config.get('enabled'):
            st.success(f"✓ Hourly IHS")
            categories.append('hourly_ihs')
        else:
            st.warning("⊘ Hourly IHS : non configuré")
        
        # Personalized XLOOKUP
        if personalized_xlookup_config and personalized_xlookup_config.get('enabled'):
            target_file = personalized_xlookup_config.get('target_file')
            file_name = target_file.name if target_file and hasattr(target_file, 'name') else 'N/A'
            st.success(f"✓ Personalized XLOOKUP : {file_name}")
            categories.append('personalized_xlookup')
        else:
            st.warning("⊘ Personalized XLOOKUP : non configuré")
    
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
        _execute_matches(source_config, celldown_config, ticket_config, ocm_config,
                        dashboard_celldown_config, hourly_ihs_config, personalized_xlookup_config, categories)


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
    else:
        st.info("Aucune correspondance trouvée")


def _execute_matches(source_config, celldown_config, ticket_config, ocm_config,
                    dashboard_celldown_config, hourly_ihs_config, personalized_xlookup_config, categories):
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
            "ocm_enabled": ocm_config.get('enabled') if ocm_config else False,
            "ocm_files_count": ocm_config.get('count', 0) if ocm_config else 0,
            "dashboard_celldown_enabled": dashboard_celldown_config.get('enabled') if dashboard_celldown_config else False,
            "hourly_ihs_enabled": hourly_ihs_config.get('enabled') if hourly_ihs_config else False
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
    if 'dashboard_celldown' in categories:
        total_steps += 1
    if 'hourly_ihs' in categories:
        total_steps += 1
    if 'personalized_xlookup' in categories:
        total_steps += 1
    
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
        'ocm': [],
        'dashboard_celldown': False,
        'hourly_ihs': False,
        'personalized_xlookup': False
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
    
    # Exécuter Dashboard Celldown
    if 'dashboard_celldown' in categories and dashboard_celldown_config and dashboard_celldown_config.get('enabled'):
        current_step += 1
        progress.update(current_step, "Exécution de Dashboard Celldown...")
        
        # Mise à jour de la progression en temps réel
        progress_placeholder.markdown(f"🔄 **Progression** : {progress.get_percentage():.0f}% - Dashboard Celldown")
        
        logger.info("🔵 Démarrage de Dashboard Celldown")
        
        try:
            # Importer la classe DashboardCelldown
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from dashboard_celldown import DashboardCelldown
            
            # Construire la configuration
            dashboard = DashboardCelldown(
                source_file_path=source_config['source_file_path'],
                target_file_path=dashboard_celldown_config['target_file_path'],
                colown_key_path_source=dashboard_celldown_config['source_key_column'],
                target_key_column=dashboard_celldown_config['target_key_column'],
                target_value_column=dashboard_celldown_config['target_value_column'],
                result_position_column=dashboard_celldown_config['start_column'],
                source_sheet_path=source_config.get('source_sheet_path', ''),
                target_sheet_name=dashboard_celldown_config.get('target_sheet_name'),
                date_str=dashboard_celldown_config['date_str'],
                start_column=dashboard_celldown_config['start_column'],
                reference_date=dashboard_celldown_config.get('reference_date', '')
            )
            
            # Exécuter
            dashboard.super_xlookup_par_date()
            
            logger.success("✅ Dashboard Celldown terminé avec succès")
            results['dashboard_celldown'] = True
            
        except Exception as e:
            logger.error(f"❌ Erreur Dashboard Celldown : {e}")
            results['dashboard_celldown'] = False
        
        # Mise à jour des logs en temps réel
        with log_placeholder.container():
            st.markdown("#### 📄 Logs en temps réel")
            logger.render()
    
    # Exécuter Hourly IHS
    if 'hourly_ihs' in categories and hourly_ihs_config and hourly_ihs_config.get('enabled'):
        current_step += 1
        progress.update(current_step, "Exécution de Hourly IHS...")
        
        # Mise à jour de la progression en temps réel
        progress_placeholder.markdown(f"🔄 **Progression** : {progress.get_percentage():.0f}% - Hourly IHS")
        
        logger.info("🔵 Démarrage de Hourly IHS")
        
        try:
            # Importer la classe HourlyIHS
            import sys
            import traceback
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from hourly_IHS import HourlyIHS
            
            # DEBUG: Afficher les configurations avant l'exécution
            logger.info(f"📋 Config source_file_path: {source_config['source_file_path']}")
            logger.info(f"📋 Config target_file_path: {hourly_ihs_config['target_file_path']}")
            logger.info(f"📋 Config source_sheet: {source_config.get('source_sheet_path', '')}")
            logger.info(f"📋 Config target_sheet: {hourly_ihs_config.get('target_sheet_name', '')}")
            logger.info(f"📋 Config source_key_column: {hourly_ihs_config['source_key_column']}")
            logger.info(f"📋 Config target_key_column: {hourly_ihs_config.get('target_key_column')}")
            
            # Construire la configuration
            hourly = HourlyIHS(
                source_file_path=source_config['source_file_path'],
                target_file_path=hourly_ihs_config['target_file_path'],
                source_key_column=hourly_ihs_config['source_key_column'],
                result_position_column=hourly_ihs_config['result_position_column'],
                result_column_name=hourly_ihs_config['result_column_name'],
                source_sheet_name=source_config.get('source_sheet_path', ''),  # Utiliser la feuille source principale
                target_sheet_name=hourly_ihs_config.get('target_sheet_name', ''),
                reference_name=hourly_ihs_config['reference_name'],
                reference_date=hourly_ihs_config.get('reference_date'),
                target_join_columns=hourly_ihs_config.get('target_join_columns'),
                join_separator=hourly_ihs_config.get('join_separator', ' .. '),
                ignore_empty=hourly_ihs_config.get('ignore_empty', True),
                target_key_column=hourly_ihs_config.get('target_key_column')
            )
            
            logger.info("🔄 Lancement de l'exécution Hourly IHS...")
            # Exécuter
            hourly.run()
            
            logger.success("✅ Hourly IHS terminé avec succès")
            results['hourly_ihs'] = True
            
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"❌ Erreur Hourly IHS : {e}")
            logger.error(f"📝 Détails de l'erreur :\n{error_trace}")
            results['hourly_ihs'] = False
        
        # Mise à jour des logs en temps réel
        with log_placeholder.container():
            st.markdown("#### 📄 Logs en temps réel")
            logger.render()
    
    # Exécuter Personalized XLOOKUP
    if 'personalized_xlookup' in categories and personalized_xlookup_config and personalized_xlookup_config.get('enabled'):
        current_step += 1
        progress.update(current_step, "Exécution de Personalized XLOOKUP...")
        
        # Mise à jour de la progression en temps réel
        progress_placeholder.markdown(f"🔄 **Progression** : {progress.get_percentage():.0f}% - Personalized XLOOKUP")
        
        logger.info("🔵 Démarrage de Personalized XLOOKUP")
        
        try:
            # Importer la classe PersonnalizedXlookup
            import sys
            import traceback
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from personnalized import PersonnalizedXlookup
            
            # Sauvegarder le fichier target uploadé temporairement
            import tempfile
            import os
            target_file_obj = personalized_xlookup_config.get('target_file')
            
            if target_file_obj:
                # Réinitialiser le curseur du fichier uploadé au début
                target_file_obj.seek(0)
                
                # Créer un fichier temporaire et écrire le contenu
                temp_target_path = None
                file_creation_success = False
                
                try:
                    # Lire le contenu du fichier uploadé
                    file_content = target_file_obj.read()
                    
                    # Créer un fichier temporaire
                    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xlsx') as tmp_file:
                        tmp_file.write(file_content)
                        temp_target_path = tmp_file.name
                    
                    # Vérifier que le fichier a bien été créé
                    if not os.path.exists(temp_target_path):
                        raise FileNotFoundError(f"Le fichier temporaire {temp_target_path} n'a pas été créé")
                    
                    file_creation_success = True
                    logger.info(f"📋 Fichier cible temporaire créé: {temp_target_path}")
                    logger.info(f"📋 Taille du fichier: {os.path.getsize(temp_target_path)} bytes")
                    
                except Exception as file_error:
                    logger.error(f"❌ Erreur lors de la création du fichier temporaire: {file_error}")
                    results['personalized_xlookup'] = False
                    file_creation_success = False
                
                if file_creation_success and temp_target_path:
                    logger.info(f"📋 Config source_file_path: {source_config['source_file_path']}")
                    logger.info(f"📋 Config target_sheet_name: {personalized_xlookup_config.get('target_sheet_name', '')}")
                    logger.info(f"📋 Config result_column_name: {personalized_xlookup_config.get('result_column_name')}")
                    logger.info(f"📋 Config reference_name: {personalized_xlookup_config.get('reference_name')}")
                    
                    # Préparer les colonnes join
                    join_columns = personalized_xlookup_config.get('join_columns')
                    if join_columns and len(join_columns) > 0:
                        logger.info(f"📋 Colonnes TEXTJOIN: {join_columns}")
                        target_join_columns = join_columns
                        target_value_column = None
                    else:
                        logger.info("📋 Pas de colonnes TEXTJOIN spécifiées")
                        target_join_columns = None
                        target_value_column = None
                    
                    # Préparer les préfixes d'extraction
                    extract_prefixes = personalized_xlookup_config.get('extract_prefixes', ['ABC'])
                    
                    # Construire la configuration
                    personalized = PersonnalizedXlookup(
                        source_file_path=source_config['source_file_path'],
                        target_file_path=temp_target_path,
                        source_key_column=["code site", "site code", "site id"],  # Par défaut
                        result_position_column=personalized_xlookup_config.get('result_position', 'last_free'),
                        result_column_name=personalized_xlookup_config.get('result_column_name'),
                        source_sheet_name=source_config.get('source_sheet_path', ''),
                        target_sheet_name=personalized_xlookup_config.get('target_sheet_name', ''),
                        reference_name=personalized_xlookup_config.get('reference_name', ''),
                        reference_date=None,  # Date du jour par défaut
                        target_value_column=target_value_column,
                        target_join_columns=target_join_columns,
                        join_separator=personalized_xlookup_config.get('join_separator', ' .. '),
                        ignore_empty=True,
                        target_key_column=None,  # Auto-détection
                        extract_source_column=personalized_xlookup_config.get('extract_column'),
                        extract_prefixes=extract_prefixes
                    )
                    
                    logger.info("🔄 Lancement de l'exécution Personalized XLOOKUP...")
                    # Exécuter
                    personalized.run()
                    
                    # Nettoyer le fichier temporaire
                    try:
                        os.unlink(temp_target_path)
                        logger.info(f"🗑️ Fichier temporaire supprimé: {temp_target_path}")
                    except:
                        pass
                    
                    logger.success("✅ Personalized XLOOKUP terminé avec succès")
                    results['personalized_xlookup'] = True
            else:
                logger.error("❌ Aucun fichier cible fourni")
                results['personalized_xlookup'] = False
            
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"❌ Erreur Personalized XLOOKUP : {e}")
            logger.error(f"📝 Détails de l'erreur :\n{error_trace}")
            results['personalized_xlookup'] = False
        
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
    
    if 'dashboard_celldown' in categories:
        result_cols.append(('Dashboard Celldown', results.get('dashboard_celldown', False)))
    
    if 'hourly_ihs' in categories:
        result_cols.append(('Hourly IHS', results.get('hourly_ihs', False)))
    
    if 'personalized_xlookup' in categories:
        result_cols.append(('Personalized XLOOKUP', results.get('personalized_xlookup', False)))
    
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
