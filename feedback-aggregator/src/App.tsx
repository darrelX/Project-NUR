import { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import FileList from './components/FileList'
import FileDetails from './components/FileDetails'
import PreviewArea from './components/PreviewArea'
import Footer from './components/Footer'
import type { FileItem, FileMapping, PreviewChecks } from './types'
import { generatePreviewItems, initPreviewChecks } from './utils/fileHelpers'
import { defaultMapping } from './constants'
import { fileAnalyzerService } from './services/fileAnalyzer'
import { compilationService } from './services/compilationService'

function App() {
  // État des fichiers - Commence vide, les fichiers seront chargés dynamiquement
  const [files, setFiles] = useState<FileItem[]>([])

  const [selectedFileId, setSelectedFileId] = useState<string>('')

  const [fileMappings, setFileMappings] = useState<Record<string, FileMapping>>({})
  const [filePreviewChecks, setFilePreviewChecks] = useState<Record<string, PreviewChecks>>({})

  // Initialiser mappings et previews au premier chargement
  useEffect(() => {
    const initialMappings: Record<string, FileMapping> = {}
    const initialPreviews: Record<string, PreviewChecks> = {}

    files.forEach((file) => {
      if (!fileMappings[file.id]) {
        initialMappings[file.id] = { ...defaultMapping }
      }
      if (!filePreviewChecks[file.id]) {
        initialPreviews[file.id] = initPreviewChecks(file.name)
      }
    })

    if (Object.keys(initialMappings).length > 0) {
      setFileMappings((prev) => ({ ...prev, ...initialMappings }))
    }
    if (Object.keys(initialPreviews).length > 0) {
      setFilePreviewChecks((prev) => ({ ...prev, ...initialPreviews }))
    }
  }, [files]) // Se déclenche uniquement quand la liste des fichiers change

  // Synchroniser les previews quand le nom d'un fichier change (cas d'ajout)
  useEffect(() => {
    files.forEach((file) => {
      if (filePreviewChecks[file.id] === undefined) {
        setFilePreviewChecks((prev) => ({
          ...prev,
          [file.id]: initPreviewChecks(file.name),
        }))
      }
    })
  }, [files, filePreviewChecks])

  // Gestionnaires
  const selectFile = (id: string) => {
    setSelectedFileId(id)
  }

  const updateMapping = (mapping: FileMapping) => {
    setFileMappings((prev) => ({
      ...prev,
      [selectedFileId]: mapping,
    }))
  }

  const togglePreviewItem = (issueId: string) => {
    setFilePreviewChecks((prev) => ({
      ...prev,
      [selectedFileId]: {
        ...prev[selectedFileId],
        [issueId]: !prev[selectedFileId]?.[issueId],
      },
    }))
  }

  // Gérer la sélection de fichiers depuis l'explorateur Windows
const handleFileSelect = async (
  event: React.ChangeEvent<HTMLInputElement>
) => {
  const input = event.currentTarget
  const selectedFiles = input.files

  if (!selectedFiles?.length) return

  try {
    for (const file of Array.from(selectedFiles)) {
      const newId = crypto.randomUUID()

      const newFile: FileItem = {
        id: newId,
        name: file.name,
        statusColor: 'bg-yellow-400',
        availableSheets: [],
      }

      setFiles((prev) => [...prev, newFile])
      setSelectedFileId(newId)
      setFileMappings((prev) => ({
        ...prev,
        [newId]: { ...defaultMapping },
      }))
      setFilePreviewChecks((prev) => ({
        ...prev,
        [newId]: initPreviewChecks(file.name),
      }))

      const uploadResult = await compilationService.uploadFile(file)

      if (!uploadResult.success) {
        throw new Error(uploadResult.error || "Échec de l'upload")
      }

      if (!uploadResult.filePath) {
        throw new Error("Le backend n'a pas renvoyé de filePath")
      }

      

      const metadata = await fileAnalyzerService.analyzeFile(uploadResult.filePath)

      console.log("Essayons voir");

      if (!metadata) {
        throw new Error("Impossible d'analyser le fichier")
      }

      setFiles((prev) =>
        prev.map((f) =>
          f.id === newId
            ? {
                ...f,
                filePath: uploadResult.filePath,
                availableSheets: metadata.sheets,
                metadata,
                statusColor: 'bg-green-500',
              }
            : f
        )
      )

      if (metadata.issues?.length) {
        const checks = metadata.issues.reduce<Record<string, boolean>>(
          (acc, issue) => {
            acc[issue.id] = true
            return acc
          },
          {}
        )

        setFilePreviewChecks((prev) => ({
          ...prev,
          [newId]: checks,
        }))
      }
    }
  } catch (error) {
    console.error('Erreur lors du chargement du fichier:', error)

    setFiles((prev) =>
      prev.map((f) =>
        f.id === selectedFiles?.[0]?.name
          ? { ...f, statusColor: 'bg-red-500' }
          : f
      )
    )

    alert(
      `Erreur lors du chargement : ${
        error instanceof Error ? error.message : 'Erreur inconnue'
      }`
    )
  } finally {
    input.value = ''
  }
}

  // Ajouter un nouveau fichier - Déclenche la fenêtre de sélection
  const handleAddFile = () => {
    document.getElementById('file-input')?.click()
  }

  const deleteFile = (fileId: string, event: React.MouseEvent) => {
    event.stopPropagation()
    if (files.length === 1) {
      alert('Impossible de supprimer le dernier fichier.')
      return
    }
    setFiles((prev) => prev.filter((f) => f.id !== fileId))
    setFileMappings((prev) => {
      const { [fileId]: _, ...rest } = prev
      return rest
    })
    setFilePreviewChecks((prev) => {
      const { [fileId]: _, ...rest } = prev
      return rest
    })
    if (selectedFileId === fileId) {
      const remainingFiles = files.filter((f) => f.id !== fileId)
      setSelectedFileId(remainingFiles[0]?.id || '')
    }
  }

  // Calcul des statistiques de progression
  const getProgressStats = useCallback(() => {
    let totalIssues = 0
    let selectedIssues = 0
    files.forEach((file) => {
      const checks = filePreviewChecks[file.id]
      if (checks) {
        const issuesCount = Object.keys(checks).length
        totalIssues += issuesCount
        selectedIssues += Object.values(checks).filter((v) => v === true).length
      }
    })
    return { totalIssues, selectedIssues }
  }, [files, filePreviewChecks])

  const { totalIssues, selectedIssues } = getProgressStats()
  const progressPercent = totalIssues === 0 ? 0 : (selectedIssues / totalIssues) * 100

  const handleCompile = () => {
    const selectedFile = files.find((f) => f.id === selectedFileId)
    const mapping = fileMappings[selectedFileId] || defaultMapping
    const previews = filePreviewChecks[selectedFileId]
    const selectedItems = previews ? Object.entries(previews).filter(([, v]) => v).map(([k]) => k) : []

    let configDetails = ''
    if (mapping.operationType === 'superxlookup' && mapping.superxlookupConfig) {
      const cfg = mapping.superxlookupConfig
      configDetails = 
        `Type: SuperXlookup\n` +
        `Feuille source: ${cfg.source_sheet_name}\n` +
        `Feuille cible: ${cfg.target_sheet_name}\n` +
        `Colonne clé source: ${cfg.source_key_column}\n` +
        `Colonne clé cible: ${cfg.target_key_column}\n` +
        `Colonne valeur: ${cfg.target_value_column}\n` +
        `Position résultat: ${cfg.result_position_column}\n` +
        `Nom colonne résultat: ${cfg.result_column_name}`
    } else if (mapping.operationType === 'celldown' && mapping.celldownConfig) {
      const cfg = mapping.celldownConfig
      configDetails =
        `Type: CellDown\n` +
        `Feuille source: ${cfg.source_sheet_path}\n` +
        `Date: ${cfg.date_str}\n` +
        `Colonne clé source: ${cfg.colown_key_path_source}\n` +
        `Colonne clé cible: ${cfg.target_key_column}\n` +
        `Colonne valeur: ${cfg.target_value_column}\n` +
        `Position résultat: ${cfg.result_position_column}\n` +
        `Colonne de départ: ${cfg.start_column}`
    }

    alert(
      `Compilation lancée !\n\n` +
        `Fichier actif : ${selectedFile?.name}\n\n` +
        `Configuration :\n${configDetails}\n\n` +
        `Éléments sélectionnés : ${selectedItems.length}/${Object.keys(previews || {}).length}\n` +
        `Progression globale : ${selectedIssues}/${totalIssues} (${Math.round(progressPercent)}%)`
    )
  }

  const selectedFile = files.find((f) => f.id === selectedFileId)
  const currentMapping = fileMappings[selectedFileId] || defaultMapping
  const currentPreviewChecks = filePreviewChecks[selectedFileId] || {}
  
  // Générer les preview items à partir des métadonnées du fichier
  const previewItems = selectedFile?.metadata?.issues || (selectedFile ? generatePreviewItems(selectedFile.name) : [])

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 to-gray-100 flex flex-col font-sans">
      {/* Input file caché pour la sélection de fichiers */}
      <input
        id="file-input"
        type="file"
        accept=".xlsx,.xls,.csv"
        multiple
        onChange={handleFileSelect}
        className="hidden"
      />

      <Header onAddSourceFile={handleAddFile} />

      <main className="flex-1 flex flex-col md:flex-row gap-6 p-6 w-full">
        <FileList
          files={files}
          selectedFileId={selectedFileId}
          onSelectFile={selectFile}
          onDeleteFile={deleteFile}
        />

        <FileDetails
          selectedFile={selectedFile}
          allFiles={files}
          currentMapping={currentMapping}
          currentPreviewChecks={currentPreviewChecks}
          previewItems={previewItems}
          onUpdateMapping={updateMapping}
          onTogglePreviewItem={togglePreviewItem}
        />

        <PreviewArea />
      </main>

      <Footer progressStats={{ totalIssues, selectedIssues }} onCompile={handleCompile} />
    </div>
  )
}


export default App