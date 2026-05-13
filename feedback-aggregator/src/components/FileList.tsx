import type { FileItem } from '../types'

interface FileListProps {
  files: FileItem[]
  selectedFileId: string
  onSelectFile: (id: string) => void
  onDeleteFile: (fileId: string, event: React.MouseEvent) => void
}

export default function FileList({ files, selectedFileId, onSelectFile, onDeleteFile }: FileListProps) {
  return (
    <div className="w-full md:w-80 lg:w-96 bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden flex flex-col h-fit md:h-auto">
      <div className="p-4 border-b border-gray-100 bg-gray-50/50">
        <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Fichiers sources</h2>
      </div>
      <div className="divide-y divide-gray-100 max-h-[calc(100vh-200px)] overflow-y-auto">
        {files.map((file) => (
          <div
            key={file.id}
            className={`group relative transition-all ${
              selectedFileId === file.id ? 'bg-blue-50/50 border-l-4 border-blue-500' : 'hover:bg-gray-50'
            }`}
          >
            <button onClick={() => onSelectFile(file.id)} className="w-full flex items-center gap-4 p-4 text-left">
              <div className={`w-3 h-3 rounded-full shrink-0 ${file.statusColor} ring-2 ring-white`} />
              <span
                className={`text-sm truncate flex-1 ${
                  selectedFileId === file.id ? 'font-semibold text-slate-900' : 'text-slate-600'
                }`}
              >
                {file.name}
              </span>
            </button>
            <button
              onClick={(e) => onDeleteFile(file.id, e)}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-red-500 rounded-md opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 backdrop-blur"
              aria-label="Supprimer le fichier"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
