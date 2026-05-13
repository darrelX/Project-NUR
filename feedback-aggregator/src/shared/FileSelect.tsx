// shared/FileSelect.tsx
import { FileItem } from '../types';

interface FileSelectProps {
  value: string;
  onChange: (path: string) => Promise<void> | void;
  availableFiles: FileItem[];
  isLoading: boolean;
  disabled?: boolean;
  label?: string;
}

export function FileSelect({
  value,
  onChange,
  availableFiles,
  isLoading,
  disabled = false,
  label = '📄 Fichier',
}: FileSelectProps) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-500 mb-1">{label}</label>
      <div className="relative">
        <select
          value={value}
          onChange={async (e) => {
            await onChange(e.target.value);
          }}
          disabled={disabled || isLoading}
          className="w-full border rounded-lg px-3 py-2 text-sm disabled:bg-gray-50 disabled:text-gray-500"
        >
          <option value="">-- Sélectionner --</option>
          {availableFiles.map(file => (
            <option key={file.id} value={file.filePath}>{file.name}</option>
          ))}
        </select>
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </div>
    </div>
  );
}