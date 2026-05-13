import type { FileMapping, CellDownConfig, SuperXlookupConfig } from '../types'

export const defaultCellDownConfig: CellDownConfig = {
  source_file_path: '',
  target_file_path: '',
  colown_key_path_source: 'B',
  target_key_column: 'B',
  target_value_column: 'T',
  result_position_column: 'C',
  source_sheet_path: 'Sheet1',
  date_str: '',
  start_column: 'C',
}

export const defaultSuperXlookupConfig: SuperXlookupConfig = {
  source_file_path: '',
  target_file_path: '',
  source_key_column: 'B',
  target_key_column: 'D',
  target_value_column: 'J',
  result_position_column: 'C',
  result_column_name: 'Commentaire',
  source_sheet_name: 'Sheet1',
  target_sheet_name: 'Sheet1',
}

export const defaultMapping: FileMapping = {
  operationType: 'superxlookup',
  superxlookupConfig: { ...defaultSuperXlookupConfig },
}

// Options communes pour les colonnes Excel (A-Z)
export const excelColumns = Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i))

