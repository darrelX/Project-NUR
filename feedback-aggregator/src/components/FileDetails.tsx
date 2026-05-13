import type { FileItem, FileMapping, PreviewChecks, PreviewItem } from '../types'
import OperationConfig from './OperationConfig'

interface FileDetailsProps {
  selectedFile: FileItem | undefined
  allFiles: FileItem[] // Tous les fichiers disponibles pour sélection
  currentMapping: FileMapping
  currentPreviewChecks: PreviewChecks
  previewItems: PreviewItem[]
  onUpdateMapping: (mapping: FileMapping) => void
  onTogglePreviewItem: (issueId: string) => void
}

export default function FileDetails({
  selectedFile,
  allFiles,
  currentMapping,
  currentPreviewChecks,
  previewItems,
  onUpdateMapping,
  onTogglePreviewItem,
}: FileDetailsProps) {

  if (!selectedFile) {
    return (
      <div className="w-full md:w-96 lg:w-[28rem] bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden flex flex-col h-fit md:h-auto">
        <div className="flex flex-col items-center justify-center p-12 text-center h-full">
          <svg
            className="w-16 h-16 mx-auto text-gray-300 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.5"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p className="text-gray-500 text-lg">Aucun fichier sélectionné</p>
          <p className="text-gray-400 text-sm mt-1">Cliquez sur un fichier dans la liste de gauche</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full md:w-96 lg:w-[28rem] bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden flex flex-col h-fit md:h-auto">
      <div className="flex flex-col h-full">
        <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-white">
          <div className={`w-3 h-3 rounded-full ${selectedFile.statusColor}`} />
          <h2 className="text-xl font-medium text-slate-800 truncate">{selectedFile.name}</h2>
        </div>

        <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(100vh-240px)]">
          {/* Configuration des opérations */}
          <OperationConfig
            mapping={currentMapping}
            availableFiles={allFiles}
            onUpdateMapping={onUpdateMapping}
          />


        </div>
      </div>
    </div>
  )
}