interface CompilationSummaryProps {
  filesCount: number
  totalLines: number
  duplicates: number
  conflicts: number
  uniqueLines: number
}

export default function CompilationSummary({ 
  filesCount, 
  totalLines, 
  duplicates, 
  conflicts, 
  uniqueLines 
}: CompilationSummaryProps) {
  return (
    <div className="bg-[#161b22] rounded-xl p-8 border border-[#30363d] shadow-lg">
      <h3 className="text-white font-bold mb-8 text-lg">Résumé de la compilation</h3>
      <div className="space-y-5">
        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-base">Fichiers importés</span>
          <span className="text-white font-semibold text-lg">{filesCount}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-base">Lignes uniques</span>
          <span className="text-white font-semibold text-lg">{totalLines.toLocaleString()}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-red-400 text-base">Doublons détectés</span>
          <span className="text-red-400 font-bold text-lg">{duplicates}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-red-400 text-base">Conflits détectés</span>
          <span className="text-red-400 font-bold text-lg">{conflicts}</span>
        </div>
        <div className="flex justify-between items-center pt-5 mt-2 border-t border-[#30363d]">
          <span className="text-gray-300 text-base font-medium">Lignes uniques</span>
          <span className="text-white font-bold text-xl">{uniqueLines.toLocaleString()}</span>
        </div>
      </div>
      <button className="w-full mt-7 px-5 py-3 bg-transparent border-2 border-[#58a6ff] text-[#58a6ff] rounded-lg hover:bg-[#58a6ff]/10 transition-all duration-200 font-medium text-base">
        Voir le rapport de qualité
      </button>
    </div>
  )
}
