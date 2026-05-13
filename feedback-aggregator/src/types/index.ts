export interface FileItem {
  id: string
  name: string
  statusColor: string
  filePath?: string // Chemin complet du fichier
  availableSheets?: string[] // Feuilles disponibles dans le fichier
  metadata?: FileMetadata // Métadonnées complètes du fichier
}

export interface FileMetadata {
  fileName: string
  filePath: string
  sheets: string[]
  columns: Record<string, ColumnInfo[]> // sheetName -> infos colonnes
  preview: Record<string, any[]> // sheetName -> aperçu des données
  issues?: Array<{ id: string; label: string }> // Issues détectées automatiquement
}

export interface ColumnInfo {
  name: string // Nom de l'en-tête
  letter: string // Lettre Excel (A, B, C...)
  index: number // Index 0-based
  type?: string // Type détecté (string, number, date)
  sampleValues?: any[] // Quelques valeurs exemple
}

export type OperationType = 'celldown' | 'superxlookup' | 'ticket'

export interface TicketConfig {
  source_file_path: string, 
  target_file_path: string,
  colown_key_path_source: string // Colonne clé dans source (ex: "B")
  target_key_column: string // Colonne clé dans cible (ex: "B")
  target_value_column: string // Colonne valeur dans cible (ex: "T")
  result_position_column: string // Où écrire le résultat (ex: "C")
  source_sheet_name: string // Nom de la feuille source
  start_column: string // Colonne de départ (ex: "C")
  reference_name: string
  target_join_columns: string[] // colonnes à concaténer
  join_separator: string // séparateur
  ignore_empty: boolean // ignorer les vides
  target_sheet_name: string // Nom de la feuille cible
}


export interface CellDownConfig {
  source_file_path: string
  target_file_path: string
  colown_key_path_source: string // Colonne clé dans source (ex: "B")
  target_key_column: string // Colonne clé dans cible (ex: "B")
  target_value_column: string // Colonne valeur dans cible (ex: "T")
  result_position_column: string // Où écrire le résultat (ex: "C")
  source_sheet_path: string // Nom de la feuille source
  date_str: string // Date à rechercher (ex: "29042026")
  start_column: string // Colonne de départ (ex: "C")
}

export interface SuperXlookupConfig {
  source_file_path: string
  target_file_path: string
  source_key_column: string // Colonne clé dans source (ex: "B")
  target_key_column: string // Colonne clé dans cible (ex: "D")
  target_value_column: string // Colonne valeur à rapporter (ex: "J")
  result_position_column: string // Position résultat (ex: "C" ou "last_free")
  result_column_name: string // Nom de la colonne résultat (ex: "Commentaire")
  source_sheet_name: string // Nom de la feuille source
  target_sheet_name: string // Nom de la feuille cible
}

export interface FileMapping {
  operationType: OperationType
  celldownConfig?: CellDownConfig
  superxlookupConfig?: SuperXlookupConfig
  ticketConfig?: TicketConfig
}

export type PreviewChecks = Record<string, boolean> // issueId -> checked

export interface PreviewItem {
  id: string
  label: string
}

export interface ProgressStats {
  totalIssues: number
  selectedIssues: number
}
