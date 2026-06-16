import { useState } from 'react'

interface MainFileInfo {
  name: string
  backendPath: string
  sheet: string | number
  lines: number
  size: number
  uploadedAt: string
}

interface MainFileUploaderProps {
  onFileSelect: (file: File) => void
  fileInfo: MainFileInfo | null
  onClear: () => void
}

export default function MainFileUploader({ onFileSelect, fileInfo, onClear }: MainFileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv'))) {
      onFileSelect(file)
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onFileSelect(file)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  // Si un fichier est chargé, afficher ses informations
  if (fileInfo) {
    return (
      <div className="bg-gradient-to-br from-[#1a2332] to-[#0d1117] rounded-2xl border-2 border-green-500/30 shadow-2xl shadow-green-500/10 overflow-hidden">
        <div className="px-6 py-4 bg-gradient-to-r from-green-500/10 to-green-600/5 border-b border-green-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/30">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h2 className="text-white text-lg font-bold tracking-tight flex items-center gap-2">
                  Fichier Principal Chargé
                  <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs font-semibold rounded-full">ACTIF</span>
                </h2>
                <p className="text-green-400 text-sm">
                  Base de référence pour tous les traitements
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                if (confirm('Êtes-vous sûr de vouloir supprimer le fichier principal ? Tous les fichiers traités seront également supprimés.')) {
                  onClear()
                }
              }}
              className="text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg p-2 transition-all duration-200"
              title="Supprimer le fichier principal"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-[#0d1117]/70 rounded-xl p-4 border border-[#30363d]">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Nom du fichier</p>
              </div>
              <p className="text-white font-semibold truncate" title={fileInfo.name}>{fileInfo.name}</p>
            </div>
            
            <div className="bg-[#0d1117]/70 rounded-xl p-4 border border-[#30363d]">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Feuille</p>
              </div>
              <p className="text-white font-semibold">{fileInfo.sheet}</p>
            </div>
            
            <div className="bg-[#0d1117]/70 rounded-xl p-4 border border-[#30363d]">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Lignes</p>
              </div>
              <p className="text-white font-semibold text-xl">{fileInfo.lines.toLocaleString()}</p>
            </div>
            
            <div className="bg-[#0d1117]/70 rounded-xl p-4 border border-[#30363d]">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                </svg>
                <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Taille</p>
              </div>
              <p className="text-white font-semibold">{formatFileSize(fileInfo.size)}</p>
            </div>
            
            <div className="bg-[#0d1117]/70 rounded-xl p-4 border border-[#30363d] md:col-span-2">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
                <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Chemin backend</p>
              </div>
              <p className="text-white font-mono text-xs truncate" title={fileInfo.backendPath}>{fileInfo.backendPath}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Afficher l'uploader par défaut
  return (
    <div className="bg-[#161b22] rounded-xl border border-[#30363d] shadow-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-[#21262d]">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 bg-gradient-to-br from-[#58a6ff] to-[#1f6feb] rounded-lg flex items-center justify-center shadow-lg">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h2 className="text-white text-base font-semibold tracking-tight">
              Fichier principal
            </h2>
            <p className="text-gray-400 text-xs mt-0.5">
              Base de référence pour la consolidation
            </p>
          </div>
        </div>
      </div>

      <div className="p-5">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-xl transition-all duration-300 ${
            isDragging
              ? 'border-[#58a6ff] bg-[#58a6ff]/5 scale-[1.02]'
              : 'border-[#30363d] hover:border-[#58a6ff] hover:bg-[#0d1117]/50'
          }`}
        >
          <input
            type="file"
            id="main-file-input"
            accept=".xlsx,.xls,.csv"
            onChange={handleFileInput}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          />
          <div className="py-8 px-4 text-center">
            <div className="w-14 h-14 bg-gradient-to-br from-[#58a6ff]/20 to-[#1f6feb]/10 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-inner">
              <svg className="w-7 h-7 text-[#58a6ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            
            <h3 className="text-white text-base font-semibold mb-2">
              Glissez votre fichier ici
            </h3>
            <p className="text-gray-400 text-sm mb-4">
              ou <label htmlFor="main-file-input" className="text-[#58a6ff] hover:text-[#79c0ff] cursor-pointer font-medium underline underline-offset-2">parcourez vos fichiers</label>
            </p>
            
            <div className="flex items-center justify-center gap-3 text-xs text-gray-500">
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Excel (.xlsx, .xls)
              </span>
              <span className="text-gray-600">•</span>
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                CSV
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
