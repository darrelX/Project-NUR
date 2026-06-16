from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
import pandas as pd
import traceback
from werkzeug.utils import secure_filename
import msvcrt


# Ajouter le dossier 'compilation tool' au path Python
sys.path.insert(0, str(Path(__file__).parent.parent / 'compilation tool'))

from automate.celldown import CellDown
from automate.super_xlookup import SuperXlookup
from excel_analyzer import ExcelAnalyzer

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin depuis React

# Dossier pour les fichiers uploadés
UPLOAD_FOLDER = Path(__file__).parent.parent / 'inputs'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Extensions autorisées
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifie que le serveur fonctionne"""
    return jsonify({'status': 'ok', 'message': 'Backend is running'})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload un fichier Excel dans le dossier inputs"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        
        if file.filename == '' or file.filename is None:
            return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Type de fichier non autorisé'}), 400
        
        filename = secure_filename(file.filename)
        file_path = UPLOAD_FOLDER / filename
        file.save(str(file_path))
        
        # Convertir le chemin Windows en format standard (forward slashes)
        file_path_str = str(file_path).replace('\\', '/')
        
        print(f"✅ Fichier uploadé: {filename}")
        print(f"📁 Chemin complet: {file_path_str}")
        
        return jsonify({
            'success': True,
            'message': f'Fichier {filename} uploadé avec succès',
            'filename': filename,
            'filePath': file_path_str
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    """Liste tous les fichiers Excel disponibles"""
    try:
        files = []
        for idx, file_path in enumerate(UPLOAD_FOLDER.glob('*.xlsx'), start=1):
            # Lire les feuilles du fichier
            try:
                excel_file = pd.ExcelFile(file_path)
                sheets = excel_file.sheet_names
            except:
                sheets = []
            
            files.append({
                'id': idx,
                'name': file_path.name,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'sheets': sheets
            })
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/columns', methods=['POST'])
def get_file_columns():
    """Récupère les colonnes d'une feuille Excel"""
    try:
        data = request.json
        file_path = data.get('filePath')
        sheet_name = data.get('sheetName', 0)
        
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Retourner les colonnes avec leur index
        columns = []
        for idx, col in enumerate(df.columns):
            letter = _index_to_col_letter(idx)
            columns.append({
                'index': idx,
                'letter': letter,
                'name': str(col),
                'label': f"{letter} - {col}"
            })
        
        return jsonify({'columns': columns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/sheets', methods=['POST'])
def get_file_sheets():
    """Récupère les feuilles détectées dans un fichier (avec dates éventuelles)"""
    try:
        data = request.json
        file_path = data.get('filePath')
        
        excel_file = pd.ExcelFile(file_path)
        sheets = []
        
        for sheet_name in excel_file.sheet_names:
            # Essayer de détecter des dates dans le nom de la feuille
            sheets.append({
                'name': sheet_name,
                'hasDate': any(char.isdigit() for char in sheet_name)
            })
        
        return jsonify({'sheets': sheets})
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/file/preview', methods=['POST'])
def preview_file():
    """Affiche un aperçu des données d'un fichier"""
    try:
        data = request.json
        file_path = data.get('filePath')
        sheet_name = data.get('sheetName', 0)
        max_rows = data.get('maxRows', 10)
        
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Limiter le nombre de lignes
        preview_df = df.head(max_rows)
        
        return jsonify({
            'columns': list(df.columns),
            'data': preview_df.to_dict('records'),
            'totalRows': len(df)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== NOUVEAUX ENDPOINTS D'ANALYSE ====================



@app.route('/api/analyze', methods=['POST'])
def analyze_file():
    """Analyse complète d'un fichier Excel avec détection de fichier ouvert"""
    try:
        # 1. Récupération du chemin
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée JSON fournie'}), 400

        file_path = data.get('filePath')
        if not file_path:
            return jsonify({'error': 'Paramètre filePath manquant'}), 400

        # 2. Vérification existence du fichier
        if not Path(file_path).exists():
            return jsonify({'error': f'Fichier introuvable: {file_path}'}), 404

        print(f"📊 Analyse du fichier: {file_path}")

        # 3. Vérifier si le fichier est déjà ouvert (Windows)
        try:
            with open(file_path, 'r+b') as f:
                # Tentative de verrouillage non-bloquant d'un petit segment
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except (OSError, IOError) as e:
            if e.errno == 13:  # Permission denied → fichier ouvert
                return jsonify({
                    'error': 'Le fichier est actuellement ouvert dans Excel (ou un autre programme). Fermez-le et réessayez.'
                }), 409
            # Autre erreur système → on la propage
            return jsonify({'error': f'Erreur d\'accès au fichier: {str(e)}'}), 500

        # 4. Analyse du fichier (lecture seule)
        try:
            metadata = ExcelAnalyzer.analyze_file(file_path)
        except Exception as e:
            print(f"❌ Erreur d'analyse détaillée: {traceback.format_exc()}")
            return jsonify({
                'error': 'Impossible d\'analyser le fichier : types de données incompatibles. Vérifiez les noms des feuilles ou des colonnes.'
            }), 400

        # 5. Ajouter les issues détectées pour la première feuille
        if metadata.get('sheets'):
            try:
                issues = ExcelAnalyzer.detect_issues(file_path, metadata['sheets'][0])
                metadata['issues'] = issues
            except Exception as e:
                print(f"⚠️ Erreur lors de la détection des issues: {e}")
                metadata['issues'] = []  # optionnel : ne pas bloquer

        # 6. Retourner le résultat
        print(f"✅ Analyse réussie: {len(metadata.get('sheets', []))} feuilles trouvées")
        return jsonify(metadata)

    except Exception as e:
        print(f"❌ Erreur inattendue: {traceback.format_exc()}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500



@app.route('/api/preview', methods=['GET'])
def get_preview():
    """Récupère un aperçu des données d'une feuille"""
    try:
        file_path = request.args.get('file')
        sheet_name = request.args.get('sheet')
        rows = int(request.args.get('rows', 10))
        
        if not file_path or not sheet_name:
            return jsonify({'error': 'Paramètres manquants'}), 400
        
        preview = ExcelAnalyzer.get_sheet_preview(file_path, sheet_name, rows)
        return jsonify({'preview': preview})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sheets', methods=['GET'])
def get_sheets():
    """Récupère les feuilles disponibles dans un fichier"""
    try:
        file_path = request.args.get('file')
        
        if not file_path:
            return jsonify({'error': 'Paramètre file manquant'}), 400
        
        if not Path(file_path).exists():
            return jsonify({'error': 'Fichier introuvable'}), 404
        
        excel_file = pd.ExcelFile(file_path)
        return jsonify({'sheets': excel_file.sheet_names})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _index_to_col_letter(idx: int) -> str:
    """Convertit un index 0-based en lettre Excel"""
    result = ""
    idx += 1
    while idx > 0:
        idx, remainder = divmod(idx - 1, 26)
        result = chr(65 + remainder) + result
    return result


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Serveur Backend Flask démarré")
    print("=" * 60)
    print(f"📁 Dossier de fichiers: {UPLOAD_FOLDER}")
    print(f"🌐 URL: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
