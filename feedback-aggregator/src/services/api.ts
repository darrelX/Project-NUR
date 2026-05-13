const API_BASE_URL: string = 'http://localhost:5000/api';

// Types for API responses and parameters
interface ColumnInfo {
  letter: string;
  // Add other properties if needed
}

interface SheetInfo {
  name: string;
  // Add other properties if needed
}

interface FileColumnsResponse {
  columns: ColumnInfo[] | string[];
}

interface FileSheetsResponse {
  sheets: SheetInfo[] | string[];
}

interface FilePreviewResponse {
  // Define based on actual API response (unknown for now)
  [key: string]: any;
}

interface HealthCheckResponse {
  // Define as needed
  [key: string]: any;
}

interface GetFilesResponse {
  // Define as needed
  [key: string]: any;
}

interface CompileResponse {
  // Define as needed
  [key: string]: any;
}

interface UploadResponse {
  // Define as needed
  [key: string]: any;
}

// Config types (adjust according to actual API contract)
interface XLookupConfig {
  [key: string]: any;
}

interface CellDownConfig {
  [key: string]: any;
}

export const apiService = {
  // Vérifier la santé du serveur
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },

  // Récupérer la liste des fichiers
  async getFiles(): Promise<GetFilesResponse> {
    const response = await fetch(`${API_BASE_URL}/files`);
    return response.json();
  },

  // Récupérer les colonnes d'un fichier
  async getFileColumns(filePath: string, sheetName: string | number = 0): Promise<FileColumnsResponse> {
    const response = await fetch(`${API_BASE_URL}/file/columns`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ filePath, sheetName }),
    });
    return response.json();
  },

  // Récupérer les feuilles d'un fichier
  async getFileSheets(filePath: string): Promise<FileSheetsResponse> {
    const response = await fetch(`${API_BASE_URL}/file/sheets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ filePath }),
    });
    return response.json();
  },

  // Aperçu d'un fichier
  async getFilePreview(filePath: string, sheetName: string | number = 0, maxRows: number = 10): Promise<FilePreviewResponse> {
    const response = await fetch(`${API_BASE_URL}/file/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ filePath, sheetName, maxRows }),
    });
    return response.json();
  },

  // Compiler avec XLookup
  async compileXLookup(config: XLookupConfig): Promise<CompileResponse> {
    const response = await fetch(`${API_BASE_URL}/compile/xlookup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return response.json();
  },

  // Compiler avec CellDown
  async compileCellDown(config: CellDownConfig): Promise<CompileResponse> {
    const response = await fetch(`${API_BASE_URL}/compile/celldown`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return response.json();
  },

  // Upload un fichier
  async uploadFile(formData: FormData): Promise<UploadResponse> {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  // Récupérer les métadonnées d'un fichier (colonnes et feuilles)
  async getFileMetadata(fileId: string, filePath: string): Promise<{ columns: string[]; sheets: string[] }> {
    try {
      const [sheetsResponse, columnsResponse] = await Promise.all([
        this.getFileSheets(filePath),
        this.getFileColumns(filePath),
      ]);

      // Extraire les lettres de colonnes du format retourné
      const columns = columnsResponse.columns
        ? columnsResponse.columns.map((col) => (typeof col === 'string' ? col : col.letter))
        : [];

      // Extraire les noms de feuilles
      const sheets = sheetsResponse.sheets
        ? sheetsResponse.sheets.map((s) => (typeof s === 'string' ? s : s.name))
        : [];

      return { columns, sheets };
    } catch (error) {
      console.error('Error fetching file metadata:', error);
      return { columns: [], sheets: [] };
    }
  },

  // Alias pour runCellDown (utilisé dans les hooks)
  async runCellDown(config: CellDownConfig): Promise<CompileResponse> {
    return this.compileCellDown(config);
  },
};