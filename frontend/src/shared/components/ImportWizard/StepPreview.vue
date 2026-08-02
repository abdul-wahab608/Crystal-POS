<template>
  <div class="step-preview">
    <!-- Summary Bar -->
    <div class="summary-bar">
      <div class="summary-item">
        <span class="summary-label">Total Rows</span>
        <span class="summary-value">{{ store.previewRows.length }}</span>
      </div>
      <div class="summary-item valid">
        <span class="summary-label">Valid</span>
        <span class="summary-value">{{ validCount }}</span>
      </div>
      <div class="summary-item error" v-if="errorCount > 0">
        <span class="summary-label">Errors</span>
        <span class="summary-value">{{ errorCount }}</span>
      </div>
      <div class="summary-item duplicate" v-if="duplicateCount > 0">
        <span class="summary-label">Duplicates</span>
        <span class="summary-value">{{ duplicateCount }}</span>
      </div>
      <div class="summary-item selected">
        <span class="summary-label">Selected</span>
        <span class="summary-value">{{ selectedCount }}</span>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button 
        :class="['tab', { active: activeFilter === 'all' }]"
        @click="activeFilter = 'all'"
      >
        All ({{ store.previewRows.length }})
      </button>
      <button 
        :class="['tab', { active: activeFilter === 'valid' }]"
        @click="activeFilter = 'valid'"
      >
        Valid ({{ validCount }})
      </button>
      <button 
        v-if="errorCount > 0"
        :class="['tab error', { active: activeFilter === 'errors' }]"
        @click="activeFilter = 'errors'"
      >
        Errors ({{ errorCount }})
      </button>
      <button 
        v-if="duplicateCount > 0"
        :class="['tab warning', { active: activeFilter === 'duplicates' }]"
        @click="activeFilter = 'duplicates'"
      >
        Duplicates ({{ duplicateCount }})
      </button>
    </div>

    <!-- Data Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-checkbox">
              <input 
                type="checkbox" 
                :checked="allFilteredSelected"
                :indeterminate="someFilteredSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th class="col-row">#</th>
            <th class="col-status">Status</th>
            <th v-for="mapping in store.columnMappings.filter(m => m.targetField)" :key="mapping.fileColumn">
              {{ getFieldLabel(mapping.targetField!) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="row in filteredRows" 
            :key="row._rowIndex"
            :class="getRowClass(row)"
          >
            <td class="col-checkbox">
              <input 
                type="checkbox"
                :checked="row._selected"
                :disabled="row._errors.length > 0 || row._isDuplicate"
                @change="store.toggleRowSelection(row._rowIndex)"
              />
            </td>
            <td class="col-row">{{ row._rowIndex }}</td>
            <td class="col-status">
              <span v-if="row._isDuplicate" class="status-badge duplicate">
                Duplicate
              </span>
              <span v-else-if="row._errors.length > 0" class="status-badge error">
                Error
              </span>
              <span v-else class="status-badge valid">
                Valid
              </span>
            </td>
            <td v-for="mapping in store.columnMappings.filter(m => m.targetField)" :key="mapping.fileColumn">
              <span>{{ formatCellValue(row[mapping.fileColumn]) }}</span>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="filteredRows.length === 0" class="empty-state">
        <p>No rows match the current filter.</p>
      </div>
    </div>

    <!-- Errors List -->
    <div v-if="rowsWithErrors.length > 0" class="errors-summary">
      <h4>Validation Errors</h4>
      <ul>
        <li v-for="row in rowsWithErrors.slice(0, 5)" :key="row._rowIndex">
          <strong>Row {{ row._rowIndex }}:</strong> {{ row._errors.join(', ') }}
        </li>
        <li v-if="rowsWithErrors.length > 5" class="more-errors">
          ... and {{ rowsWithErrors.length - 5 }} more rows with errors
        </li>
      </ul>
    </div>

    <!-- Footer -->
    <div class="step-footer">
      <button @click="$emit('back')" class="btn-secondary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </button>
      <div class="footer-right">
        <span class="import-count">
          {{ selectedCount }} row{{ selectedCount !== 1 ? 's' : '' }} will be imported
        </span>
        <button 
          @click="startImport" 
          :disabled="selectedCount === 0 || store.importing"
          class="btn-primary"
        >
          <svg v-if="store.importing" class="w-4 h-4 mr-2 spinner-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ store.importing ? `Importing (${store.currentBatch}/${store.totalBatches})...` : 'Import Selected' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useImportStore, type ImportPreviewRow } from '../../stores/import'

const emit = defineEmits<{
  next: []
  back: []
}>()

const store = useImportStore()
const activeFilter = ref<'all' | 'valid' | 'errors' | 'duplicates'>('all')

const validCount = computed(() => {
  return store.previewRows.filter(r => r._errors.length === 0 && !r._isDuplicate).length
})

const errorCount = computed(() => {
  return store.previewRows.filter(r => r._errors.length > 0).length
})

const duplicateCount = computed(() => {
  return store.previewRows.filter(r => r._isDuplicate).length
})

const selectedCount = computed(() => {
  return store.previewRows.filter(r => r._selected).length
})

const rowsWithErrors = computed(() => {
  return store.previewRows.filter(r => r._errors.length > 0)
})

const filteredRows = computed(() => {
  switch (activeFilter.value) {
    case 'valid':
      return store.previewRows.filter(r => r._errors.length === 0 && !r._isDuplicate)
    case 'errors':
      return store.previewRows.filter(r => r._errors.length > 0)
    case 'duplicates':
      return store.previewRows.filter(r => r._isDuplicate)
    default:
      return store.previewRows
  }
})

const allFilteredSelected = computed(() => {
  const validRows = filteredRows.value.filter(r => r._errors.length === 0 && !r._isDuplicate)
  if (validRows.length === 0) return false
  return validRows.every(r => r._selected)
})

const someFilteredSelected = computed(() => {
  const validRows = filteredRows.value.filter(r => r._errors.length === 0 && !r._isDuplicate)
  if (validRows.length === 0) return false
  const selected = validRows.filter(r => r._selected)
  return selected.length > 0 && selected.length < validRows.length
})

function getFieldLabel(fieldKey: string): string {
  const config = store.entityConfig
  if (!config) return fieldKey
  const field = config.fields.find(f => f.key === fieldKey)
  return field?.label || fieldKey
}

function getRowClass(row: ImportPreviewRow) {
  return {
    'row-error': row._errors.length > 0,
    'row-duplicate': row._isDuplicate,
    'row-selected': row._selected
  }
}

function formatCellValue(value: any): string {
  if (value === undefined || value === null) return '-'
  return String(value)
}

function toggleSelectAll() {
  const validRows = filteredRows.value.filter(r => r._errors.length === 0 && !r._isDuplicate)
  const shouldSelect = !allFilteredSelected.value
  
  for (const row of validRows) {
    row._selected = shouldSelect
  }
}

async function startImport() {
  await store.runImport()
  if (store.importResult && !store.error) {
    emit('next')
  }
}

onMounted(() => {
  // Auto-select all valid rows on mount
  store.selectAllRows(true)
})
</script>

<style scoped>
.step-preview {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
}

.summary-bar {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  min-width: 80px;
}

.summary-item.valid {
  border-color: #22c55e;
  background: #f0fdf4;
}

.summary-item.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.summary-item.duplicate {
  border-color: #f59e0b;
  background: #fffbeb;
}

.summary-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.summary-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.filter-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.tab {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  border-radius: 6px 6px 0 0;
  transition: all 0.2s;
}

.tab:hover {
  background: #f3f4f6;
  color: #374151;
}

.tab.active {
  background: #3b82f6;
  color: white;
}

.tab.error.active {
  background: #ef4444;
}

.tab.warning.active {
  background: #f59e0b;
}

.table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th {
  position: sticky;
  top: 0;
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: top;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.col-checkbox {
  width: 40px;
  text-align: center;
}

.col-row {
  width: 50px;
  color: #9ca3af;
}

.col-status {
  width: 100px;
}

.row-error {
  background: #fef2f2;
}

.row-duplicate {
  background: #fffbeb;
}

.row-selected {
  background: #eff6ff !important;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
}

.status-badge.valid {
  background: #dcfce7;
  color: #166534;
}

.status-badge.error {
  background: #fecaca;
  color: #991b1b;
}

.status-badge.duplicate {
  background: #fef3c7;
  color: #92400e;
}

.error-cell {
  color: #dc2626;
}

.error-text {
  font-size: 0.75rem;
  color: #dc2626;
  margin: 0.25rem 0 0;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #6b7280;
}

.errors-summary {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 1rem;
}

.errors-summary h4 {
  margin: 0 0 0.5rem;
  color: #991b1b;
  font-size: 0.875rem;
}

.errors-summary ul {
  margin: 0;
  padding-left: 1.5rem;
  font-size: 0.875rem;
  color: #dc2626;
}

.errors-summary .more-errors {
  font-style: italic;
  color: #9ca3af;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  z-index: 10;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.step-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  margin-top: auto;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.import-count {
  font-size: 0.875rem;
  color: #6b7280;
}

.btn-primary {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.25rem;
  background: #3b82f6;
  color: white;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.25rem;
  background: white;
  color: #374151;
  font-weight: 500;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f9fafb;
}
</style>
