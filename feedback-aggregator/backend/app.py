import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Union, Optional, Dict, Any

import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Configuration logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ajout du chemin automate
backend_path = Path(__file__).resolve().parent
project_root = backend_path.parent.parent
automate_path = project_root / "automate"
sys.path.insert(0, str(automate_path))

from celldown import CellDown
from super_xlookup import SuperXlookup
from ticket import Ticket

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
PERSISTENCE_FILE = UPLOAD_FOLDER / ".main_file_path.txt"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 Mo
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

_main_file_path: Optional[str] = None

# ----------------------------------------------------------------------
# Fonctions utilitaires
# ----------------------------------------------------------------------


def load_main_file_path() -> bool:
    global _main_file_path
    if PERSISTENCE_FILE.exists():
        path = PERSISTENCE_FILE.read_text().strip()
        if path and Path(path).exists():
            _main_file_path = path
            logger.info(f"Fichier principal restauré: {_main_file_path}")
            return True
    return False


def save_main_file_path() -> None:
    if _main_file_path:
        PERSISTENCE_FILE.write_text(_main_file_path)


def parse_column_param(
    param: Union[str, List[str], None],
) -> Union[str, List[str], None]:
    if param is None:
        return None
    if isinstance(param, list):
        return param
    if isinstance(param, str):
        if "," in param:
            return [p.strip() for p in param.split(",")]
        return param
    return param


def save_uploaded_file(file, prefix: str = "upload") -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}_{file.filename}"
    file_path = UPLOAD_FOLDER / filename
    file.save(str(file_path))
    return file_path


def copy_main_file_for_processing(suffix: str = "processed") -> Path:
    if not _main_file_path or not os.path.exists(_main_file_path):
        raise FileNotFoundError("Fichier principal introuvable")
    timestamp = (
        datetime.now().strftime("%Y%m%d_%H%M%S")
        + f"_{int(time.time() * 1000000) % 1000000}"
    )
    processed_file = UPLOAD_FOLDER / f"{suffix}_{timestamp}.xlsx"
    shutil.copy(_main_file_path, processed_file)
    return processed_file


def jsonify_dataframe(df: pd.DataFrame, max_rows: int = 100) -> Dict[str, Any]:
    df_clean = df.fillna("")
    return {
        "lines": len(df_clean),
        "columns": list(df_clean.columns),
        "data": df_clean.head(max_rows).to_dict("records"),
    }


def validate_required_fields(data: Dict, required: List[str]) -> None:
    """Lève une exception si un champ requis est manquant."""
    missing = [f for f in required if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"Champ(s) requis manquant(s): {', '.join(missing)}")


# ----------------------------------------------------------------------
# Routes API
# ----------------------------------------------------------------------


@app.route("/api/health", methods=["GET"])
def health():
    """GET /api/health - Vérifie l'état du backend."""
    print(f"❤️ [health] Backend health check appelé")
    return jsonify({"status": "ok", "message": "Backend is running"})


@app.route("/api/upload-main-file", methods=["POST"])
def upload_main_file():
    """
    POST /api/upload-main-file
    Content-Type: multipart/form-data
    Paramètres requis:
        - file (fichier Excel) : fichier principal à utiliser
    Paramètres optionnels:
        - sheet_name (str) : nom de la feuille Excel à utiliser (par défaut : première feuille)
    Réponse: JSON avec succès, filename, sheet_name utilisé, lignes, taille, etc.
    """
    print(f"🚀 [upload-main-file] Début de la requête")
    print(f"📦 [upload-main-file] Files dans request: {list(request.files.keys())}")
    print(f"📝 [upload-main-file] Form data: {dict(request.form)}")
    
    if "file" not in request.files:
        print(f"❌ [upload-main-file] Champ 'file' manquant")
        return jsonify({"error": "Missing required field: file"}), 400

    file = request.files["file"]
    print(f"📄 [upload-main-file] Fichier reçu: {file.filename}")
    
    if file.filename == "":
        print(f"❌ [upload-main-file] Nom de fichier vide")
        return jsonify({"error": "Empty filename"}), 400

    # Récupérer le nom de la feuille depuis le formulaire (optionnel)
    sheet_name = request.form.get("sheet_name")
    # Si non fourni, utiliser la première feuille (0)
    if sheet_name is None:
        sheet_name = 0
    
    print(f"📊 [upload-main-file] Sheet name: {sheet_name}")

    try:
        file_path = save_uploaded_file(file, prefix="main")
        print(f"💾 [upload-main-file] Fichier sauvegardé: {file_path}")
        
        # Lire un aperçu (5 premières lignes) pour valider
        print(f"🔍 [upload-main-file] Lecture de l'aperçu...")
        df_preview = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
        print(f"✅ [upload-main-file] Aperçu lu: {len(df_preview)} lignes")
        
        # Compter le nombre total de lignes (peut être lourd sur gros fichiers)
        # Alternative : utiliser openpyxl ou lire le fichier une seule fois
        print(f"📊 [upload-main-file] Lecture complète du fichier...")
        df_full = pd.read_excel(file_path, sheet_name=sheet_name)
        lines = len(df_full)
        size = os.path.getsize(file_path)
        print(f"✅ [upload-main-file] Fichier complet: {lines} lignes, {size} bytes")

        global _main_file_path
        _main_file_path = str(file_path)
        save_main_file_path()
        print(f"✅ [upload-main-file] _main_file_path défini: {_main_file_path}")

        response_data = {
            "success": True,
            "filename": file.filename,
            "sheet_name": str(sheet_name) if sheet_name != 0 else "0",  # pour information
            "path": str(file_path),
            "lines": lines,
            "size": size,
        }
        print(f"✅ [upload-main-file] Réponse prête: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        print(f"❌ [upload-main-file] ERREUR: {type(e).__name__}: {str(e)}")
        logger.exception("Erreur upload main file")
        return jsonify({"error": str(e)}), 500


@app.route("/api/clear-main-file", methods=["DELETE"])
def clear_main_file():
    """DELETE /api/clear-main-file - Supprime la référence au fichier principal."""
    global _main_file_path
    _main_file_path = None
    if PERSISTENCE_FILE.exists():
        PERSISTENCE_FILE.unlink()
    return jsonify({"success": True, "message": "Main file cleared"})


@app.route("/api/process-celldown", methods=["POST"])
def process_celldown():
    global _main_file_path
    if not _main_file_path:
        return jsonify({
            "status": "error",
            "message": "Main file not uploaded. Please upload a main file first."
        }), 400

    if "file" not in request.files:
        return jsonify({
            "status": "error",
            "message": "Missing required field: file"
        }), 400

    file = request.files["file"]
    data = request.form

    # Sauvegarde
    try:
        target_path = save_uploaded_file(file, prefix="target")
    except Exception as e:
        logger.exception("save_uploaded_file")
        return jsonify({
            "status": "error",
            "message": f"Failed to save target file: {str(e)}"
        }), 500

    try:
        processed_file = copy_main_file_for_processing("celldown")
    except Exception as e:
        logger.exception("copy_main_file_for_processing")
        return jsonify({
            "status": "error",
            "message": f"Failed to copy main file: {str(e)}"
        }), 500

    # Paramètres
    try:
        reference_name = data.get("reference_name", "")
        reference_date = data.get("reference_date", "")
        date_str = data.get("date_str", "")
        colown_key_path_source = parse_column_param(data.get("colown_key_path_source", "Codesite"))
        target_key_column = parse_column_param(data.get("target_key_column", "Site Code,SITE_CODE,site code,Code Site"))
        target_value_column = parse_column_param(data.get("target_value_column", "Comment,COMMENT,comment"))
        source_sheet_path = data.get("source_sheet_path", "Sheet1")
        start_column = data.get("start_column", "last_column")
    except Exception as e:
        logger.exception("parse_column_param")
        return jsonify({
            "status": "error",
            "message": f"Parameter parsing error: {str(e)}"
        }), 400

    # Vérification des colonnes
    try:
        df_source = pd.read_excel(processed_file, sheet_name=source_sheet_path, nrows=0)
        if isinstance(colown_key_path_source, list):
            found = any(col in df_source.columns for col in colown_key_path_source)
            if not found:
                logger.warning(f"Aucune des colonnes source {colown_key_path_source} trouvée")
        elif colown_key_path_source not in df_source.columns:
            logger.warning(f"Colonne source '{colown_key_path_source}' introuvable")
    except Exception as e:
        logger.exception("read_excel for column check")
        return jsonify({
            "status": "error",
            "message": f"Failed to read source sheet: {str(e)}"
        }), 500

    # CellDown
    try:
        celldown = CellDown(
            source_file_path=str(processed_file),
            target_file_path=str(target_path),
            colown_key_path_source=colown_key_path_source,
            target_key_column=target_key_column,
            target_value_column=target_value_column,
            result_position_column="last_column",
            source_sheet_path=source_sheet_path,
            date_str=date_str,
            start_column=start_column,
            reference_name=reference_name,
        )
        celldown.super_xlookup_par_date()
    except Exception as e:
        logger.exception("CellDown processing")
        return jsonify({
            "status": "error",
            "message": f"CellDown processing failed: {str(e)}"
        }), 500

    # Mise à jour du chemin
    try:
        _main_file_path = str(processed_file)
        save_main_file_path()
    except Exception as e:
        logger.exception("save_main_file_path")
        return jsonify({
            "status": "error",
            "message": f"Failed to update main file path: {str(e)}"
        }), 500

    # Réponse finale
    try:
        df_result = pd.read_excel(processed_file, sheet_name=source_sheet_path)
        response = jsonify_dataframe(df_result)
        response["status"] = "success"
        response["message"] = "CellDown processed successfully"
        response["filename"] = file.filename
        return jsonify(response)
    except Exception as e:
        logger.exception("jsonify_dataframe")
        return jsonify({
            "status": "error",
            "message": f"Failed to generate response: {str(e)}"
        }), 500

@app.route("/api/process-xlookup", methods=["POST"])
def process_xlookup():
    """
    POST /api/process-xlookup
    Content-Type: multipart/form-data
    Paramètres requis:
        - file (fichier Excel) : fichier cible
    Paramètres optionnels:
        - source_key_column (str/ liste) : défaut "Codesite"
        - target_key_column (str/ liste) : défaut "Site ID,SITE_ID,site id"
        - target_value_column (str/ liste) : défaut "Actions en cours,Actions"
        - source_sheet_name (str) : défaut "Sheet1"
        - target_sheet_name (str) : défaut "" (première feuille)
        - result_column_name (str) : défaut = nom du fichier cible (sans extension)
        - reference_name (str) : défaut "" (pas de préfixe)
        - reference_date (str) : défaut "" (utilise date du jour)
        - result_position_column (str) : défaut "last_column"
    """
    global _main_file_path
    if not _main_file_path:
        return jsonify({"error": "Main file not uploaded"}), 400

    if "file" not in request.files:
        return jsonify({"error": "Missing required field: file"}), 400

    file = request.files["file"]
    data = request.form

    try:
        target_path = save_uploaded_file(file, prefix="target")
        processed_file = copy_main_file_for_processing("xlookup")

        source_key_column = parse_column_param(
            data.get("source_key_column", "Codesite")
        )
        target_key_column = parse_column_param(
            data.get("target_key_column", "Site ID,SITE_ID,site id")
        )
        target_value_column = parse_column_param(
            data.get("target_value_column", "Actions en cours,Actions")
        )
        source_sheet_name = data.get("source_sheet_name", "Sheet1")
        target_sheet_name = data.get("target_sheet_name", "")
        result_column_name = data.get("result_column_name", "")
        reference_name = data.get("reference_name", "")
        reference_date = data.get("reference_date", "")
        result_position_column = data.get("result_position_column", "last_column")

        # Si aucun nom de colonne résultat fourni, utiliser le nom du fichier cible (sans extension)
        if not result_column_name:
            result_column_name = Path(file.filename).stem

        xlookup = SuperXlookup(
            source_file_path=str(processed_file),
            target_file_path=str(target_path),
            source_key_column=source_key_column,
            target_key_column=target_key_column,
            target_value_column=target_value_column,
            result_position_column=result_position_column,
            result_column_name=result_column_name,
            source_sheet_name=source_sheet_name,
            target_sheet_name=target_sheet_name,
            reference_name=reference_name,
            reference_date=reference_date,
        )
        xlookup.run()

        _main_file_path = str(processed_file)
        save_main_file_path()

        df_result = pd.read_excel(processed_file, sheet_name=source_sheet_name)
        response = jsonify_dataframe(df_result)
        response["success"] = True
        response["message"] = "SuperXlookup processed successfully"
        response["filename"] = file.filename
        return jsonify(response)

    except Exception as e:
        logger.exception("Erreur process_xlookup")
        return jsonify({"error": str(e)}), 500


import json  # à ajouter en haut du fichier si ce n'est pas déjà fait

@app.route('/api/process-ticket', methods=['POST'])
def process_ticket():
    """
    POST /api/process-ticket
    Content-Type: multipart/form-data
    Paramètres requis:
        - file (fichier Excel) : fichier cible
    Paramètres optionnels:
        - reference_name (str) : défaut "Ticket"
        - reference_date (str) : défaut date du jour (format DD/MM/YYYY) – laisser vide pour auto
        - source_key_column (str ou JSON list) : défaut "Codesite"
        - target_key_column (str, JSON list ou null) : défaut None (extraction auto via extract_source_column)
        - source_sheet_name (str) : défaut "Sheet1"
        - target_sheet_name (str) : défaut "" (première feuille)
        - result_column_name (str) : défaut "Ticket"
        - target_join_columns (JSON) : liste de listes de colonnes, défaut [["Ticket ID"],["Description"],["Solution"],["Root Cause"],["Incident Reason"]]
        - join_separator (str) : défaut ".."
        - ignore_empty (bool) : "true" ou "false", défaut "true"
        - extract_source_column (JSON list) : liste de noms de colonnes pour extraire la clé cible, défaut None
    """
    global _main_file_path
    if not _main_file_path:
        return jsonify({"error": "Main file not uploaded"}), 400
    
    if 'file' not in request.files:
        return jsonify({"error": "Missing required field: file"}), 400
    
    file = request.files['file']
    data = request.form
    
    try:
        target_path = save_uploaded_file(file, prefix="target")
        processed_file = copy_main_file_for_processing("ticket")
        
        # Paramètres simples
        reference_name = data.get('reference_name', 'Ticket')
        reference_date_str = data.get('reference_date', '')
        source_sheet_name = data.get('source_sheet_name', 'Sheet1')
        target_sheet_name = data.get('target_sheet_name', '')
        result_column_name = data.get('result_column_name', 'Ticket')
        join_separator = data.get('join_separator', '..')
        ignore_empty = data.get('ignore_empty', 'true').lower() == 'true'
        
        # reference_date : si vide, None (la classe utilisera datetime.now())
        reference_date = reference_date_str if reference_date_str else None
        
        # source_key_column : peut être une chaîne ou une liste JSON
        source_key_raw = data.get('source_key_column', 'Codesite')
        try:
            source_key_column = json.loads(source_key_raw) if source_key_raw.strip().startswith('[') else source_key_raw
        except:
            source_key_column = source_key_raw
        
        # target_key_column : peut être None, chaîne ou liste JSON
        target_key_raw = data.get('target_key_column')
        if target_key_raw is None or target_key_raw == '':
            target_key_column = None
        else:
            try:
                target_key_column = json.loads(target_key_raw) if target_key_raw.strip().startswith('[') else target_key_raw
            except:
                target_key_column = target_key_raw
        
        # target_join_columns : JSON attendu (liste de listes)
        join_cols_raw = data.get('target_join_columns')
        if join_cols_raw:
            try:
                target_join_columns = json.loads(join_cols_raw)
                # Normalisation : chaque élément devient une liste (pour gérer les alias multiples)
                target_join_columns = [
                    [col] if isinstance(col, str) else col 
                    for col in target_join_columns
                ]
            except:
                # Fallback : interpréter comme une liste simple séparée par des virgules
                items = [item.strip() for item in join_cols_raw.split(',')]
                target_join_columns = [[item] for item in items]
        else:
            # Valeur par défaut : 5 colonnes, chacune avec un seul nom
            target_join_columns = [
                ["Ticket ID(Create TT)"],
                ["Description(Process TT)"],
                ["Solution(Process TT)"],
                ["Root Cause(Process TT)"],
                ["Incident Reason Detail(Process TT)"]
            ]
        
        # extract_source_column : JSON list attendue
        extract_raw = data.get('extract_source_column')
        if extract_raw:
            try:
                extract_source_column = json.loads(extract_raw)
                if isinstance(extract_source_column, str):
                    extract_source_column = [extract_source_column]
            except:
                extract_source_column = [extract_raw]
        else:
            extract_source_column = None
        
        # Instanciation de Ticket
        ticket = Ticket(
            source_file_path=str(processed_file),
            target_file_path=str(target_path),
            source_key_column=source_key_column,
            target_key_column=target_key_column,
            result_position_column="last_column",
            result_column_name=result_column_name,
            source_sheet_name=source_sheet_name,
            target_sheet_name=target_sheet_name,
            reference_name=reference_name,
            reference_date=reference_date,
            target_join_columns=target_join_columns,
            join_separator=join_separator,
            ignore_empty=ignore_empty,
            extract_source_column=extract_source_column
        )
        ticket.run()
        
        _main_file_path = str(processed_file)
        save_main_file_path()
        
        df_result = pd.read_excel(processed_file, sheet_name=source_sheet_name)
        response = jsonify_dataframe(df_result)
        response["success"] = True
        response["message"] = "Ticket processed successfully"
        response["filename"] = file.filename
        return jsonify(response)
        
    except Exception as e:
        logger.exception("Erreur process_ticket")
        return jsonify({"error": str(e)}), 500


@app.route("/api/get-data", methods=["GET"])
def get_data():
    """
    GET /api/get-data
    Réponse: { "success": true, "file_exists": true/false, "message": "...", "file_path": "..." }
    """
    if not _main_file_path:
        return jsonify({
            "success": False,
            "file_exists": False,
            "message": "Aucun fichier n'a encore été sauvegardé",
            "file_path": None
        }), 200

    file_exists = os.path.exists(_main_file_path)
    return jsonify({
        "success": file_exists,
        "file_exists": file_exists,
        "message": "Fichier sauvegardé" if file_exists else "Fichier non trouvé",
        "file_path": _main_file_path if file_exists else None
    }), 200


@app.route("/api/export", methods=["GET"])
def export_file():
    """
    GET /api/export
    Télécharge le fichier principal courant (sans paramètres).
    """
    if not _main_file_path or not os.path.exists(_main_file_path):
        return jsonify({"error": "No file to export"}), 400

    return send_file(
        _main_file_path,
        as_attachment=True,
        download_name=f"consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
    )


# Nettoyage initial
def cleanup_old_files(days: int = 7):
    now = time.time()
    for file_path in UPLOAD_FOLDER.glob("*"):
        if file_path.is_file() and file_path != PERSISTENCE_FILE:
            if now - file_path.stat().st_mtime > days * 86400:
                try:
                    file_path.unlink()
                except Exception:
                    pass


cleanup_old_files(days=7)
load_main_file_path()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
