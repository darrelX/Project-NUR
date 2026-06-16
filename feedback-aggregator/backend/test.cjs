// test-api.js
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

// Configuration
const BASE_URL = 'http://localhost:5000'; // Adapter selon votre serveur

/**
 * Envoie un fichier vers /api/upload-main-file
 * @param {string} filePath - Chemin vers le fichier Excel principal
 * @param {string} [sheetName] - Nom facultatif de la feuille
 * @returns {Promise<object>} Réponse JSON du serveur
 */
async function uploadMainFile(filePath, sheetName) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    if (sheetName) {
        form.append('sheet_name', sheetName);
    }

    try {
        const response = await axios.post(`${BASE_URL}/api/upload-main-file`, form, {
            headers: form.getHeaders(),
        });
        console.log('[uploadMainFile] Succès :', response.data);
        return response.data;
    } catch (error) {
        console.error('[uploadMainFile] Erreur :', error.response?.data || error.message);
        throw error;
    }
}

/**
 * Envoie un fichier cible vers /api/process-ticket avec les paramètres optionnels
 * @param {string} targetFilePath - Chemin vers le fichier Excel cible
 * @param {object} params - Paramètres optionnels (voir doc)
 * @returns {Promise<object>} Réponse JSON du serveur
 */
async function processTicket(targetFilePath, params = {}) {
    const form = new FormData();
    form.append('file', fs.createReadStream(targetFilePath));

    // Ajout des paramètres texte (s'ils sont fournis)
    const optionalFields = [
        'reference_name',
        'reference_date',
        'source_key_column',
        'target_key_column',
        'source_sheet_name',
        'target_sheet_name',
        'result_column_name',
        'target_join_columns',
        'join_separator',
        'ignore_empty',
        'extract_source_column'
    ];

    for (const field of optionalFields) {
        if (params[field] !== undefined) {
            // Si la valeur est un objet ou un tableau, on la convertit en JSON
            const value = typeof params[field] === 'object' 
                ? JSON.stringify(params[field]) 
                : params[field];
            form.append(field, value);
        }
    }

    try {
        const response = await axios.post(`${BASE_URL}/api/process-ticket`, form, {
            headers: form.getHeaders(),
        });
        // console.log('[processTicket] Succès :', response.data);
        return response.data;
    } catch (error) {
        console.error('[processTicket] Erreur :', error.response?.data || error.message);
        throw error;
    }
}

/**
 * Télécharge le fichier principal consolidé depuis /api/export
 * @param {string} outputDir - Dossier de destination (défaut : ./exports)
 * @returns {Promise<string>} Chemin du fichier téléchargé
 */
async function exportFile(outputDir = './exports') {
    try {
        // Créer le dossier s'il n'existe pas
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        const url = `${BASE_URL}/api/export`;
        const response = await axios({
            method: 'GET',
            url: url,
            responseType: 'stream'
        });

        // Extraire le nom du fichier depuis Content-Disposition ou générer un nom par défaut
        let filename = `export_${Date.now()}.xlsx`;
        const disposition = response.headers['content-disposition'];
        if (disposition && disposition.includes('filename=')) {
            const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match && match[1]) {
                filename = match[1].replace(/['"]/g, '');
            }
        }

        const outputPath = path.join(outputDir, filename);
        const writer = fs.createWriteStream(outputPath);
        response.data.pipe(writer);

        return new Promise((resolve, reject) => {
            writer.on('finish', () => {
                console.log(`[exportFile] Fichier sauvegardé : ${outputPath}`);
                resolve(outputPath);
            });
            writer.on('error', reject);
        });
    } catch (error) {
        console.error('[exportFile] Erreur :', error.response?.data || error.message);
        throw error;
    }
}

/**
 * Envoie un fichier vers /process-celldown avec une configuration
 * @param {string} filePath - Chemin vers le fichier Excel (spécifique pour CellDown)
 * @param {object} config - Configuration (reference_name, colown_key_path_source, etc.)
 * @returns {Promise<object>} Réponse JSON du serveur
 */
async function processCellDown(filePath, config = {}) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));

    // Configuration par défaut (identique à celle du frontend)
    const defaultConfig = {
        reference_name: '',
        reference_date: '',
        date_str: '13062026',
        colown_key_path_source: 'Codesite',
        target_key_column: 'Site Code,SITE_CODE,site code,Code Site',
        target_value_column: 'Comment,COMMENT,comment',
        source_sheet_path: 'Sheet1',
        start_column: 'last_column',
    };

    const mergedConfig = { ...defaultConfig, ...config };

    // Ces champs peuvent être des tableaux : on les convertit en CSV (séparés par des virgules)
    const listKeys = ['colown_key_path_source', 'target_key_column', 'target_value_column'];
    for (const key of listKeys) {
        const value = mergedConfig[key];
        if (value !== undefined && value !== null) {
            const stringValue = Array.isArray(value) ? value.join(',') : String(value);
            form.append(key, stringValue);
        }
    }

    // Champs simples
    const simpleKeys = ['reference_name', 'reference_date', 'date_str', 'source_sheet_path', 'start_column'];
    for (const key of simpleKeys) {
        const value = mergedConfig[key];
        if (value !== undefined && value !== null) {
            form.append(key, String(value));
        }
    }

    try {
        const response = await axios.post(`${BASE_URL}/api/process-celldown`, form, {
            headers: form.getHeaders(),
        });
        console.log('[processCellDown] Succès :', response.data);
        return response.data;
    } catch (error) {
        console.error('[processCellDown] Erreur :', error.response?.data || error.message);
        throw error;
    }
}

// ==================== EXEMPLE D'UTILISATION ====================
async function runTests() {
    // Chemins vers vos fichiers Excel de test
    const mainFilePath = 'C:\\Users\\f50056342\\Desktop\\computer science\\NUR Project Lyne\\inputs\\Book1.xlsx';
    const targetFilePath = 'C:\\Users\\f50056342\\Downloads\\Incident Ticket_20260611122558.xlsx';
    const celldownFilePath = 'C:\\Users\\f50056342\\Desktop\\my work\\cellsdow files\\celldown Huawei\\DAILY_W24_CELLS_DOWN_HUAWEI_13062026 14h.xlsx'; // ← À modifier selon votre fichier

    // Vérifier que les fichiers existent
    if (!fs.existsSync(mainFilePath)) {
        console.error(`Fichier principal introuvable : ${mainFilePath}`);
        return;
    }
    if (!fs.existsSync(targetFilePath)) {
        console.error(`Fichier cible (processTicket) introuvable : ${targetFilePath}`);
        return;
    }
    if (!fs.existsSync(celldownFilePath)) {
        console.error(`Fichier pour CellDown introuvable : ${celldownFilePath}`);
        console.log('Veuillez fournir un chemin valide pour celldownFilePath');
        return;
    }

    try {
        // 1. Upload du fichier principal
        console.log('--- Upload du fichier principal ---');
        await uploadMainFile(mainFilePath, ''); // adapter le nom de feuille

        // 2. Traitement du ticket (process-ticket)
        console.log('\n--- Traitement du ticket ---');
        const ticketParams = {
            reference_name: 'TicketTest',
            source_key_column: 'Codesite',
            source_sheet_name: 'Sheet1',
            target_sheet_name: '',
            result_column_name: 'Ticket',
            join_separator: '..',
            ignore_empty: 'true',
        };
        await processTicket(targetFilePath, ticketParams);

        // 3. Test de l'endpoint /process-celldown
        console.log('\n--- Test CellDown ---');
        const celldownConfig = {
            date_str: '13062026',
        };
        await processCellDown(celldownFilePath, celldownConfig);

        // 4. Export du fichier consolidé
        console.log('\n--- Export du fichier consolidé ---');
        const exportedFilePath = await exportFile('./exports');
        console.log(`Fichier exporté avec succès : ${exportedFilePath}`);

        console.log('\n✅ Tests terminés avec succès.');
    } catch (err) {
        console.error('\n❌ Un test a échoué :', err.message);
    }
}

// Lancer les tests
runTests();