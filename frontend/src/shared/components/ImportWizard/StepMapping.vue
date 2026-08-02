<template>
  <div class="step-mapping">
    <!-- Header Info -->
    <div class="mapping-info">
      <div class="info-card">
        <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <div>
          <p class="info-label">File</p>
          <p class="info-value">{{ store.fileName }}</p>
        </div>
      </div>
      <div class="info-card">
        <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
        <div>
          <p class="info-label">Rows</p>
          <p class="info-value">{{ store.totalRows }}</p>
        </div>
      </div>
      <div class="info-card">
        <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="info-label">Mapped</p>
          <p class="info-value">{{ mappedCount }} / {{ store.fileColumns.length }}</p>
        </div>
      </div>
    </div>

    <!-- Mapping Table -->
    <div class="mapping-table-container">
      <table class="mapping-table">
        <thead>
          <tr>
            <th class="col-file">File Column</th>
            <th class="col-sample">Sample Value</th>
            <th class="col-arrow"></th>
            <th class="col-target">Maps To</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="mapping in store.columnMappings" :key="mapping.fileColumn" :class="{ mapped: mapping.targetField }">
            <td class="col-file">
              <span class="column-name">{{ mapping.fileColumn }}</span>
            </td>
            <td class="col-sample">
              <span class="sample-value">{{ getSampleValue(mapping.fileColumn) }}</span>
            </td>
            <td class="col-arrow">
              <svg 
                :class="['arrow-icon', { active: mapping.targetField }]" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </td>
            <td class="col-target">
              <select 
                :value="mapping.targetField || ''" 
                @change="updateMapping(mapping.fileColumn, ($event.target as HTMLSelectElement).value)"
                class="target-select"
              >
                <option value="">-- Skip this column --</option>
                <option 
                  v-for="field in availableFields" 
                  :key="field.key"
                  :value="field.key"
                  :disabled="isFieldUsed(field.key, mapping.fileColumn)"
                >
                  {{ field.label }} {{ field.required ? '*' : '' }}
                  {{ isFieldUsed(field.key, mapping.fileColumn) ? '(already mapped)' : '' }}
                </option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Legend -->
    <div class="mapping-legend">
      <span class="legend-item">
        <span class="legend-dot required"></span>
        * Required field
      </span>
      <span class="legend-item">
        <span class="legend-dot mapped"></span>
        Mapped columns
      </span>
    </div>

    <!-- Validation Messages -->
    <div v-if="store.unmappedRequiredFields.length > 0" class="validation-warning">
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      <div>
        <p class="warning-title">Required fields not mapped:</p>
        <p class="warning-list">{{ store.unmappedRequiredFields.map((f: any) => f.label).join(', ') }}</p>
      </div>
    </div>

    <!-- Footer -->
    <div class="step-footer">
      <button @click="$emit('back')" class="btn-secondary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </button>
      <button 
        @click="proceedToPreview" 
        :disabled="!store.canProceedToPreview"
        class="btn-primary"
      >
        Next: Preview Data
        <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useImportStore } from '../../stores/import'

const emit = defineEmits<{
  next: []
  back: []
}>()

const store = useImportStore()

const availableFields = computed(() => {
  return store.entityConfig?.fields || []
})

const mappedCount = computed(() => {
  return store.columnMappings.filter(m => m.targetField).length
})

function getSampleValue(column: string): string {
  if (store.previewRows.length === 0) return '-'
  const value = store.previewRows[0][column]
  if (value === undefined || value === null || value === '') return '-'
  const strValue = String(value)
  return strValue.length > 30 ? strValue.substring(0, 30) + '...' : strValue
}

function isFieldUsed(fieldKey: string, currentColumn: string): boolean {
  for (const mapping of store.columnMappings) {
    if (mapping.fileColumn !== currentColumn && mapping.targetField === fieldKey) {
      return true
    }
  }
  return false
}

function updateMapping(column: string, fieldKey: string) {
  store.setColumnMapping(column, fieldKey || null)
}

function proceedToPreview() {
  if (store.canProceedToPreview) {
    store.validatePreviewData()
    emit('next')
  }
}
</script>

<style scoped>
.step-mapping {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.mapping-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.info-icon {
  width: 24px;
  height: 24px;
  color: #6b7280;
}

.info-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0;
}

.info-value {
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.mapping-table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.mapping-table {
  width: 100%;
  border-collapse: collapse;
}

.mapping-table th {
  background: #f9fafb;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #6b7280;
  border-bottom: 1px solid #e5e7eb;
}

.mapping-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.mapping-table tr:last-child td {
  border-bottom: none;
}

.mapping-table tr.mapped {
  background: #f0fdf4;
}

.col-file {
  width: 25%;
}

.col-sample {
  width: 25%;
}

.col-arrow {
  width: 50px;
  text-align: center;
}

.col-target {
  width: 35%;
}

.column-name {
  font-weight: 500;
  color: #374151;
}

.sample-value {
  font-size: 0.875rem;
  color: #6b7280;
  font-family: monospace;
}

.arrow-icon {
  width: 20px;
  height: 20px;
  color: #d1d5db;
  transition: all 0.2s;
}

.arrow-icon.active {
  color: #22c55e;
}

.target-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
}

.target-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.mapping-legend {
  display: flex;
  gap: 1.5rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-dot.required {
  background: #ef4444;
}

.legend-dot.mapped {
  background: #22c55e;
}

.validation-warning {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  color: #b45309;
}

.validation-warning svg {
  flex-shrink: 0;
}

.warning-title {
  font-weight: 600;
  margin: 0;
}

.warning-list {
  font-size: 0.875rem;
  margin: 0.25rem 0 0;
}

.step-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  margin-top: auto;
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
