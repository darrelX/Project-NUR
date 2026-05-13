// Service pour communiquer avec le backend Python

const API_BASE_URL = 'http://localhost:5000' // À ajuster selon votre configuration

export interface CompilationRequest {
  operationType: 'celldown' | 'superxlookup'
  config: any // CellDownConfig ou SuperXlookupConfig
  selectedIssues: string[]
}

export interface CompilationResponse {
  success: boolean
  message: string
  details?: any
}

export const compilationService = {
  /**
   * Lance une compilation avec la configuration spécifiée
   */
  async runCompilation(request: CompilationRequest): Promise<CompilationResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/compile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Erreur lors de la compilation:', error)
      return {
        success: false,
        message: `Erreur: ${error instanceof Error ? error.message : 'Erreur inconnue'}`,
      }
    }
  },

  /**
   * Récupère les feuilles disponibles dans un fichier Excel
   */
  async getAvailableSheets(filePath: string): Promise<string[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sheets?file=${encodeURIComponent(filePath)}`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.sheets || []
    } catch (error) {
      console.error('Erreur lors de la récupération des feuilles:', error)
      return []
    }
  },

  /**
   * Récupère les colonnes disponibles dans une feuille Excel
   */
  async getAvailableColumns(filePath: string, sheetName: string): Promise<string[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/columns?file=${encodeURIComponent(filePath)}&sheet=${encodeURIComponent(sheetName)}`
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.columns || []
    } catch (error) {
      console.error('Erreur lors de la récupération des colonnes:', error)
      return []
    }
  },

  /**
   * Upload un fichier Excel
   */
  // compilationService.ts (extrait modifié)
  async uploadFile(file: File): Promise<UploadResult> {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        return {
          success: false,
          error: data.error || 'Upload failed',
        }
      }

      if (!data.filePath) {
        return {
          success: false,
          error: 'Backend response missing filePath',
        }
      }

      return {
        success: true,
        filePath: data.filePath,
        metadata: data.metadata,
      }
    } catch (error) {
      console.error('Upload error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown upload error',
      }
    }
  }
}
