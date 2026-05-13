import type { PreviewItem, PreviewChecks } from '../types'

// Génère des éléments d'aperçu fictifs basés sur le nom du fichier
export const generatePreviewItems = (fileName: string): PreviewItem[] => {
  const lowerName = fileName.toLowerCase()
  if (lowerName.includes('rapport')) {
    return [
      { id: 'cell_down_1', label: 'Cell Down 29-03' },
      { id: 'cell_down_2', label: 'Signal faible' },
      { id: 'cell_down_3', label: 'Timeout dépassé' },
    ]
  } else if (lowerName.includes('logs')) {
    return [
      { id: 'error_conn', label: 'Erreur de connexion' },
      { id: 'timeout', label: 'Dépassement délai' },
      { id: 'reboot', label: 'Redémarrage intempestif' },
    ]
  } else if (lowerName.includes('brut')) {
    return [
      { id: 'corrupted', label: 'Données corrompues' },
      { id: 'invalid_format', label: 'Format invalide' },
      { id: 'missing_col', label: 'Colonne manquante' },
    ]
  } else {
    return [
      { id: 'issue_1', label: 'Anomalie réseau' },
      { id: 'issue_2', label: 'Panne matérielle' },
      { id: 'issue_3', label: 'Logiciel défaillant' },
    ]
  }
}

// Initialise les previewChecks pour un fichier (tous les éléments cochés par défaut)
export const initPreviewChecks = (fileName: string): PreviewChecks => {
  const items = generatePreviewItems(fileName)
  return items.reduce((acc, item) => ({ ...acc, [item.id]: true }), {})
}
