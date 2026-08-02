<template>
  <div class="raw-materials-page">
    <div class="page-header">
      <h1 class="page-title">Raw Materials</h1>
      <div class="header-actions">
        <ExportButton entityType="raw_materials" />
        <button v-if="authStore.canImport" class="btn-import" @click="showImportWizard = true">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
          </svg>
          Import
        </button>
        <button class="btn-primary" @click="handleAddClick">Add Material</button>
        <button class="btn-secondary" @click="showPurchaseForm">Add Purchase</button>
      </div>
    </div>

    <!-- Batch Actions Toolbar -->
    <BatchActionsToolbar 
      entityType="raw_materials"
      entityLabel="raw material"
      :showActivate="false"
      :showDeactivate="false"
      @action-complete="handleBatchActionComplete"
    />

    <!-- Material Summary Cards -->
    <div v-if="materialSummary.length > 0" class="summary-section">
      <h3>Material Stock Summary</h3>
      <div class="summary-grid">
        <div v-for="summary in materialSummary" :key="summary.key" class="summary-card">
          <div class="summary-name">{{ summary.name }} ({{ summary.unit }})</div>
          <div class="summary-quantity">{{ summary.totalQuantity.toFixed(2) }}</div>
          <div class="summary-entries">{{ summary.entries }} {{ summary.entries === 1 ? 'entry' : 'entries' }}</div>
        </div>
      </div>
    </div>

    <div v-if="store.lowStock.length > 0" class="low-stock-warning">
      <span>⚠️ The following materials need reordering:</span>
      <ul>
        <li v-for="mat in store.lowStock" :key="mat.id">
          {{ mat.name }} (Available: {{ mat.available_stock }}, Reorder Level: {{ mat.reorder_level }})
        </li>
      </ul>
    </div>

    <RawMaterialTable 
      :materials="store.materials" 
      @refresh="refresh"
      @edit="editMaterial"
      @delete="deleteMaterial"
      @usage="showUsageForm"
      @purchase="showPurchaseForm"
      @history="openHistoryModal"
    />

    <!-- Add/Edit Form Modal -->
    <div v-if="showAddForm || editingMaterial" class="modal-overlay" @click.self="closeModals">
      <RawMaterialForm 
        :material="editingMaterial"
        @success="onFormSuccess" 
        @cancel="closeModals" 
      />
    </div>

    <!-- Usage Form Modal -->
    <div v-if="showUsageModal" class="modal-overlay" @click.self="closeModals">
      <RawMaterialUsageForm 
        :material="selectedMaterial!"
        @success="onUsageSuccess" 
        @cancel="closeModals" 
      />
    </div>

    <!-- Purchase Form Modal -->
    <div v-if="showPurchaseModal" class="modal-overlay" @click.self="closeModals">
      <RawMaterialPurchaseForm 
        @success="onPurchaseSuccess" 
        @cancel="closeModals" 
      />
    </div>

    <!-- History Modal -->
    <RawMaterialHistoryModal 
      v-if="showHistoryModal"
      :material="selectedMaterial!"
      @close="closeModals"
    />

    <!-- Import Wizard -->
    <ImportWizard 
      v-if="showImportWizard"
      entityType="raw_materials"
      @close="handleImportClose"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRawMaterialsStore } from '../stores/raw_materials'
import { useAuthStore } from '../../../shared/stores/auth'
import { useBatchActionsStore } from '../../../shared/stores/batchActions'
import RawMaterialTable from '../components/RawMaterialTable.vue'
import RawMaterialForm from '../components/RawMaterialForm.vue'
import RawMaterialUsageForm from '../components/RawMaterialUsageForm.vue'
import RawMaterialPurchaseForm from '../components/RawMaterialPurchaseForm.vue'
import RawMaterialHistoryModal from '../components/RawMaterialHistoryModal.vue'
import ImportWizard from '../../../shared/components/ImportWizard/ImportWizard.vue'
import ExportButton from '../../../shared/components/ExportButton.vue'
import BatchActionsToolbar from '../../../shared/components/BatchActionsToolbar.vue'
import type { RawMaterial } from '../types'

const store = useRawMaterialsStore()
const authStore = useAuthStore()
const batchStore = useBatchActionsStore()

// Modal states
const showAddForm = ref(false)
const showImportWizard = ref(false)
const editingMaterial = ref<RawMaterial | undefined>(undefined)
const showUsageModal = ref(false)
const showPurchaseModal = ref(false)
const showHistoryModal = ref(false)
const selectedMaterial = ref<RawMaterial | null>(null)

// Computed summary of materials grouped by name+unit
const materialSummary = computed(() => {
  const summaryMap = new Map<string, { name: string; unit: string; totalQuantity: number; entries: number }>()
  
  store.materials.forEach(material => {
    const key = `${material.name}-${material.unit}`
    if (summaryMap.has(key)) {
      const existing = summaryMap.get(key)!
      existing.totalQuantity += Number(material.quantity)
      existing.entries += 1
    } else {
      summaryMap.set(key, {
        name: material.name,
        unit: material.unit,
        totalQuantity: Number(material.quantity),
        entries: 1
      })
    }
  })
  
  return Array.from(summaryMap.entries()).map(([key, value]) => ({
    key,
    ...value
  }))
})

function handleAddClick() {
  showAddForm.value = true
}

function refresh() {
  store.fetchMaterials()
  store.fetchLowStock()
}

function editMaterial(material: RawMaterial) {
  editingMaterial.value = material
}

function deleteMaterial(id: number) {
  if (confirm('Are you sure you want to delete this raw material?')) {
    store.deleteMaterial(id).then(() => {
      refresh()
    }).catch(error => {
      // Handle error silently or show user-friendly message
    })
  }
}

function showUsageForm(material: RawMaterial) {
  selectedMaterial.value = material
  showUsageModal.value = true
}

function showPurchaseForm() {
  showPurchaseModal.value = true
}

function openHistoryModal(material: RawMaterial) {
  selectedMaterial.value = material
  showHistoryModal.value = true
}

function closeModals() {
  showAddForm.value = false
  editingMaterial.value = undefined
  showUsageModal.value = false
  showPurchaseModal.value = false
  showHistoryModal.value = false
  selectedMaterial.value = null
}

function onFormSuccess() {
  closeModals()
  refresh()
}

function onUsageSuccess() {
  closeModals()
  refresh()
}

function onPurchaseSuccess() {
  closeModals()
  refresh()
}

function handleImportClose() {
  showImportWizard.value = false
  refresh()
}

function handleBatchActionComplete(action: string, result: any) {
  refresh()
  console.log(`Batch ${action} completed:`, result.message)
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.raw-materials-page {
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #111827;
}

.btn-primary {
  background: #2563eb;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: #6b7280;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  margin-left: 0.5rem;
}

.btn-import {
  background: #e5e7eb;
  color: #374151;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.btn-import:hover {
  background: #d1d5db;
}

.btn-secondary:hover {
  background: #5b6371;
}

.summary-section {
  margin-bottom: 2rem;
}

.summary-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.summary-name {
  font-size: 0.875rem;
  font-weight: 500;
  opacity: 0.9;
  margin-bottom: 0.5rem;
}

.summary-quantity {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.summary-entries {
  font-size: 0.75rem;
  opacity: 0.8;
}

.low-stock-warning {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.low-stock-warning ul {
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
}

.low-stock-warning li {
  margin-bottom: 0.25rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
</style> 