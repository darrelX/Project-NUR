import { useState, useEffect } from 'react'
import Header from './components/Header'
import CategorySelector from './components/CategorySelector'
import MainFileUploader from './components/MainFileUploader'
import ConfigForm from './components/ConfigForm'
import FileImportSection from './components/FileImportSection'
import { apiService } from './services/apiService'

interface ProcessedFile {
  name: string
  size: string
  lines: number
  isImported: boolean
  category?: string
}

interface MainFileInfo {
  name: string
  backendPath: string
  sheet: string | number
  lines: number
  size: number
  uploadedAt: string
}

function App() {
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false)
  const [isConfigFormOpen, setIsConfigFormOpen] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('')
  const [mainFileInfo, setMainFileInfo] = useState<MainFileInfo | null>(() => {
    // Charger les infos du fichier principal depuis localStorage
    const saved = localStorage.getItem('mainFileInfo')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        console.log('💾 [App] Info fichier principal restaurée:', parsed.name)
        return parsed
      } catch (e) {
        return null
      }
    }
    return null
  })
  const [files, setFiles] = useState<ProcessedFile[]>(() => {
    // Charger depuis localStorage au démarrage
    const saved = localStorage.getItem('uploadedFiles')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        console.log('💾 [App] Fichiers restaurés depuis localStorage:', parsed.length)
        return parsed
      } catch (e) {
        console.error('❌ [App] Erreur lors de la restauration:', e)
        return []
      }
    }
    return []
  })
  const [isProcessing, setIsProcessing] = useState(false)

  // Sauvegarder mainFileInfo dans localStorage
  useEffect(() => {
    if (mainFileInfo) {
      localStorage.setItem('mainFileInfo', JSON.stringify(mainFileInfo))
      console.log('💾 [App] Info fichier principal sauvegardée')
    } else {
      localStorage.removeItem('mainFileInfo')
    }
  }, [mainFileInfo])

  // Debug: Log quand files change
  useEffect(() => {
    console.log('🔴 [App] État files mis à jour:', files.length, 'fichier(s)', files)
    // Sauvegarder dans localStorage à chaque changement
    localStorage.setItem('uploadedFiles', JSON.stringify(files))
    console.log('💾 [App] Fichiers sauvegardés dans localStorage')
  }, [files])

  const handleSelectCategory = (categoryId: string) => {
    setSelectedCategory(categoryId)
    setIsCategoryModalOpen(false)
    setIsConfigFormOpen(true)
  }

  const handleMainFileSelect = async (file: File) => {
    console.log('🟢 [App] Fichier principal sélectionné:', file.name, file.size, 'bytes')
    try {
      setIsProcessing(true)
      
      // Upload vers le backend et charger l'aperçu
      console.log('📤 [App] Upload en cours...')
      const uploadResult = await apiService.uploadMainFile(file)
      console.log('✅ [App] Upload réussi:', uploadResult)
      
      console.log('📥 [App] Vérification du fichier...')
      const status = await apiService.getData()
      console.log('✅ [App] Statut:', status)
      
      // Stocker les informations du fichier principal globalement
      const fileInfo: MainFileInfo = {
        name: uploadResult.filename,
        backendPath: status.file_path || '',
        sheet: uploadResult.sheet_name || '0',
        lines: uploadResult.lines,
        size: uploadResult.size,
        uploadedAt: new Date().toISOString()
      }
      console.log('🔵 [App] Création des infos fichier principal:', fileInfo)
      
      // IMPORTANT: Mettre à jour le state AVANT de terminer le processing
      setMainFileInfo(fileInfo)
      setFiles([]) // Réinitialiser la liste des fichiers traités
      setIsProcessing(false)
      
      console.log('✨ [App] Fichier principal configuré globalement')
      
      if (status.file_exists) {
        setTimeout(() => {
          alert(`✅ Fichier chargé : ${uploadResult.filename}\n${uploadResult.lines} lignes, ${(uploadResult.size / 1024).toFixed(1)} KB\n📁 Chemin: ${status.file_path}`)
        }, 100)
      }
      
    } catch (error: any) {
      console.error('🔴 [App] ERREUR complète:', error)
      console.error('🔴 [App] Stack:', error.stack)
      setIsProcessing(false)
      alert(`❌ Erreur d'upload : ${error.message}\n\nVérifiez que le backend est lancé sur http://localhost:5000`)
    }
  }

  const handleDeleteFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleConfigSubmit = async (config: any, file: File) => {
    if (!mainFileInfo) {
      alert('Veuillez d\'abord charger le fichier principal')
      return
    }

    try {
      setIsProcessing(true)
      setIsConfigFormOpen(false)

      let result: any
      switch (selectedCategory) {
        case 'CellDown':
          console.log('Darrel 🔵 [App] Traitement CellDown avec config:', file, config)
          result = await apiService.processCelldown(file, config)
          break
        case 'OCM RAN':
          result = await apiService.processXlookup(file, config)
          break
        case 'Ticket':
          result = await apiService.processTicket(file, config)
          break
        case 'Personnalized':
          result = await apiService.processTicket(file, config)
          break
        default:
          console.log('🔵 [App] Traitement Xlookup avec config:', file, config  )
          result = await apiService.processXlookup(file, config)
      }

      // Vérifier que le fichier est sauvegardé
      const status = await apiService.getData()
      console.log('📊 [App] Statut après traitement:', status)

      const processedFile: ProcessedFile = {
        name: file.name,
        size: (file.size / (1024 * 1024)).toFixed(1) + ' MB',
        lines: result.lines,
        isImported: true,
        category: selectedCategory
      }
      setFiles(prev => [...prev, processedFile])
      
      alert(`✅ Traitement terminé : ${result.lines} lignes, ${result.columns?.length || 0} colonnes\n💡 Fichier mis à jour : ${status.message}`)
    } catch (error: any) {
      alert(`❌ Erreur : ${error.message}`)
    } finally {
      setIsProcessing(false)
    }
  }

  const loadData = async () => {
    if (!mainFileInfo) {
      alert('Aucun fichier principal chargé')
      return
    }
    
    try {
      const status = await apiService.getData()
      if (status.file_exists) {
        alert(`✅ ${status.message}\n\n💡 Pour voir les données, exportez le fichier`)
      } else {
        alert(`⚠️ ${status.message}`)
      }
    } catch (error) {
      console.error('Failed to check file:', error)
      alert('Erreur lors de la vérification du fichier')
    }
  }

  const handleExport = async () => {
    if (!mainFileInfo) {
      alert('Aucun fichier à exporter')
      return
    }
    
    try {
      setIsProcessing(true)
      console.log('🔵 [Export] Téléchargement depuis le backend...')
      await apiService.exportFile()
      alert('✅ Fichier exporté avec succès')
    } catch (error: any) {
      console.error('🔴 [Export] Erreur:', error)
      alert(`❌ Erreur d'export : ${error.message}`)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0d1117] to-[#0a0c10]">
      <Header />
      
      <main className="px-4 sm:px-6 lg:px-8 py-6 lg:py-8 max-w-[1800px] mx-auto">
        <div className="mb-8 lg:mb-10">
          <MainFileUploader 
            onFileSelect={handleMainFileSelect} 
            fileInfo={mainFileInfo}
            onClear={() => {
              setMainFileInfo(null)
              localStorage.removeItem('mainFileInfo')
              localStorage.removeItem('uploadedFiles')
              console.log('🗑️ [App] Fichier principal et fichiers traités supprimés')
            }}
          />
        </div>

        {/* Section Importation + Résumé */}
        <FileImportSection
          files={files}
          mainFileInfo={mainFileInfo}
          isProcessing={isProcessing}
          onAddFile={() => setIsCategoryModalOpen(true)}
          onDeleteFile={handleDeleteFile}
        />

        {/* Section Actions rapides */}
        <div className="bg-[#161b22] rounded-2xl border border-[#30363d] shadow-xl overflow-hidden">
          <div className="p-5 lg:p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h2 className="text-white text-xl font-semibold tracking-tight">
                  Actions sur le fichier consolidé
                </h2>
                <p className="text-gray-400 text-sm mt-1">
                  {mainFileInfo ? `Fichier actif : ${mainFileInfo.name}` : 'Aucun fichier chargé'}
                </p>
              </div>
              <div className="flex gap-3">
                <button 
                  onClick={loadData}
                  disabled={!mainFileInfo}
                  className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-lg text-sm font-medium transition-all duration-200 shadow-md shadow-green-500/20 hover:shadow-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Vérifier le statut
                </button>
                <button 
                  onClick={handleExport}
                  disabled={!mainFileInfo}
                  className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg text-sm font-medium transition-all duration-200 shadow-md shadow-blue-500/20 hover:shadow-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Exporter Excel
                </button>
              </div>
            </div>
            
            {/* Statistiques rapides */}
            {files.length > 0 && (
              <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-[#0d1117]/50 rounded-lg p-4 border border-[#30363d]">
                  <p className="text-gray-400 text-xs font-medium mb-1">Fichiers traités</p>
                  <p className="text-white text-2xl font-bold">{files.length}</p>
                </div>
                <div className="bg-[#0d1117]/50 rounded-lg p-4 border border-[#30363d]">
                  <p className="text-gray-400 text-xs font-medium mb-1">Total lignes</p>
                  <p className="text-white text-2xl font-bold">{files.reduce((sum, f) => sum + f.lines, 0).toLocaleString()}</p>
                </div>
                <div className="bg-[#0d1117]/50 rounded-lg p-4 border border-[#30363d]">
                  <p className="text-gray-400 text-xs font-medium mb-1">Celldown</p>
                  <p className="text-white text-2xl font-bold">{files.filter(f => f.category === 'celldown').length}</p>
                </div>
                <div className="bg-[#0d1117]/50 rounded-lg p-4 border border-[#30363d]">
                  <p className="text-gray-400 text-xs font-medium mb-1">Transmission</p>
                  <p className="text-white text-2xl font-bold">{files.filter(f => f.category === 'transmission').length}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <CategorySelector
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        onSelectCategory={handleSelectCategory}
      />

      {isConfigFormOpen && (
        <ConfigForm
          category={selectedCategory}
          onSubmit={handleConfigSubmit}
          onCancel={() => setIsConfigFormOpen(false)}
        />
      )}

      {isProcessing && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-[#161b22] rounded-2xl border border-[#30363d] p-8 flex flex-col items-center gap-4">
            <div className="w-16 h-16 border-4 border-[#58a6ff] border-t-transparent rounded-full animate-spin"></div>
            <p className="text-white text-lg font-semibold">Traitement en cours...</p>
            <p className="text-gray-400 text-sm">Veuillez patienter</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
