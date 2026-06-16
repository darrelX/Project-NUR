interface FileCardProps {
  name: string
  size: string
  lines: number
  isImported: boolean
  onDelete?: () => void
}

export default function FileCard({ name, size, lines, isImported, onDelete }: FileCardProps) {
  return (
    <div className="bg-[#161b22] rounded-xl p-7 border border-[#30363d] hover:border-[#58a6ff] hover:shadow-lg hover:shadow-blue-500/10 transition-all duration-200 relative group">      {onDelete && (
        <button
          onClick={onDelete}
          className="absolute top-3 right-3 w-8 h-8 bg-red-500/10 hover:bg-red-500/20 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-200"
          title="Supprimer"
        >
          <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}      <div className="flex items-start gap-5">
        <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-green-700 rounded-lg flex items-center justify-center flex-shrink-0 shadow-md">
          <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-semibold truncate text-base">{name}</h3>
          <p className="text-gray-400 text-sm mt-2">{size}</p>
          <div className="flex items-center gap-2 mt-3">
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
            <span className="text-gray-400 text-sm">{lines.toLocaleString()} lignes</span>
          </div>
          {isImported && (
            <div className="flex items-center gap-2 mt-3 text-green-400 text-sm font-medium">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Importé</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
