export default function PreviewArea() {
  return (
    <div className="hidden lg:flex-1 lg:flex items-center justify-center bg-white/40 rounded-2xl border border-dashed border-gray-200">
      <div className="text-center text-gray-400">
        <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <p className="text-sm">Zone d'aperçu global</p>
        <p className="text-xs">(réservée pour des graphiques ou logs)</p>
      </div>
    </div>
  )
}
