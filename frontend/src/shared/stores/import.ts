/**
 * Import store for managing the import wizard state and API calls
 */
import { defineStore } from 'pinia'
import api from '../api/axios'
import { IMPORT_CONFIGS, type EntityImportConfig, type ImportFieldConfig } from '../constants/importFields'

export interface ImportPreviewRow {
  _rowIndex: number
  _selected: boolean
  _errors: string[]
  _isDuplicate: boolean
  [key: string]: any
}

export interface ColumnMapping {
  fileColumn: string
  targetField: string | null
}

export interface ImportResult {
  session_id: string
  total_rows: number
  success_count: number
  error_count: number
  duplicate_count: number
  new_units: string[]
  errors: Array<{
    row: number
    type: string
    message: string
    data: any
  }>
  status: 'success' | 'partial' | 'failed'
}

export interface ImportSession {
  id: string
  entity_type: string
  entity_type_display: string
  user: number
  user_name: string
  file_name: string
  total_rows: number
  success_count: number
  error_count: number
  duplicate_count: number
  status: string
  status_display: string
  created_at: string
  undone_at: string | null
  undo_expires_at: string
  can_undo: boolean
  undo_time_remaining: string | null
  imported_ids?: number[]
  errors?: Array<{
    row: number
    type: string
    message: string
    data: any
  }>
}

export const useImportStore = defineStore('import', {
  state: () => ({
    // Wizard state
    currentStep: 1,
    entityType: '' as string,
    
    // File data
    fileName: '',
    fileColumns: [] as string[],
    previewRows: [] as ImportPreviewRow[],
    totalRows: 0,
    
    // Mapping
    columnMappings: [] as ColumnMapping[],
    suggestedMappings: {} as Record<string, string>,
    
    // Import result
    importResult: null as ImportResult | null,
    lastSessionId: null as string | null,
    
    // Loading states
    parsing: false,
    importing: false,
    currentBatch: 0,
    totalBatches: 0,
    
    // Error
    error: null as string | null,
    
    // Import history
    importSessions: [] as ImportSession[],
    historyLoading: false,
    historyError: null as string | null,
  }),

  getters: {
    entityConfig: (state): EntityImportConfig | null => {
      return IMPORT_CONFIGS[state.entityType] || null
    },

    requiredFields: (state): ImportFieldConfig[] => {
      const config = IMPORT_CONFIGS[state.entityType]
      if (!config) return []
      return config.fields.filter(f => f.required)
    },

    mappedFields: (state): string[] => {
      return state.columnMappings
        .filter(m => m.targetField)
        .map(m => m.targetField!)
    },

    unmappedRequiredFields(): ImportFieldConfig[] {
      return this.requiredFields.filter(f => !this.mappedFields.includes(f.key))
    },

    canProceedToPreview(): boolean {
      return this.unmappedRequiredFields.length === 0
    },

    selectedRows: (state): ImportPreviewRow[] => {
      return state.previewRows.filter(r => r._selected)
    },

    validSelectedRows(): ImportPreviewRow[] {
      return this.selectedRows.filter(r => r._errors.length === 0 && !r._isDuplicate)
    },
  },

  actions: {
    // Reset wizard state
    resetWizard() {
      this.currentStep = 1
      this.entityType = ''
      this.fileName = ''
      this.fileColumns = []
      this.previewRows = []
      this.totalRows = 0
      this.columnMappings = []
      this.suggestedMappings = {}
      this.importResult = null
      this.lastSessionId = null
      this.parsing = false
      this.importing = false
      this.currentBatch = 0
      this.totalBatches = 0
      this.error = null
    },

    setEntityType(type: string) {
      this.entityType = type
    },

    // Parse file on backend and get preview
    async parseFile(file: File, entityType: string) {
      this.parsing = true
      this.error = null
      this.entityType = entityType
      this.fileName = file.name

      const config = IMPORT_CONFIGS[entityType]
      if (!config) {
        this.error = 'Unknown entity type'
        this.parsing = false
        return
      }

      try {
        const formData = new FormData()
        formData.append('file', file)

        const res = await api.post(`${config.apiEndpoint}/preview_import/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })

        const data = res.data
        this.fileColumns = data.columns
        this.totalRows = data.total_rows
        this.suggestedMappings = data.suggested_mappings || {}

        // Initialize preview rows
        this.previewRows = data.preview_rows.map((row: any, idx: number) => ({
          ...row,
          _rowIndex: idx + 2, // +2 for 1-based and header row
          _selected: true,
          _errors: [],
          _isDuplicate: false,
        }))

        // Initialize mappings with suggestions
        this.columnMappings = this.fileColumns.map(col => ({
          fileColumn: col,
          targetField: this.suggestedMappings[col] || null,
        }))

        this.currentStep = 2
      } catch (e: any) {
        this.error = e.response?.data?.error || e.message
      } finally {
        this.parsing = false
      }
    },

    // Update column mapping
    setColumnMapping(fileColumn: string, targetField: string | null) {
      const mapping = this.columnMappings.find(m => m.fileColumn === fileColumn)
      if (mapping) {
        mapping.targetField = targetField
      }
    },

    // Validate preview data
    validatePreviewData() {
      const config = IMPORT_CONFIGS[this.entityType]
      if (!config) return

      // Build reverse mapping (target field -> file column)
      const reverseMapping: Record<string, string> = {}
      for (const mapping of this.columnMappings) {
        if (mapping.targetField) {
          reverseMapping[mapping.targetField] = mapping.fileColumn
        }
      }

      // Validate each row
      for (const row of this.previewRows) {
        row._errors = []

        // Check required fields
        for (const field of config.fields) {
          if (field.required) {
            const fileCol = reverseMapping[field.key]
            const value = fileCol ? row[fileCol] : undefined

            if (value === undefined || value === null || value === '') {
              row._errors.push(`${field.label} is required`)
            }
          }
        }
      }
    },

    // Toggle row selection
    toggleRowSelection(rowIndex: number) {
      const row = this.previewRows.find(r => r._rowIndex === rowIndex)
      if (row) {
        row._selected = !row._selected
      }
    },

    // Select/deselect all rows
    selectAllRows(selected: boolean) {
      for (const row of this.previewRows) {
        row._selected = selected
      }
    },

    // Run the import
    async runImport() {
      const config = IMPORT_CONFIGS[this.entityType]
      if (!config) {
        this.error = 'Unknown entity type'
        return
      }

      this.importing = true
      this.error = null
      this.currentBatch = 0

      try {
        // Build mapping object
        const mappings: Record<string, string> = {}
        for (const mapping of this.columnMappings) {
          if (mapping.targetField) {
            mappings[mapping.fileColumn] = mapping.targetField
          }
        }

        // Transform selected rows to mapped data
        const dataToImport = this.selectedRows.map(row => {
          const mapped: Record<string, any> = {}
          for (const [fileCol, targetField] of Object.entries(mappings)) {
            mapped[targetField] = row[fileCol]
          }
          return mapped
        })

        // Import in batches of 100
        const batchSize = 100
        this.totalBatches = Math.ceil(dataToImport.length / batchSize)

        let finalResult: ImportResult | null = null

        for (let i = 0; i < dataToImport.length; i += batchSize) {
          this.currentBatch = Math.floor(i / batchSize) + 1
          const batch = dataToImport.slice(i, i + batchSize)

          const res = await api.post(`${config.apiEndpoint}/bulk_import/`, {
            data: batch,
            mappings: {}, // Already mapped
          })

          // Merge results
          if (!finalResult) {
            finalResult = res.data
          } else {
            finalResult.success_count += res.data.success_count
            finalResult.error_count += res.data.error_count
            finalResult.duplicate_count += res.data.duplicate_count
            finalResult.errors = [...finalResult.errors, ...res.data.errors]
            finalResult.new_units = [...new Set([...finalResult.new_units, ...res.data.new_units])]
          }
        }

        this.importResult = finalResult
        this.lastSessionId = finalResult?.session_id || null
        this.currentStep = 4
      } catch (e: any) {
        this.error = e.response?.data?.error || e.message
      } finally {
        this.importing = false
      }
    },

    // Fetch import history
    async fetchImportHistory(filters?: { entity_type?: string; status?: string }) {
      this.historyLoading = true
      this.historyError = null

      try {
        const params = new URLSearchParams()
        if (filters?.entity_type) params.append('entity_type', filters.entity_type)
        if (filters?.status) params.append('status', filters.status)

        const res = await api.get<ImportSession[]>(`/import-sessions/?${params.toString()}`)
        this.importSessions = res.data
      } catch (e: any) {
        this.historyError = e.response?.data?.detail || e.message
      } finally {
        this.historyLoading = false
      }
    },

    // Get single import session details
    async getImportSession(id: string): Promise<ImportSession | null> {
      try {
        const res = await api.get<ImportSession>(`/import-sessions/${id}/`)
        return res.data
      } catch (e: any) {
        this.error = e.response?.data?.detail || e.message
        return null
      }
    },

    // Undo an import
    async undoImport(sessionId: string) {
      try {
        const res = await api.post(`/import-sessions/${sessionId}/undo/`)
        
        // Refresh history
        await this.fetchImportHistory()
        
        return res.data
      } catch (e: any) {
        throw new Error(e.response?.data?.error || e.message)
      }
    },

    // Download template
    async downloadTemplate(entityType: string) {
      const config = IMPORT_CONFIGS[entityType]
      if (!config) {
        throw new Error('Unknown entity type')
      }

      try {
        const res = await api.get(`${config.apiEndpoint}/download_template/`, {
          responseType: 'blob',
        })

        // Download the file
        const blob = new Blob([res.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${entityType}_template.csv`
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (e: any) {
        throw new Error(e.response?.data?.error || e.message)
      }
    },
  },
})
