// apiService.ts
const API_BASE_URL = 'http://127.0.0.1:5000/api'

export interface ProcessedFile {
  name: string
  size: string
  lines: number
  isImported: boolean
  category?: string
}

type SaveStatus = {
  success: boolean;
  file_exists: boolean;
  message: string;
  file_path?: string;
};

export interface ApiDataRow {
  [key: string]: any
}

// Utilitaire pour convertir une valeur en chaîne utilisable par FormData
function serializeConfigValue(_key: string, value: any): string {
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false'
  }
  if (Array.isArray(value) || (typeof value === 'object' && value !== null)) {
    return JSON.stringify(value)
  }
  return String(value)
}

export class ApiService {
  // Upload du fichier principal (avec nom de feuille optionnel)
  async uploadMainFile(file: File, sheetName?: string) {
    console.log('📤 [apiService] Uploading file:', file.name, file.size, 'bytes')
    const formData = new FormData()
    formData.append('file', file)
    if (sheetName) {
      formData.append('sheet_name', sheetName)
    }

    const url = `${API_BASE_URL}/upload-main-file`
    console.log('🌐 [apiService] POST:', url)

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      })
      console.log('📡 [apiService] Upload response:', response.status, response.statusText)

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Upload failed')
      }
      const result = await response.json()
      console.log('✅ [apiService] Upload success:', result)
      return result
    } catch (error: any) {
      console.error('❌ [apiService] Upload error:', error.message)
      throw error
    }
  }

  // Efface la référence au fichier principal (côté backend)
  async clearMainFile() {
    const response = await fetch(`${API_BASE_URL}/clear-main-file`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Clear failed')
    }
    return response.json()
  }

  // Processus CellDown
async processCelldown(file: File, config: any) {
  console.log('📤 [CellDown] Config reçu du frontend:', config);
  
  const defaultConfig = {
    reference_name: '',
    reference_date: '',
    date_str: '',
    source_sheet_path: 'Sheet1',
    colown_key_path_source: 'Codesite',
    target_key_column: 'Site Code,SITE_CODE,site code,Code Site',
    target_value_column: 'Comment,COMMENT,comment',
    start_column: 'last_column',
  };



  const mergedConfig = { ...defaultConfig, ...config };
  
  console.log('🔧 [CellDown] Configuration fusionnée (defaultConfig + config frontend):', mergedConfig);
  
  const formData = new FormData();
  formData.append('file', file);
    console.log("Darrel 1 ")

  // Pour CellDown, les listes doivent être envoyées sous forme de chaîne CSV
  const listKeys = ['colown_key_path_source', 'target_key_column', 'target_value_column'];
  for (const key of listKeys) {
    const value = mergedConfig[key];
    if (value !== undefined && value !== null) {
      try {
        formData.append(key, Array.isArray(value) ? value.join(',') : String(value));
      } catch (err) {
        console.error(`❌ Error appending list key '${key}':`, err);
        throw new Error(`Invalid format for parameter '${key}'`);
      }
    }
  }

  // Autres paramètres simples
  const simpleKeys = ['reference_name', 'reference_date', 'date_str', 'source_sheet_path', 'start_column'];
  for (const key of simpleKeys) {
    const value = mergedConfig[key];
    if (value !== undefined && value !== null) {
      try {
        formData.append(key, String(value));
      } catch (err) {
        console.error(`❌ Error appending simple key '${key}':`, err);
        throw new Error(`Invalid value for parameter '${key}'`);
      }
    }
  }

  // Afficher les paramètres envoyés (sans le File object pour plus de clarté)
  console.log('📋 [CellDown] Paramètres envoyés au backend:');
  const params: Record<string, any> = {};
  for (const [key, value] of formData.entries()) {
    if (key !== 'file') {
      params[key] = value;
      console.log(`  ✓ ${key}: ${value}`);
    }
  }

  try {
    const response = await fetch(`${API_BASE_URL}/process-celldown`, {
      method: 'POST',
      body: formData,
    });

    console.log('📡 [CellDown] Response status:', response.status, response.statusText);
    if (!response.ok) {
      console.log('📡 [CellDown] Response status:', response.status, response.statusText);
      let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorDetail = errorData.error || errorDetail;
      } catch (parseError) {
        // Si la réponse n'est pas du JSON valide, on utilise le texte brut
        try {
          const textError = await response.text();
          if (textError) errorDetail = textError;
        } catch (textError) {
          // Ignorer, on garde le message par défaut
        }
      }
      throw new Error(`CellDown processing failed: ${errorDetail}`);
    }
    console.log("response ", response)

    const data = await response.json(); 
    return data;
  } catch (error) {
    // Gestion des erreurs réseau ou autres exceptions
    console.error('❌ [apiService] CellDown request failed:', error);
    if (error instanceof Error) {
      throw new Error(`Failed to process CellDown: ${error.message}`);
    }
    throw new Error('An unknown error occurred during CellDown processing');
  }
}

  // Processus Xlookup
  async processXlookup(file: File, config: any) {
    console.log('📤 [Xlookup] Config reçu du frontend:', config);
    
    // Définir les valeurs par défaut selon le backend
    const defaultConfig = {
      source_key_column: 'Codesite',
      target_key_column: 'Site ID,SITE_ID,site id',
      target_value_column: 'Actions en cours,Actions',
      source_sheet_name: 'Sheet1',
      target_sheet_name: '',
      result_column_name: '',
      reference_name: '',
      reference_date: '',
      result_position_column: 'last_column',
    }

    const mergedConfig = { ...defaultConfig, ...config }
    
    console.log('🔧 [Xlookup] Configuration fusionnée (defaultConfig + config frontend):', mergedConfig);
    
    const formData = new FormData()
    formData.append('file', file)

    // Si aucun nom de colonne résultat n'est fourni, utiliser le nom du fichier (sans extension)
    if (!mergedConfig.result_column_name) {
      mergedConfig.result_column_name = file.name.replace(/\.[^/.]+$/, '')
    }

    // Paramètres pouvant être des listes (CSV)
    const listKeys = ['source_key_column', 'target_key_column', 'target_value_column']
    for (const key of listKeys) {
      const value = mergedConfig[key]
      if (value !== undefined && value !== null) {
        formData.append(key, Array.isArray(value) ? value.join(',') : String(value))
      }
    }

    // Paramètres simples
    const simpleKeys = [
      'source_sheet_name',
      'target_sheet_name',
      'result_column_name',
      'reference_name',
      'reference_date',
      'result_position_column',
    ]
    for (const key of simpleKeys) {
      const value = mergedConfig[key]
      if (value !== undefined && value !== null) {
        formData.append(key, String(value))
      }
    }

    // Afficher les paramètres envoyés
    console.log('📋 [Xlookup] Paramètres envoyés au backend:');
    for (const [key, value] of formData.entries()) {
      if (key !== 'file') {
        console.log(`  ✓ ${key}: ${value}`);
      }
    }
    console.log(`  ✓ file: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);

    const response = await fetch(`${API_BASE_URL}/process-xlookup`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Xlookup processing failed')
    }
    return response.json()
  }

  // Processus Ticket
  async processTicket(file: File, config: any) {
    console.log('📤 [Ticket] Config reçu du frontend:', config);
    
    // Définir les valeurs par défaut selon le backend
    const defaultConfig = {
      reference_name: 'Ticket',
      reference_date: '',
      source_key_column: 'Codesite',
      target_key_column: null,
      source_sheet_name: 'Sheet1',
      target_sheet_name: '',
      result_column_name: 'Ticket',
      target_join_columns: [
        ['Ticket ID(Create TT)'],
        ['Description(Process TT)'],
        ['Solution(Process TT)'],
        ['Root Cause(Process TT)'],
        ['Incident Reason Detail(Process TT)'],
      ],
      join_separator: '..',
      ignore_empty: true,
      extract_source_column: null,
    }

    const mergedConfig = { ...defaultConfig, ...config }
    
    console.log('🔧 [Ticket] Configuration fusionnée (defaultConfig + config frontend):', mergedConfig);
    
    const formData = new FormData()
    formData.append('file', file)

    // Paramètres qui peuvent être des structures complexes → JSON
    const jsonKeys = [
      'source_key_column',
      'target_key_column',
      'target_join_columns',
      'extract_source_column',
    ]
    for (const key of jsonKeys) {
      const value = mergedConfig[key]
      if (value !== undefined && value !== null) {
        formData.append(key, serializeConfigValue(key, value))
      }
    }

    // Paramètres simples (booléens convertis en 'true'/'false')
    const simpleKeys = [
      'reference_name',
      'reference_date',
      'source_sheet_name',
      'target_sheet_name',
      'result_column_name',
      'join_separator',
      'ignore_empty',
    ]
    for (const key of simpleKeys) {
      const value = mergedConfig[key]
      if (value !== undefined && value !== null) {
        formData.append(key, serializeConfigValue(key, value))
      }
    }

    // Afficher les paramètres envoyés
    console.log('📋 [Ticket] Paramètres envoyés au backend:');
    for (const [key, value] of formData.entries()) {
      if (key !== 'file') {
        console.log(`  ✓ ${key}: ${value}`);
      }
    }
    console.log(`  ✓ file: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);

    const response = await fetch(`${API_BASE_URL}/process-ticket`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Ticket processing failed')
    }
    return response.json()
  }

// Nouveau type pour la réponse simplifiée

// Nouveau type pour la réponse simplifiée


// Dans la classe ApiService
async getData(): Promise<SaveStatus> {
  const url = `${API_BASE_URL}/get-data`;  // plus de paramètres
  console.log('🌐 [apiService] GET:', url);

  try {
    const response = await fetch(url);
    console.log('📡 [apiService] Response status:', response.status, response.statusText);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get save status');
    }

    const json = await response.json();
    console.log('✅ [apiService] Save status:', json);
    return {
      success: json.success,
      file_exists: json.file_exists,
      message: json.message,
      file_path: json.file_path || '',
    };
  } catch (error: any) {
    console.error('❌ [apiService] Fetch error:', error.message);
    console.error('❌ [apiService] URL was:', url);
    throw error;
  }
}

  // Export du fichier consolidé (déclenche le téléchargement)
  async exportFile() {
    const response = await fetch(`${API_BASE_URL}/export`)
    if (!response.ok) {
      throw new Error('Export failed')
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `consolidated_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  // Télécharge le fichier traité sous forme de Blob (utile pour traitement local)
  async downloadProcessedFile(): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/export`)
    if (!response.ok) {
      throw new Error('Failed to download processed file')
    }
    return response.blob()
  }

  // Vérification de l'état du backend
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      return response.ok
    } catch {
      return false
    }
  }
}

export const apiService = new ApiService()