"""
Système de logging pour l'application
Gère les logs en temps réel avec timestamps et niveaux
"""

import streamlit as st
from datetime import datetime
from typing import Literal, List, Dict
from dataclasses import dataclass, field


LogLevel = Literal["info", "success", "warning", "error"]


@dataclass
class LogEntry:
    """Entrée de log avec timestamp, niveau et message"""
    timestamp: str
    level: LogLevel
    message: str


class Logger:
    """Gestionnaire de logs pour l'interface Streamlit"""
    
    def __init__(self, session_key: str = "app_logs"):
        self.session_key = session_key
        
        # Initialiser les logs dans la session
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = []
    
    def _add_log(self, level: LogLevel, message: str):
        """Ajoute une entrée de log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = LogEntry(timestamp=timestamp, level=level, message=message)
        st.session_state[self.session_key].append(entry)
    
    def info(self, message: str):
        """Log de niveau INFO"""
        self._add_log("info", message)
    
    def success(self, message: str):
        """Log de niveau SUCCESS"""
        self._add_log("success", message)
    
    def warning(self, message: str):
        """Log de niveau WARNING"""
        self._add_log("warning", message)
    
    def error(self, message: str):
        """Log de niveau ERROR"""
        self._add_log("error", message)
    
    def get_logs(self) -> List[LogEntry]:
        """Retourne tous les logs"""
        return st.session_state.get(self.session_key, [])
    
    def clear(self):
        """Efface tous les logs"""
        st.session_state[self.session_key] = []
    
    def render(self, max_entries: int = 50):
        """Affiche les logs dans une console stylisée"""
        logs = self.get_logs()[-max_entries:]  # Limite au nombre max d'entrées
        
        if not logs:
            st.info("Aucun log disponible")
            return
        
        # Générer le HTML de la console
        log_html = '<div class="log-console">'
        
        for log in logs:
            # Choisir la classe CSS selon le niveau
            level_class = f"log-{log.level}"
            
            # Icône selon le niveau
            icons = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌"
            }
            icon = icons.get(log.level, "•")
            
            log_html += f'''
            <div class="log-entry">
                <span class="log-time">[{log.timestamp}]</span>
                <span>{icon}</span>
                <span class="{level_class}">{log.message}</span>
            </div>
            '''
        
        log_html += '</div>'
        
        st.markdown(log_html, unsafe_allow_html=True)


class ProgressTracker:
    """Tracker de progression pour les traitements"""
    
    def __init__(self, total_steps: int, session_key: str = "progress"):
        self.total_steps = total_steps
        self.session_key = session_key
        self.current_step = 0
        
        # Initialiser dans la session
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                "current": 0,
                "total": total_steps,
                "message": ""
            }
    
    def update(self, step: int, message: str = ""):
        """Met à jour la progression"""
        self.current_step = min(step, self.total_steps)
        st.session_state[self.session_key] = {
            "current": self.current_step,
            "total": self.total_steps,
            "message": message
        }
    
    def increment(self, message: str = ""):
        """Incrémente la progression d'un pas"""
        self.update(self.current_step + 1, message)
    
    def get_progress(self) -> Dict:
        """Retourne l'état actuel de la progression"""
        return st.session_state.get(self.session_key, {
            "current": 0,
            "total": self.total_steps,
            "message": ""
        })
    
    def get_percentage(self) -> float:
        """Retourne le pourcentage de progression"""
        progress = self.get_progress()
        if progress["total"] == 0:
            return 0.0
        return (progress["current"] / progress["total"]) * 100
    
    def render(self):
        """Affiche la barre de progression stylisée"""
        progress = self.get_progress()
        percentage = self.get_percentage()
        
        # HTML de la barre de progression
        progress_html = f'''
        <div class="custom-progress">
            <div class="custom-progress-bar" style="width: {percentage}%">
                {int(percentage)}%
            </div>
        </div>
        '''
        
        st.markdown(progress_html, unsafe_allow_html=True)
        
        if progress["message"]:
            st.caption(progress["message"])
    
    def reset(self):
        """Réinitialise la progression"""
        self.current_step = 0
        st.session_state[self.session_key] = {
            "current": 0,
            "total": self.total_steps,
            "message": ""
        }


def format_duration(seconds: float) -> str:
    """Formate une durée en secondes en format lisible"""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"


def format_file_size(bytes: int) -> str:
    """Formate une taille de fichier en format lisible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"
