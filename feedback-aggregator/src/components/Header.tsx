interface HeaderProps {
  onAddSourceFile: () => void
}

export default function Header({ onAddSourceFile }: HeaderProps) {
  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 px-6 py-4 w-full">
        <h1 className="text-3xl font-light tracking-tight text-slate-800 flex items-center gap-2">
          Breakdown
          <span className="text-xs font-normal text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">v2.0</span>
        </h1>
        <button
          onClick={onAddSourceFile}
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all shadow-sm hover:shadow-md"
        >
          <span className="text-xl leading-5">+</span>
          <span className="font-medium">Ajouter un fichier</span>
        </button>
      </div>
    </header>
  )
}
