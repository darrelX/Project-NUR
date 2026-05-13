// operations/SuperXlookupForm.tsx
import type { SuperXlookupConfig } from '../types';
import { FileSelect, SheetSelect, ColumnSelect, ResultPositionSelect } from '../shared';

interface SuperXlookupFormProps {
  config: SuperXlookupConfig;
  onUpdate: <K extends keyof SuperXlookupConfig>(field: K, value: SuperXlookupConfig[K]) => void;
  availableFiles: any[];
  // les helpers viennent du hook du parent, ou on passe directement les getters
  getSheetsForFile: (path: string) => string[];
  getColumnsForSheet: (path: string, sheet: string) => any[];
  ensureFileMetadata: (path: string) => Promise<void>;
  loadingFiles: Record<string, boolean>;
}

export function SuperXlookupForm({
  config,
  onUpdate,
  availableFiles,
  getSheetsForFile,
  getColumnsForSheet,
  ensureFileMetadata,
  loadingFiles,
}: SuperXlookupFormProps) {
  const sourceFile = config.source_file_path;
  const targetFile = config.target_file_path;
  const sourceSheets = getSheetsForFile(sourceFile);
  const targetSheets = getSheetsForFile(targetFile);
  const sourceColumns = getColumnsForSheet(sourceFile, config.source_sheet_name);
  const targetColumns = getColumnsForSheet(targetFile, config.target_sheet_name);

  return (
    <div className="space-y-4 border-t border-gray-100 pt-4">
      <h3 className="text-sm font-semibold text-gray-700">Configuration SuperXlookup</h3>

      <FileSelect
        value={sourceFile}
        onChange={async (path) => {
          await ensureFileMetadata(path);
          const firstSheet = getSheetsForFile(path)[0] || '';
          onUpdate('source_file_path', path);
          onUpdate('source_sheet_name', firstSheet);
          onUpdate('source_key_column', '');
          onUpdate('result_position_column', 'last_free');
        }}
        availableFiles={availableFiles}
        isLoading={!!loadingFiles[sourceFile]}
        label="📄 Fichier source"
      />

      <SheetSelect
        value={config.source_sheet_name}
        onChange={(sheet) => {
          onUpdate('source_sheet_name', sheet);
          onUpdate('source_key_column', '');
          onUpdate('result_position_column', 'last_free');
        }}
        sheets={sourceSheets}
        isLoading={!!loadingFiles[sourceFile]}
        disabled={!sourceFile}
      />

      <FileSelect
        value={targetFile}
        onChange={async (path) => {
          await ensureFileMetadata(path);
          const firstSheet = getSheetsForFile(path)[0] || '';
          onUpdate('target_file_path', path);
          onUpdate('target_sheet_name', firstSheet);
          onUpdate('target_key_column', '');
          onUpdate('target_value_column', '');
        }}
        availableFiles={availableFiles}
        isLoading={!!loadingFiles[targetFile]}
        label="📄 Fichier cible"
      />

      <SheetSelect
        value={config.target_sheet_name}
        onChange={(sheet) => {
          onUpdate('target_sheet_name', sheet);
          onUpdate('target_key_column', '');
          onUpdate('target_value_column', '');
        }}
        sheets={targetSheets}
        isLoading={!!loadingFiles[targetFile]}
        disabled={!targetFile}
      />

      <ColumnSelect
        value={config.source_key_column}
        onChange={(col) => onUpdate('source_key_column', col)}
        columns={sourceColumns}
        disabled={!sourceFile || !config.source_sheet_name}
        label="🔑 Colonne clé source"
      />

      <ColumnSelect
        value={config.target_key_column}
        onChange={(col) => onUpdate('target_key_column', col)}
        columns={targetColumns}
        disabled={!targetFile || !config.target_sheet_name}
        label="🔑 Colonne clé cible"
      />

      <ColumnSelect
        value={config.target_value_column}
        onChange={(col) => onUpdate('target_value_column', col)}
        columns={targetColumns}
        disabled={!targetFile || !config.target_sheet_name}
        label="📋 Colonne valeur (cible)"
      />

      <ResultPositionSelect
        value={config.result_position_column}
        onChange={(pos) => onUpdate('result_position_column', pos)}
        columns={sourceColumns}
        disabled={!sourceFile || !config.source_sheet_name}
      />

      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">🏷️ Nom de la nouvelle colonne</label>
        <input
          type="text"
          value={config.result_column_name}
          onChange={(e) => onUpdate('result_column_name', e.target.value)}
          placeholder="Ex: Commentaire"
          className="w-full border rounded-lg px-3 py-2 text-sm"
        />
      </div>
    </div>
  );
}