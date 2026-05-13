import { useState } from 'react'
import { SelectField } from './SelectField.tsx'
import { TextField } from './TextField'
import type { FileMapping, CellDownConfig, SuperXlookupConfig, OperationType, ColumnInfo, FileItem } from '../types'

interface OperationConfigProps {
    mapping: FileMapping
    availableFiles: FileItem[]
    onUpdateMapping: (mapping: FileMapping) => void
}

export default function OperationConfig({
    mapping,
    availableFiles,
    onUpdateMapping
}: OperationConfigProps) {

    const [loadingFiles, setLoadingFiles] = useState<Record<string, boolean>>({})

    // Chargement des métadonnées d'un fichier si nécessaire
    const ensureFileMetadata = async (filePath: string) => {
        if (!filePath) return
        const file = availableFiles.find(f => f.filePath === filePath)
        if (!file?.metadata) {
            setLoadingFiles(prev => ({ ...prev, [filePath]: true }))
            try {
                await new Promise(resolve => setTimeout(resolve, 300))
                // Les métadonnées sont normalement déjà chargées lors de l'upload
            } catch (error) {
                console.error('Erreur lors du chargement des métadonnées:', error)
            } finally {
                setLoadingFiles(prev => ({ ...prev, [filePath]: false }))
            }
        }
    }

    const getSheetsForFile = (filePath: string): string[] => {
        const file = availableFiles.find(f => f.filePath === filePath)
        return file?.metadata?.sheets || []
    }

    const getColumnsForSheet = (filePath: string, sheetName: string): ColumnInfo[] => {
        const file = availableFiles.find(f => f.filePath === filePath)
        if (!file?.metadata) return []
        return file.metadata.columns[sheetName] || []
    }

    const getColumnOptions = (columns: ColumnInfo[]) => {
        if (columns.length === 0) {
            return Array.from({ length: 26 }, (_, i) => ({
                value: String.fromCharCode(65 + i),
                label: String.fromCharCode(65 + i)
            }))
        }
        return columns.map(col => ({
            value: col.letter,
            label: col.name || col.letter
        }))
    }

    const getSheetOptions = (filePath: string) => {
        return getSheetsForFile(filePath).map(sheet => ({ value: sheet, label: sheet }))
    }

    const getFileOptions = () => {
        return availableFiles.map(file => ({ value: file.filePath, label: file.name }))
    }

    const handleOperationTypeChange = (type: OperationType) => {
        const firstFile = availableFiles[0]
        const defaultSourcePath = firstFile?.filePath || ''
        const defaultSheet = firstFile?.metadata?.sheets[0] || 'Sheet1'

        if (type === 'celldown') {
            onUpdateMapping({
                operationType: 'celldown',
                celldownConfig: mapping.celldownConfig || {
                    source_file_path: defaultSourcePath,
                    target_file_path: '',
                    colown_key_path_source: '',
                    source_key_column: '',
                    target_key_column: '',
                    target_value_column: '',
                    result_position_column: 'last_free',
                    result_column_name: 'Résultat',
                    source_sheet_path: defaultSheet,
                    source_sheet_name: defaultSheet,
                    target_sheet_name: '',
                    date_str: '',
                    start_column: '',
                },
            })
        } else if (type === 'superxlookup') {
            onUpdateMapping({
                operationType: 'superxlookup',
                superxlookupConfig: mapping.superxlookupConfig || {
                    source_file_path: defaultSourcePath,
                    target_file_path: '',
                    source_sheet_name: defaultSheet,
                    target_sheet_name: 'Sheet1',
                    source_key_column: '',
                    target_key_column: '',
                    target_value_column: '',
                    result_position_column: 'last_free',
                    result_column_name: 'Commentaire',
                },
            })
        } else if (type === 'ticket') {
            onUpdateMapping({
                operationType: 'ticket',
                ticketConfig: mapping.ticketConfig || {
                    source_file_path: '',
                    target_file_path: '',
                    colown_key_path_source: '',
                    target_key_column: '',
                    target_value_column: '',
                    result_position_column: '',
                    source_sheet_name: '',
                    start_column: '',
                    reference_name: '',
                    target_join_columns: [],
                    join_separator: '',
                    ignore_empty: false,
                    target_sheet_name: '',
                },
            })
        }
    }

    const updateCellDownField = <K extends keyof CellDownConfig>(field: K, value: CellDownConfig[K]) => {
        if (mapping.celldownConfig) {
            onUpdateMapping({
                ...mapping,
                celldownConfig: { ...mapping.celldownConfig, [field]: value },
            })
        }
    }

    const updateSuperXlookupField = <K extends keyof SuperXlookupConfig>(field: K, value: SuperXlookupConfig[K]) => {
        if (mapping.superxlookupConfig) {
            onUpdateMapping({
                ...mapping,
                superxlookupConfig: { ...mapping.superxlookupConfig, [field]: value },
            })
        }
    }

    return (
        <div className="space-y-6">
            {/* Type d'opération */}
            <div>
                <label className="block text-sm font-semibold text-gray-600 mb-2">Type d'opération</label>
                <div className="flex gap-2">
                    <button
                        onClick={() => handleOperationTypeChange('superxlookup')}
                        className={`flex-1 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${mapping.operationType === 'superxlookup'
                            ? 'bg-blue-600 text-white shadow-md'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                    >
                        SuperXlookup
                    </button>
                    <button
                        onClick={() => handleOperationTypeChange('celldown')}
                        className={`flex-1 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${mapping.operationType === 'celldown'
                            ? 'bg-blue-600 text-white shadow-md'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                    >
                        CellDown
                    </button>
                    <button
                        onClick={() => handleOperationTypeChange('ticket')}
                        className={`flex-1 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${mapping.operationType === 'ticket'
                            ? 'bg-blue-600 text-white shadow-md'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                    >
                        Ticket
                    </button>
                </div>
            </div>

            {/* ==================== SUPERXLOOKUP ==================== */}
            {mapping.operationType === 'superxlookup' && mapping.superxlookupConfig && (
                <div className="space-y-4 border-t border-gray-100 pt-4">
                    <h3 className="text-sm font-semibold text-gray-700">Configuration SuperXlookup</h3>

                    {/* Fichier source */}
                    <SelectField
                        label="📄 Fichier source"
                        value={mapping.superxlookupConfig.source_file_path}
                        onChange={async (newPath) => {
                            await ensureFileMetadata(newPath)
                            const firstSheet = getSheetsForFile(newPath)[0] || ''
                            updateSuperXlookupField('source_file_path', newPath)
                            updateSuperXlookupField('source_sheet_name', firstSheet)
                            updateSuperXlookupField('source_key_column', '')
                            updateSuperXlookupField('result_position_column', 'last_free')
                        }}
                        options={getFileOptions()}
                        placeholder="-- Sélectionner --"
                        loading={loadingFiles[mapping.superxlookupConfig.source_file_path || '']}
                    />

                    {/* Feuille source */}
                    <SelectField
                        label="📊 Feuille source"
                        value={mapping.superxlookupConfig.source_sheet_name}
                        onChange={(sheet) => {
                            updateSuperXlookupField('source_sheet_name', sheet)
                            updateSuperXlookupField('source_key_column', '')
                            updateSuperXlookupField('result_position_column', 'last_free')
                        }}
                        options={getSheetOptions(mapping.superxlookupConfig.source_file_path)}
                        placeholder="-- Choisir une feuille --"
                        disabled={!mapping.superxlookupConfig.source_file_path}
                        loading={loadingFiles[mapping.superxlookupConfig.source_file_path || '']}
                    />

                    {/* Fichier cible */}
                    <SelectField
                        label="📄 Fichier cible"
                        value={mapping.superxlookupConfig.target_file_path}
                        onChange={async (newPath) => {
                            await ensureFileMetadata(newPath)
                            const firstSheet = getSheetsForFile(newPath)[0] || ''
                            updateSuperXlookupField('target_file_path', newPath)
                            updateSuperXlookupField('target_sheet_name', firstSheet)
                            updateSuperXlookupField('target_key_column', '')
                            updateSuperXlookupField('target_value_column', '')
                        }}
                        options={getFileOptions()}
                        placeholder="-- Sélectionner --"
                        loading={loadingFiles[mapping.superxlookupConfig.target_file_path || '']}
                    />

                    {/* Feuille cible */}
                    <SelectField
                        label="📊 Feuille cible"
                        value={mapping.superxlookupConfig.target_sheet_name}
                        onChange={(sheet) => {
                            updateSuperXlookupField('target_sheet_name', sheet)
                            updateSuperXlookupField('target_key_column', '')
                            updateSuperXlookupField('target_value_column', '')
                        }}
                        options={getSheetOptions(mapping.superxlookupConfig.target_file_path)}
                        placeholder="-- Choisir une feuille --"
                        disabled={!mapping.superxlookupConfig.target_file_path}
                        loading={loadingFiles[mapping.superxlookupConfig.target_file_path || '']}
                    />

                    {/* Colonne clé source */}
                    <SelectField
                        label="🔑 Colonne clé source"
                        value={mapping.superxlookupConfig.source_key_column}
                        onChange={(col) => updateSuperXlookupField('source_key_column', col)}
                        options={getColumnOptions(getColumnsForSheet(
                            mapping.superxlookupConfig.source_file_path,
                            mapping.superxlookupConfig.source_sheet_name
                        ))}
                        placeholder="-- Choisir --"
                        disabled={!mapping.superxlookupConfig.source_file_path || !mapping.superxlookupConfig.source_sheet_name}
                    />

                    {/* Colonne clé cible */}
                    <SelectField
                        label="🔑 Colonne clé cible"
                        value={mapping.superxlookupConfig.target_key_column}
                        onChange={(col) => updateSuperXlookupField('target_key_column', col)}
                        options={getColumnOptions(getColumnsForSheet(
                            mapping.superxlookupConfig.target_file_path,
                            mapping.superxlookupConfig.target_sheet_name
                        ))}
                        placeholder="-- Choisir --"
                        disabled={!mapping.superxlookupConfig.target_file_path || !mapping.superxlookupConfig.target_sheet_name}
                    />

                    {/* Colonne valeur cible */}
                    <SelectField
                        label="📋 Colonne valeur (cible)"
                        value={mapping.superxlookupConfig.target_value_column}
                        onChange={(col) => updateSuperXlookupField('target_value_column', col)}
                        options={getColumnOptions(getColumnsForSheet(
                            mapping.superxlookupConfig.target_file_path,
                            mapping.superxlookupConfig.target_sheet_name
                        ))}
                        placeholder="-- Choisir --"
                        disabled={!mapping.superxlookupConfig.target_file_path || !mapping.superxlookupConfig.target_sheet_name}
                    />

                    {/* Position résultat */}
                    <SelectField
                        label="📍 Position résultat (source)"
                        value={mapping.superxlookupConfig.result_position_column}
                        onChange={(pos) => updateSuperXlookupField('result_position_column', pos)}
                        options={[
                            { value: 'last_free', label: '✨ Dernière colonne libre' },
                            ...getColumnOptions(getColumnsForSheet(
                                mapping.superxlookupConfig.source_file_path,
                                mapping.superxlookupConfig.source_sheet_name
                            ))
                        ]}
                        placeholder="-- Choisir --"
                        disabled={!mapping.superxlookupConfig.source_file_path || !mapping.superxlookupConfig.source_sheet_name}
                    />

                    {/* Nom de la nouvelle colonne */}
                    <TextField
                        label="🏷️ Nom de la nouvelle colonne"
                        value={mapping.superxlookupConfig.result_column_name}
                        onChange={(name) => updateSuperXlookupField('result_column_name', name)}
                        placeholder="Ex: Commentaire"
                    />
                </div>
            )}

            {/* ==================== CELLDOWN ==================== */}
            {mapping.operationType === 'celldown' && mapping.celldownConfig && (
                <div className="space-y-4 border-t border-gray-100 pt-4">
                    <h3 className="text-sm font-semibold text-gray-700">Configuration CellDown</h3>

                    {/* Fichier source */}
                    <SelectField
                        label="📄 Fichier source"
                        value={mapping.celldownConfig.source_file_path}
                        onChange={async (newPath) => {
                            await ensureFileMetadata(newPath)
                            const firstSheet = getSheetsForFile(newPath)[0] || 'Sheet1'
                            updateCellDownField('source_file_path', newPath)
                            updateCellDownField('source_sheet_name', firstSheet)
                            updateCellDownField('source_key_column', '')
                            updateCellDownField('start_column', '')
                            updateCellDownField('result_position_column', 'last_free')
                        }}
                        options={getFileOptions()}
                        placeholder="-- Sélectionner --"
                        loading={loadingFiles[mapping.celldownConfig.source_file_path || '']}
                    />

                    {/* Feuille source (conditionnelle) */}
                    {mapping.celldownConfig.source_file_path && (
                        <SelectField
                            label="📊 Feuille source"
                            value={mapping.celldownConfig.source_sheet_name}
                            onChange={(sheet) => {
                                updateCellDownField('source_sheet_name', sheet)
                                updateCellDownField('source_key_column', '')
                                updateCellDownField('start_column', '')
                                updateCellDownField('result_position_column', 'last_free')
                            }}
                            options={getSheetOptions(mapping.celldownConfig.source_file_path)}
                            placeholder="-- Choisir une feuille --"
                            loading={loadingFiles[mapping.celldownConfig.source_file_path || '']}
                        />
                    )}

                    {/* Fichier cible */}
                    <div className="border-t pt-4">
                        <SelectField
                            label="📄 Fichier cible"
                            value={mapping.celldownConfig.target_file_path}
                            onChange={async (newPath) => {
                                await ensureFileMetadata(newPath)
                                const firstSheet = getSheetsForFile(newPath)[0] || 'Sheet1'
                                updateCellDownField('target_file_path', newPath)
                                updateCellDownField('target_sheet_name', firstSheet)
                                updateCellDownField('target_key_column', '')
                                updateCellDownField('target_value_column', '')
                            }}
                            options={getFileOptions()}
                            placeholder="-- Sélectionner --"
                            loading={loadingFiles[mapping.celldownConfig.target_file_path || '']}
                        />
                    </div>

                    {/* Feuille cible (conditionnelle) */}
                    {mapping.celldownConfig.target_file_path && (
                        <SelectField
                            label="📊 Feuille cible"
                            value={mapping.celldownConfig.target_sheet_name}
                            onChange={(sheet) => {
                                updateCellDownField('target_sheet_name', sheet)
                                updateCellDownField('target_key_column', '')
                                updateCellDownField('target_value_column', '')
                            }}
                            options={getSheetOptions(mapping.celldownConfig.target_file_path)}
                            placeholder="-- Choisir une feuille --"
                            loading={loadingFiles[mapping.celldownConfig.target_file_path || '']}
                        />
                    )}

                    {/* Date */}
                    <TextField
                        label="📅 Date (DDMMYYYY)"
                        value={mapping.celldownConfig.date_str}
                        onChange={(date) => updateCellDownField('date_str', date)}
                        placeholder="Ex: 29042026"
                    />

                    {/* Colonnes (affichées seulement si fichiers+feuilles sont sélectionnés) */}
                    {mapping.celldownConfig.source_file_path &&
                        mapping.celldownConfig.target_file_path &&
                        mapping.celldownConfig.source_sheet_name &&
                        mapping.celldownConfig.target_sheet_name && (
                            <>
                                <div className="grid grid-cols-2 gap-3">
                                    <SelectField
                                        label="🔑 Colonne clé source"
                                        value={mapping.celldownConfig.source_key_column}
                                        onChange={(col) => updateCellDownField('source_key_column', col)}
                                        options={getColumnOptions(getColumnsForSheet(
                                            mapping.celldownConfig.source_file_path,
                                            mapping.celldownConfig.source_sheet_name
                                        ))}
                                        placeholder="-- Choisir --"
                                    />
                                    <SelectField
                                        label="🔑 Colonne clé cible"
                                        value={mapping.celldownConfig.target_key_column}
                                        onChange={(col) => updateCellDownField('target_key_column', col)}
                                        options={getColumnOptions(getColumnsForSheet(
                                            mapping.celldownConfig.target_file_path,
                                            mapping.celldownConfig.target_sheet_name
                                        ))}
                                        placeholder="-- Choisir --"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <SelectField
                                        label="📋 Colonne valeur (cible)"
                                        value={mapping.celldownConfig.target_value_column}
                                        onChange={(col) => updateCellDownField('target_value_column', col)}
                                        options={getColumnOptions(getColumnsForSheet(
                                            mapping.celldownConfig.target_file_path,
                                            mapping.celldownConfig.target_sheet_name
                                        ))}
                                        placeholder="-- Choisir --"
                                    />
                                    <SelectField
                                        label="▶️ Colonne de départ (source)"
                                        value={mapping.celldownConfig.start_column}
                                        onChange={(col) => updateCellDownField('start_column', col)}
                                        options={getColumnOptions(getColumnsForSheet(
                                            mapping.celldownConfig.source_file_path,
                                            mapping.celldownConfig.source_sheet_name
                                        ))}
                                        placeholder="-- Choisir --"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <SelectField
                                        label="📍 Position résultat (source)"
                                        value={mapping.celldownConfig.result_position_column}
                                        onChange={(pos) => updateCellDownField('result_position_column', pos)}
                                        options={[
                                            { value: 'last_free', label: '✨ Dernière colonne libre' },
                                            ...getColumnOptions(getColumnsForSheet(
                                                mapping.celldownConfig.source_file_path,
                                                mapping.celldownConfig.source_sheet_name
                                            ))
                                        ]}
                                        placeholder="-- Choisir --"
                                    />
                                    <TextField
                                        label="🏷️ Nom de la nouvelle colonne"
                                        value={mapping.celldownConfig.result_column_name}
                                        onChange={(name) => updateCellDownField('result_column_name', name)}
                                        placeholder="Ex: Date calculée"
                                    />
                                </div>
                            </>
                        )}
                </div>
            )}
        </div>
    )
}