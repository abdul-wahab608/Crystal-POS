<template>
  <div class="step-upload">
    <!-- Entity Selection (if not pre-selected) -->
    <div v-if="!entityType" class="form-group">
      <label class="form-label">What do you want to import?</label>
      <select v-model="selectedEntity" class="form-select">
        <option value="">Select entity type...</option>
        <option v-for="entity in importableEntities" :key="entity.value" :value="entity.value">
          {{ entity.label }}
        </option>
      </select>
    </div>

    <!-- File Upload Area -->
    <div 
      :class="['upload-zone', { dragover: isDragOver, 'has-file': store.fileName }]"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
    >
      <input 
        ref="fileInput"
        type="file" 
        accept=".csv,.xlsx,.xls"
        @change="handleFileSelect"
        class="hidden"
      />

      <div v-if="!store.fileName" class="upload-placeholder" @click="openFileDialog">
        <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="upload-text">
          <span class="text-blue-600 font-semibold">Click to upload</span> or drag and drop
        </p>
        <p class="upload-hint">CSV or Excel files (.xlsx, .xls)</p>
      </div>

      <div v-else class="file-info">
        <svg class="file-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <div class="file-details">
          <p class="file-name">{{ store.fileName }}</p>
          <p class="file-rows">{{ store.totalRows }} rows detected</p>
        </div>
        <button @click="clearFile" class="clear-btn">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Download Template -->
    <div class="template-section">
      <p class="template-hint">
        Need a template? 
        <button @click="downloadTemplate" class="template-link" :disabled="!effectiveEntityType">
          Download {{ effectiveEntityType ? IMPORT_CONFIGS[effectiveEntityType]?.displayName : '' }} template
        </button>
      </p>
    </div>

    <!-- Loading -->
    <div v-if="store.parsing" class="loading-state">
      <div class="spinner"></div>
      <p>Parsing file...</p>
    </div>

    <!-- Error -->
    <div v-if="store.error" class="error-message">
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      {{ store.error }}
    </div>

    <!-- Footer -->
    <div class="step-footer">
      <div></div>
      <button 
        @click="proceedToMapping" 
        :disabled="!canProceed"
        class="btn-primary"
      >
        Next: Map Columns
        <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useImportStore } from '../../stores/import'
import { useToastStore } from '../../stores/toast'
import { getImportableEntities, IMPORT_CONFIGS } from '../../constants/importFields'

const props = defineProps<{
  entityType?: string
}>()

const emit = defineEmits<{
  next: []
}>()

const store = useImportStore()
const toast = useToastStore()

const fileInput = ref<HTMLInputElement>()
const isDragOver = ref(false)
const selectedEntity = ref(props.entityType || '')

const importableEntities = getImportableEntities()

const effectiveEntityType = computed(() => props.entityType || selectedEntity.value)

const canProceed = computed(() => {
  return effectiveEntityType.value && store.fileName && store.fileColumns.length > 0 && !store.parsing
})

function openFileDialog() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    processFile(input.files[0])
  }
}

function handleDrop(event: DragEvent) {
  isDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    processFile(event.dataTransfer.files[0])
  }
}

async function processFile(file: File) {
  const validExtensions = ['.csv', '.xlsx', '.xls']
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!validExtensions.includes(ext)) {
    toast.error('Invalid File', 'Please upload a CSV or Excel file.')
    return
  }

  if (!effectiveEntityType.value) {
    toast.error('Select Entity', 'Please select what you want to import first.')
    return
  }

  await store.parseFile(file, effectiveEntityType.value)
}

function clearFile() {
  store.resetWizard()
  if (props.entityType) {
    store.setEntityType(props.entityType)
  }
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function downloadTemplate() {
  if (!effectiveEntityType.value) return
  
  try {
    await store.downloadTemplate(effectiveEntityType.value)
    toast.success('Template Downloaded', 'Check your downloads folder.')
  } catch (e: any) {
    toast.error('Download Failed', e.message)
  }
}

function proceedToMapping() {
  if (canProceed.value) {
    emit('next')
  }
}
</script>

<style scoped>
.step-upload {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.form-select {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  transition: all 0.2s;
}

.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.upload-zone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.2s;
  cursor: pointer;
  background: #fafafa;
}

.upload-zone:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.upload-zone.dragover {
  border-color: #3b82f6;
  background: #dbeafe;
}

.upload-zone.has-file {
  border-style: solid;
  border-color: #22c55e;
  background: #f0fdf4;
  cursor: default;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.upload-icon {
  width: 48px;
  height: 48px;
  color: #9ca3af;
}

.upload-text {
  font-size: 0.875rem;
  color: #6b7280;
}

.upload-hint {
  font-size: 0.75rem;
  color: #9ca3af;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
}

.file-icon {
  width: 40px;
  height: 40px;
  color: #22c55e;
  flex-shrink: 0;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.file-rows {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.clear-btn {
  padding: 0.5rem;
  border-radius: 8px;
  color: #6b7280;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #fee2e2;
  color: #dc2626;
}

.template-section {
  text-align: center;
}

.template-hint {
  font-size: 0.875rem;
  color: #6b7280;
}

.template-link {
  color: #3b82f6;
  font-weight: 500;
  text-decoration: underline;
}

.template-link:hover:not(:disabled) {
  color: #2563eb;
}

.template-link:disabled {
  color: #9ca3af;
  cursor: not-allowed;
  text-decoration: none;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.875rem;
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

.hidden {
  display: none;
}
</style>
