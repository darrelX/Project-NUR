export default function Header() {
  return (
    <header className="bg-[#0d1117] border-b border-[#21262d] px-12 py-8">
      <div className="flex items-center gap-6">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center text-white font-bold text-3xl shadow-lg">
          C
        </div>
        <div>
          <h1 className="text-white text-3xl font-bold tracking-tight">CENTRALISATION DES DONNÉES</h1>
          <p className="text-gray-400 text-base mt-2">Compilation & Aperçu du fichier consolidé</p>
        </div>
      </div>
    </header>
  )
}
