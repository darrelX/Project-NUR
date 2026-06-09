import { useState } from 'react'

interface Category {
  id: string
  name: string
  description: string
  filesCount: number
  icon: string
  color: string
}

interface CategorySelectorProps {
  isOpen: boolean
  onClose: () => void
  onSelectCategory: (categoryId: string) => void
}

const categories: Category[] = [
  {
    id: 'celldown',
    name: 'Celldown',
    description: 'Données liées aux incidents de type cellule down (ID, alarme, logs...)',
    filesCount: 12,
    icon: '📱',
    color: 'bg-blue-600'
  },
  {
    id: 'transmission',
    name: 'Transmission',
    description: 'Données de transmission (microwave, fibre, backhaul...)',
    filesCount: 8,
    icon: '📡',
    color: 'bg-green-600'
  },
  {
    id: 'infra',
    name: 'Infra',
    description: 'Données d\'infrastructure (power, batteries, rectifiers...)',
    filesCount: 6,
    icon: '🏗️',
    color: 'bg-orange-600'
  },
  {
    id: 'sites',
    name: 'Sites',
    description: 'Informations générales sur les sites (ID, coordonnées...)',
    filesCount: 5,
    icon: '📍',
    color: 'bg-purple-600'
  },
  {
    id: 'autres',
    name: 'Autres',
    description: 'Autres types de données',
    filesCount: 3,
    icon: '📋',
    color: 'bg-gray-600'
  }
]

export default function CategorySelector({ isOpen, onClose, onSelectCategory }: CategorySelectorProps) {
  const [searchQuery, setSearchQuery] = useState('')

  if (!isOpen) return null

  const filteredCategories = categories.filter(cat =>
    cat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cat.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 animate-fadeIn p-6" onClick={onClose}>
      <div 
        className="bg-[#0d1117] rounded-2xl w-full max-w-2xl border border-[#30363d] overflow-hidden shadow-2xl animate-slideUp"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-8 py-6 border-b border-[#21262d] bg-[#161b22]">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-white text-xl font-bold">Choisir une catégorie</h2>
              <p className="text-gray-400 text-sm mt-2">Sélectionnez la catégorie pour vos fichiers</p>
            </div>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white hover:bg-[#30363d] rounded-lg p-2 transition-all duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="px-8 py-6 bg-[#0d1117]">
          <div className="relative">
            <input
              type="text"
              placeholder="Rechercher une catégorie..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#161b22] text-white px-5 py-3 pl-12 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20 transition-all text-base"
            />
            <svg 
              className="w-5 h-5 text-gray-500 absolute left-4 top-1/2 -translate-y-1/2" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Categories List */}
        <div className="px-8 pb-8 max-h-96 overflow-y-auto bg-[#0d1117]">
          <div className="space-y-4">
            {filteredCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => {
                  onSelectCategory(category.id)
                  onClose()
                }}
                className="w-full flex items-center gap-5 p-5 bg-[#161b22] hover:bg-[#1c2128] rounded-xl border border-[#30363d] hover:border-[#58a6ff] transition-all duration-200 text-left group"
              >
                <div className={`w-16 h-16 ${category.color} rounded-xl flex items-center justify-center text-3xl flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform duration-200`}>
                  {category.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold text-base">{category.name}</h3>
                  <p className="text-gray-400 text-sm truncate mt-1">{category.description}</p>
                </div>
                <div className="text-[#58a6ff] text-sm font-semibold flex-shrink-0 bg-[#58a6ff]/10 px-4 py-2 rounded-full">
                  {category.filesCount} fichiers
                </div>
              </button>
            ))}
          </div>
          {filteredCategories.length === 0 && (
            <div className="text-center py-12 text-gray-400 text-base">
              Aucune catégorie trouvée
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
