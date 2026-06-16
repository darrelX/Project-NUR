// ConfigForm.tsx
import { useState, useRef } from 'react'
import * as XLSX from 'xlsx'

type ConfigData = Record<string, any>

interface ConfigFormProps {
  category: string
  onSubmit: (config: ConfigData, file: File) => void
  onCancel: () => void
}

export default function ConfigForm({ category, onSubmit, onCancel }: ConfigFormProps) {
  const [configValues, setConfigValues] = useState<ConfigData>({})
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [sheetNames, setSheetNames] = useState<string[]>([])
  const [selectedSheet, setSelectedSheet] = useState<string>('')
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleChange = (key: string, value: string) => {
    setConfigValues(prev => ({ ...prev, [key]: value }))
  }

  const handleFileSelect = async (file: File) => {
    if (!file) return
    
    // Vérifier que c'est un fichier Excel ou CSV
    const validExtensions = ['.xlsx', '.xls', '.csv']
    const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))
    
    if (!hasValidExtension) {
      alert('Veuillez sélectionner un fichier Excel (.xlsx, .xls) ou CSV')
      return
    }

    setUploadedFile(file)

    // Lire les feuilles Excel si c'est un fichier Excel
    if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
      try {
        const arrayBuffer = await file.arrayBuffer()
        const workbook = XLSX.read(arrayBuffer, { type: 'array' })
        const sheets = workbook.SheetNames
        setSheetNames(sheets)
        
        // Sélectionner automatiquement la première feuille
        if (sheets.length > 0) {
          setSelectedSheet(sheets[0])
          setConfigValues(prev => ({ ...prev, target_sheet_name: sheets[0] }))
        }
      } catch (error) {
        console.error('Erreur lors de la lecture du fichier:', error)
        alert('Erreur lors de la lecture des feuilles Excel')
      }
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleSubmit = () => {
    if (!uploadedFile) {
      alert('Veuillez sélectionner un fichier')
      return
    }

    // Validation spécifique pour CellDown
    if (category === 'CellDown') {
      if (!configValues.date_str || configValues.date_str.trim() === '') {
        alert('⚠️ La date de référence est obligatoire pour CellDown')
        return
      }
    }

    // Construire la config finale selon la catégorie
    // Chaque catégorie doit envoyer UNIQUEMENT les champs définis dans apiService
    let finalConfig: ConfigData = {}

    switch (category) {
      case 'CellDown':
        // Structure pour CellDown (selon apiService.processCelldown)
        // Champs requis: date_str
        // Champs optionnels: reference_name, reference_date, source_sheet_path
        finalConfig = {
          date_str: configValues.date_str || '',
          reference_name: configValues.reference_name || '',
          reference_date: configValues.reference_date || '',
          source_sheet_path: configValues.source_sheet_path || 'Sheet1',
        }
        // Note: colown_key_path_source, target_key_column, etc. sont gérés par defaultConfig dans apiService
        break

      case 'OCM RAN':
        // Structure pour Xlookup (selon apiService.processXlookup)
        finalConfig = {
          target_sheet_name: selectedSheet || '',
          result_column_name: configValues.result_column_name || '',
          reference_name: configValues.reference_name || '',
          reference_date: configValues.reference_date || '',
        }
        break

      case 'Ticket':
      case 'Personnalized':
        // Structure pour Ticket (selon apiService.processTicket)
        finalConfig = {
          target_sheet_name: selectedSheet || '',
          join_separator: configValues.join_separator || '..',
          reference_name: configValues.reference_name || '',
          reference_date: configValues.reference_date || '',
        }
        break

      default:
        // Cas par défaut: structure basique avec target_sheet_name
        finalConfig = {
          target_sheet_name: selectedSheet || '',
          ...configValues
        }
    }

    console.log('📤 [ConfigForm] Soumission config pour', category, ':', finalConfig)
    onSubmit(finalConfig, uploadedFile)
  }

  const renderFields = () => {
    console.log("Rendering fields for category:", category)
    switch (category) {
      case 'CellDown':
        return (
          <>
            {console.log("Rendu avec :", category)}
            {/* Champ PRINCIPAL: Date String - Date de référence */}
            <div>
              <label className="block text-white text-sm font-medium mb-2">
                Date de référence <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                value={configValues.date_str || ''}
                onChange={(e) => handleChange('date_str', e.target.value)}
                placeholder="YYYY-MM-DD (Ex: 2024-01-15)"
                className="w-full bg-[#161b22] text-white px-4 py-2 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20"
              />
              <p className="text-gray-400 text-xs mt-1">
                Date qui apparaîtra dans la colonne résultante (texte brut, pas de conversion)
              </p>
            </div>

            {/* === Paramètres optionnels === */}
            <div className="border-t border-[#21262d] pt-4 mt-2">
              <p className="text-gray-500 text-xs uppercase font-semibold mb-3">Paramètres optionnels</p>
              
              {/* Champ optionnel: Reference Name */}
              <div className="mb-4">
                <label className="block text-white text-sm font-medium mb-2">
                  Nom de référence (optionnel)
                </label>
                <input
                  type="text"
                  value={configValues.reference_name || ''}
                  onChange={(e) => handleChange('reference_name', e.target.value)}
                  placeholder="Ex: IHS, Camusat, OCM... (vide = auto-génération)"
                  className="w-full bg-[#161b22] text-white px-4 py-2 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20"
                />
                <p className="text-gray-400 text-xs mt-1">
                  Nom de la colonne dans le fichier consolidé. Si vide, sera généré automatiquement.
                </p>
              </div>

              {/* Champ optionnel: Source Sheet Path */}
              <div>
                <label className="block text-white text-sm font-medium mb-2">
                  Feuille source (optionnel)
                </label>
                <input
                  type="text"
                  value={configValues.source_sheet_path || ''}
                  onChange={(e) => handleChange('source_sheet_path', e.target.value)}
                  placeholder="Sheet1"
                  className="w-full bg-[#161b22] text-white px-4 py-2 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20"
                />
                <p className="text-gray-400 text-xs mt-1">
                  Nom de la feuille dans le fichier principal (défaut: Sheet1)
                </p>
              </div>
            </div>
          </>
        )

      case 'OCM RAN':
        return (
          <>
            {console.log("Rendu avec :", category)}
            <div>
              <label className="block text-white text-sm font-medium mb-2">
                Result Column Name (optionnel)
              </label>
              <input
                type="text"
                value={configValues.result_column_name || ''}
                onChange={(e) => handleChange('result_column_name', e.target.value)}
                placeholder="Laisser vide pour utiliser le nom du fichier"
                className="w-full bg-[#161b22] text-white px-4 py-2 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20"
              />
            </div>
          </>

        )
      case 'Ticket':
        return (
          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Join Separator (optionnel)
            </label>
            <input
              type="text"
              value={configValues.join_separator || '..'}
              onChange={(e) => handleChange('join_separator', e.target.value)}
              placeholder="Défaut: .."
              className="w-full bg-[#161b22] text-white px-4 py-2 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20"
            />
          </div>
        )

      case 'Personnalized':
        return (
          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Custom Configuration (JSON)
            </label>
            <textarea
              rows={4}
              value={JSON.stringify(configValues, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value)
                  setConfigValues(parsed)
                } catch {
                  setConfigValues({ raw: e.target.value })
                }
              }}
              placeholder='{"key": "value"}'
              className="w-full bg-[#161b22] text-white px-4 py-2 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20 font-mono text-sm"
            />
            <p className="text-gray-400 text-xs mt-2">
              Enter valid JSON or any custom configuration
            </p>
          </div>
        )

      default:
        return <p className="text-gray-400">Unknown category</p>
    }
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-6">
      <div className="bg-[#0d1117] rounded-2xl w-full max-w-2xl border border-[#30363d] overflow-hidden shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-8 py-6 border-b border-[#21262d] bg-[#161b22] sticky top-0 z-10">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-white text-xl font-bold">
                Configuration pour {category}
              </h2>
              <p className="text-gray-400 text-sm mt-2">
                Importez un fichier et configurez les paramètres
              </p>
            </div>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-white hover:bg-[#30363d] rounded-lg p-2 transition-all"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="px-8 py-6 bg-[#0d1117] space-y-6">
          {/* Upload Section */}
          <div>
            <label className="block text-white text-sm font-medium mb-3">
              Fichier à traiter *
            </label>
            
            {!uploadedFile ? (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-xl transition-all duration-300 cursor-pointer ${
                  isDragging
                    ? 'border-[#58a6ff] bg-[#58a6ff]/5 scale-[1.02]'
                    : 'border-[#30363d] hover:border-[#58a6ff] hover:bg-[#0d1117]/50'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={handleFileInput}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className="py-8 px-4 text-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#58a6ff]/20 to-[#1f6feb]/10 rounded-xl flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-[#58a6ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  
                  <h3 className="text-white text-sm font-semibold mb-1">
                    Glissez votre fichier ici
                  </h3>
                  <p className="text-gray-400 text-xs mb-3">
                    ou <span className="text-[#58a6ff] hover:text-[#79c0ff] cursor-pointer font-medium">parcourez vos fichiers</span>
                  </p>
                  
                  <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                    <span>Excel (.xlsx, .xls)</span>
                    <span className="text-gray-600">•</span>
                    <span>CSV</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-10 h-10 bg-gradient-to-br from-green-500/20 to-green-600/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-white text-sm font-medium truncate">{uploadedFile.name}</p>
                      <p className="text-gray-400 text-xs mt-0.5">
                        {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setUploadedFile(null)
                      setSheetNames([])
                      setSelectedSheet('')
                      if (fileInputRef.current) fileInputRef.current.value = ''
                    }}
                    className="text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg p-2 transition-all flex-shrink-0"
                    title="Supprimer le fichier"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Sheet Selector */}
          {sheetNames.length > 0 && (
            <div>
              <label className="block text-white text-sm font-medium mb-2">
                Feuille Excel *
              </label>
              <select
                value={selectedSheet}
                onChange={(e) => {
                  setSelectedSheet(e.target.value)
                  handleChange('target_sheet_name', e.target.value)
                }}
                className="w-full bg-[#161b22] text-white px-4 py-2.5 rounded-lg border border-[#30363d] focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff]/20"
              >
                {sheetNames.map((sheet) => (
                  <option key={sheet} value={sheet}>
                    {sheet}
                  </option>
                ))}
              </select>
              <p className="text-gray-400 text-xs mt-2">
                {sheetNames.length} feuille(s) détectée(s) dans le fichier
              </p>
            </div>
          )}

          {/* Configuration Fields */}
          <div className="space-y-4">
            {category === 'CellDown' ? (
              <h3 className="text-white text-sm font-semibold">Configuration CellDown</h3>
            ) : (
              <h3 className="text-white text-sm font-semibold">Paramètres optionnels</h3>
            )}
            {renderFields()}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-4 pt-4 border-t border-[#21262d]">
            <button
              onClick={onCancel}
              className="px-5 py-2 text-gray-300 border border-[#30363d] rounded-lg hover:bg-[#21262d] transition-all"
            >
              Annuler
            </button>
            <button
              onClick={handleSubmit}
              disabled={!uploadedFile}
              className="px-5 py-2 bg-[#238636] text-white rounded-lg hover:bg-[#2ea043] disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md"
            >
              Valider et traiter
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}