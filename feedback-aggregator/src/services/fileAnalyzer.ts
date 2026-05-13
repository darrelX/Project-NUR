import type { FileMetadata, ColumnInfo, PreviewItem } from '../types'

// Service pour analyser les fichiers Excel
const API_BASE_URL = 'http://localhost:5000'

export const fileAnalyzerService = {
    /**
     * Analyse complète d'un fichier Excel
     * Retourne toutes les métadonnées nécessaires pour la configuration
     */
    // fileAnalyzerService.analyzeFile modifié
    // Dans votre service (fileAnalyzerService)
    async analyzeFile(filePath: string): Promise<FileMetadata | null> {
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filePath }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            // Lancer une erreur avec le message du backend
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        return await response.json();
    },
    /**
     * Récupère les colonnes d'une feuille spécifique avec détails
     */
    async getSheetColumns(filePath: string, sheetName: string): Promise<ColumnInfo[]> {
        try {
            const response = await fetch(
                `${API_BASE_URL}/api/columns-detail?file=${encodeURIComponent(filePath)}&sheet=${encodeURIComponent(sheetName)}`
            )

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            return await response.json()
        } catch (error) {
            console.error('Erreur lors de la récupération des colonnes:', error)
            return []
        }
    },

    /**
     * Détecte automatiquement les issues potentielles dans un fichier
     * (basé sur des mots-clés, patterns, etc.)
     */
    async detectIssues(filePath: string, sheetName: string): Promise<PreviewItem[]> {
        try {
            const response = await fetch(
                `${API_BASE_URL}/api/detect-issues?file=${encodeURIComponent(filePath)}&sheet=${encodeURIComponent(sheetName)}`
            )

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data = await response.json()
            return data.issues || []
        } catch (error) {
            console.error('Erreur lors de la détection des issues:', error)
            return []
        }
    },

    /**
     * Récupère un aperçu des données d'une feuille
     */
    async getSheetPreview(filePath: string, sheetName: string, rows: number = 10): Promise<any[]> {
        try {
            const response = await fetch(
                `${API_BASE_URL}/api/preview?file=${encodeURIComponent(filePath)}&sheet=${encodeURIComponent(sheetName)}&rows=${rows}`
            )

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data = await response.json()
            return data.preview || []
        } catch (error) {
            console.error('Erreur lors de la récupération de l\'aperçu:', error)
            return []
        }
    },
}
