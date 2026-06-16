import FileCard from './FileCard'
import CompilationSummary from './CompilationSummary'

interface ProcessedFile {
  name: string
  size: string
  lines: number
  isImported: boolean
  category?: string
}

interface MainFileInfo {
  name: string
  backendPath: string
  sheet: string | number
  lines: number
  size: number
  uploadedAt: string
}

interface FileImportSectionProps {
  files: ProcessedFile[]
  mainFileInfo: MainFileInfo | null
  isProcessing: boolean
  onAddFile: () => void
  onDeleteFile: (index: number) => void
}

export default function FileImportSection({
  files,
  mainFileInfo,
  isProcessing,
  onAddFile,
  onDeleteFile
}: FileImportSectionProps) {
  // Le bouton est actif automatiquement si mainFileInfo existe
  const isActive = mainFileInfo !== null && !isProcessing

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 mb-8 lg:mb-10">
      {/* Bloc importation */}
      <div className="lg:col-span-2">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-white text-xl font-semibold tracking-tight">
            Importation des fichiers
          </h2>
          <div className="flex items-center gap-3">
            {isActive && (
              <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs font-semibold rounded-full flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                ACTIF
              </span>
            )}
            <span className="text-xs text-gray-400 bg-[#1c2128] px-3 py-1 rounded-full">
              {files.length} fichier(s) chargé(s)
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 lg:gap-5">
          {files.map((file, index) => (
            <FileCard key={index} {...file} onDelete={() => onDeleteFile(index)} />
          ))}
          
          {/* Carte d'ajout - automatiquement active si mainFileInfo existe */}
          <button
            onClick={onAddFile}
            disabled={!isActive}
            className={`group bg-[#161b22] rounded-xl border-2 border-dashed transition-all duration-200 p-6 flex flex-col items-center justify-center gap-3 min-h-[180px] ${
              isActive
                ? 'border-[#30363d] hover:border-[#58a6ff] hover:bg-[#1c2128] cursor-pointer hover:scale-[1.02]'
                : 'border-[#21262d] opacity-50 cursor-not-allowed'
            }`}
            title={!mainFileInfo ? 'Chargez d\'abord le fichier principal' : ''}
          >
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-200 ${
              isActive
                ? 'bg-[#58a6ff]/10 group-hover:scale-110 group-hover:bg-[#58a6ff]/20'
                : 'bg-gray-700/10'
            }`}>
              <svg className={`w-6 h-6 ${isActive ? 'text-[#58a6ff]' : 'text-gray-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <div className="text-center">
              <p className={`font-medium text-sm transition-all ${
                isActive
                  ? 'text-[#58a6ff] group-hover:font-semibold'
                  : 'text-gray-600'
              }`}>
                Importer un fichier
              </p>
              <p className={`text-xs mt-1 ${isActive ? 'text-gray-500' : 'text-gray-600'}`}>
                Excel / CSV
              </p>
            </div>
          </button>
        </div>

        {/* Message quand inactif */}
        {!mainFileInfo && (
          <div className="mt-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 flex items-start gap-3">
            <svg className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="text-yellow-400 text-sm font-semibold">Fichier principal requis</p>
              <p className="text-yellow-300/70 text-xs mt-0.5">
                Chargez d'abord le fichier principal ci-dessus pour activer l'importation de fichiers
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Résumé */}
      <div className="mt-2 lg:mt-0">
        <CompilationSummary
          filesCount={files.length}
          totalLines={files.reduce((sum, f) => sum + f.lines, 0)}
          duplicates={0}
          conflicts={0}
          uniqueLines={files.reduce((sum, f) => sum + f.lines, 0)}
        />
      </div>
    </div>
  )
}
