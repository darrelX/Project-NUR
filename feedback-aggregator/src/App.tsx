import { useState } from 'react'
import Header from './components/Header'
import FileCard from './components/FileCard'
import CompilationSummary from './components/CompilationSummary'
import CategorySelector from './components/CategorySelector'
import DataTable from './components/DataTable'

function App() {
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false)
  const [showDuplicates, setShowDuplicates] = useState(false)
  const [showConflicts, setShowConflicts] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)

  // Données exemple (à remplacer par vos vraies données)
  const files = [
    { name: 'Cell2TE_Jan.xlsx', size: '1.2 MB', lines: 1345, isImported: true },
    { name: 'Transmission_Nokia.xlsx', size: '980 KB', lines: 860, isImported: true },
    { name: 'Infra_Huawei.xlsx', size: '1.5 MB', lines: 1120, isImported: true }
  ]

  const sampleData = [
    {
      siteId: 'BDC1234',
      owner: 'IHS',
      comments: 'grid only || power issue || FME on site awaiting Camusat feedback',
      topology: 'RAN / Power',
      rca: 'Power Issue',
      subRca: 'Default GE',
      status: 'Open',
      quality: 95
    },
    {
      siteId: 'NB05678',
      owner: 'ZTE',
      comments: 'Transmission degradation || microwave link unstable || high BER',
      topology: 'Transmission',
      rca: 'Transmission Issue',
      subRca: 'MW Link Failure',
      status: 'In Progress',
      quality: 90
    },
    {
      siteId: 'KGL9012',
      owner: 'Huawei',
      comments: 'RRU Not reachable || no alarm from site || fixer ok',
      topology: 'RAN',
      rca: 'Hardware Issue',
      subRca: 'RRU Failure',
      status: 'Open',
      quality: 88
    },
    {
      siteId: 'FTL3456',
      owner: 'Ericsson',
      comments: 'Site down || no power || battery flat || rectifier failure',
      topology: 'Power',
      rca: 'Power Issue',
      subRca: 'Rectifier Failure',
      status: 'Resolved',
      quality: 92
    },
    {
      siteId: 'BJA7890',
      owner: 'IHS',
      comments: 'VSAT link down || rain fade (suspected) || backup link ok',
      topology: 'Backhaul',
      rca: 'Transmission Issue',
      subRca: 'VSAT Degradation',
      status: 'Open',
      quality: 85
    }
  ]

  const handleSelectCategory = (categoryId: string) => {
    console.log('Selected category:', categoryId)
    // Ici vous pouvez gérer la logique d'importation de fichiers
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0d1117] to-[#0a0c10]">
      <Header />
      
      <main className="px-4 sm:px-6 lg:px-8 py-6 lg:py-8 max-w-[1800px] mx-auto">
        {/* Section Importation + Résumé */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 mb-8 lg:mb-10">
          {/* Bloc importation */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-white text-xl font-semibold tracking-tight">
                Importation des fichiers
              </h2>
              <span className="text-xs text-gray-400 bg-[#1c2128] px-3 py-1 rounded-full">
                {files.length} fichier(s) chargé(s)
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 lg:gap-5">
              {files.map((file, index) => (
                <FileCard key={index} {...file} />
              ))}
              
              {/* Carte d'ajout */}
              <button
                onClick={() => setIsCategoryModalOpen(true)}
                className="group bg-[#161b22] rounded-xl border-2 border-dashed border-[#30363d] hover:border-[#58a6ff] hover:bg-[#1c2128] transition-all duration-200 p-6 flex flex-col items-center justify-center gap-3 min-h-[180px] cursor-pointer"
              >
                <div className="w-12 h-12 bg-[#58a6ff]/10 rounded-xl flex items-center justify-center group-hover:scale-110 group-hover:bg-[#58a6ff]/20 transition-all duration-200">
                  <svg className="w-6 h-6 text-[#58a6ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <div className="text-center">
                  <p className="text-[#58a6ff] font-medium text-sm group-hover:font-semibold transition-all">
                    Importer un fichier
                  </p>
                  <p className="text-gray-500 text-xs mt-1">Excel / CSV</p>
                </div>
              </button>
            </div>
          </div>

          {/* Résumé */}
          <div className="mt-2 lg:mt-0">
            <CompilationSummary
              filesCount={3}
              totalLines={3345}
              duplicates={124}
              conflicts={37}
              uniqueLines={3184}
            />
          </div>
        </div>

        {/* Section Aperçu consolidé */}
        <div className="bg-[#161b22] rounded-2xl border border-[#30363d] shadow-xl overflow-hidden">
          <div className="p-5 lg:p-6 border-b border-[#21262d]">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <h2 className="text-white text-xl font-semibold tracking-tight">
                Aperçu du fichier consolidé
              </h2>
              <button className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg text-sm font-medium transition-all duration-200 shadow-md shadow-blue-500/20 hover:shadow-blue-500/30">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Ouvrir dans Excel
              </button>
            </div>
          </div>

          {/* Filtres et recherche */}
          <div className="p-5 lg:p-6 border-b border-[#21262d] bg-[#0d1117]/30">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="relative flex-1 min-w-[240px]">
                <input
                  type="text"
                  placeholder="Rechercher un site, owner, RCA..."
                  className="w-full bg-[#0d1117] text-white text-sm px-4 py-2.5 pl-10 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20 transition-all placeholder:text-gray-500"
                />
                <svg className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <button 
                  onClick={() => setShowDuplicates(!showDuplicates)}
                  className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    showDuplicates 
                      ? 'bg-[#58a6ff]/10 border border-[#58a6ff] text-[#58a6ff]' 
                      : 'bg-[#0d1117] text-gray-300 border border-[#30363d] hover:border-[#58a6ff] hover:text-white'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  Doublons
                </button>
                <button 
                  onClick={() => setShowConflicts(!showConflicts)}
                  className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    showConflicts 
                      ? 'bg-red-500/10 border border-red-500 text-red-400' 
                      : 'bg-[#0d1117] text-gray-300 border border-[#30363d] hover:border-red-500 hover:text-red-400'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Conflits
                </button>
                <button className="inline-flex items-center gap-2 px-3.5 py-2 bg-[#0d1117] text-gray-300 rounded-lg border border-[#30363d] hover:border-[#58a6ff] hover:text-white transition-all duration-200 text-sm font-medium">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  Filtres
                </button>
              </div>
            </div>
          </div>

          {/* Tableau avec scroll horizontal */}
          <div className="overflow-x-auto">
            <div className="min-w-[800px]">
              <DataTable 
                data={sampleData} 
                showDuplicates={showDuplicates}
                showConflicts={showConflicts}
              />
            </div>
          </div>

          {/* Pagination */}
          <div className="p-5 lg:p-6 border-t border-[#21262d] bg-[#0d1117]/20">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="text-gray-400 text-sm">
                Affichage 1 à 5 sur <span className="text-white font-semibold">3,184</span> lignes
              </div>
              <div className="flex items-center justify-center gap-1.5">
                <button className="p-2 bg-[#0d1117] text-gray-400 rounded-lg border border-[#30363d] hover:border-[#58a6ff] hover:text-white transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                {[1, 2, 3, 4, 5, '...', 637].map((page, index) => (
                  <button
                    key={index}
                    onClick={() => typeof page === 'number' && setCurrentPage(page)}
                    className={`min-w-[36px] h-9 px-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      page === currentPage
                        ? 'bg-[#58a6ff] text-white shadow-md shadow-[#58a6ff]/20'
                        : typeof page === 'number'
                        ? 'bg-[#0d1117] text-gray-300 hover:bg-[#1c2128] hover:text-white border border-[#30363d] hover:border-[#58a6ff]'
                        : 'bg-transparent text-gray-500 cursor-default'
                    }`}
                    disabled={typeof page !== 'number'}
                  >
                    {page}
                  </button>
                ))}
                <button className="p-2 bg-[#0d1117] text-gray-400 rounded-lg border border-[#30363d] hover:border-[#58a6ff] hover:text-white transition-all duration-200">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
              <div className="flex items-center justify-end gap-3 text-sm">
                <span className="text-gray-400">Lignes par page :</span>
                <select className="bg-[#0d1117] text-white px-3 py-1.5 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20 cursor-pointer text-sm">
                  <option>10</option>
                  <option>25</option>
                  <option>50</option>
                  <option>100</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Modal (inchangé) */}
      <CategorySelector
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        onSelectCategory={handleSelectCategory}
      />
    </div>
  )
}

export default App