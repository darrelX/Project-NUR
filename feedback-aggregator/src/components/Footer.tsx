import type { ProgressStats } from '../types'

interface FooterProps {
  progressStats: ProgressStats
  onCompile: () => void
}

export default function Footer({ progressStats, onCompile }: FooterProps) {
  const { totalIssues, selectedIssues } = progressStats
  const progressPercent = totalIssues === 0 ? 0 : (selectedIssues / totalIssues) * 100

  return (
    <footer className="border-t border-gray-200 bg-white/90 backdrop-blur-sm sticky bottom-0 z-10 w-full">
      <div className="px-6 py-4 flex flex-col sm:flex-row items-center gap-4 w-full">
        <div className="flex items-center gap-4 w-full sm:w-auto flex-1">
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="whitespace-nowrap">
              {selectedIssues} / {totalIssues} éléments
            </span>
          </div>
          <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden shadow-inner">
            <div
              className="h-full bg-gradient-to-r from-green-500 via-emerald-500 to-blue-500 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <span className="text-sm font-mono font-semibold text-slate-600 min-w-[3rem]">
            {Math.round(progressPercent)}%
          </span>
        </div>
        <button
          onClick={onCompile}
          className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-8 py-2.5 rounded-xl text-sm font-medium transition-all shadow-md hover:shadow-lg disabled:opacity-50"
        >
          Lancer la compilation
        </button>
      </div>
    </footer>
  )
}
