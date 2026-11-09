<template>
  <div class="raw-materials-page">
    <div class="page-header">
      <h1 class="page-title">Raw Materials</h1>
      <div class="header-actions">
        <ExportButton entityType="raw_materials" />
        <button v-if="authStore.canImport" class="btn-secondary" @click="showImportWizard = true">Import</button>
        <router-link class="btn-secondary" to="/purchases">Buy stock on Purchases</router-link>
        <button class="btn-secondary" :disabled="!store.materials.length" @click="openUsage(null)">Record usage</button>
        <button class="btn-primary" @click="openForm(null)">Add material</button>
      </div>
    </div>

    <div v-if="store.lowStock.length" class="low-stock-banner">
      Reorder soon:
      <span v-for="(material, index) in store.lowStock" :key="material.id">
        {{ index ? ', ' : '' }}{{ material.name }} ({{ Number(material.quantity).toFixed(2) }} {{ material.unit }} left)
      </span>
    </div>

    <p v-if="loadError" class="form-error">{{ loadError }}</p>
    <RawMaterialTable
      :materials="pageItems"
      @edit="openForm"
      @usage="openUsage"
      @history="openHistory"
      @delete="confirmDelete"
    />
    <PaginationBar
      :page="page"
      :totalPages="totalPages"
      :total="total"
      :pageSize="pageSize"
      @update:page="goTo"
      @update:pageSize="setPageSize"
    />

    <div v-if="formOpen" class="modal-overlay" @click.self="closeModals">
      <RawMaterialForm :material="editing" @success="closeModals" @cancel="closeModals" />
    </div>

    <div v-if="usageOpen" class="modal-overlay" @click.self="closeModals">
      <RawMaterialUsageForm
        :materials="store.materials"
        :initialMaterialId="usageMaterialId"
        @success="closeModals"
        @cancel="closeModals"
      />
    </div>

    <RawMaterialHistoryModal v-if="historyMaterial" :material="historyMaterial" @close="closeModals" />

    <ImportWizard v-if="showImportWizard" entityType="raw_materials" @close="handleImportClose" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRawMaterialsStore } from '../stores/raw_materials'
import { usePagination } from '../../../shared/composables/usePagination'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { useAuthStore } from '../../../shared/stores/auth'
import { useToastStore } from '../../../shared/stores/toast'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { errorMessageOf } from '../utils/errorMessage'
import RawMaterialTable from '../components/RawMaterialTable.vue'
import RawMaterialForm from '../components/RawMaterialForm.vue'
import RawMaterialUsageForm from '../components/RawMaterialUsageForm.vue'
import RawMaterialHistoryModal from '../components/RawMaterialHistoryModal.vue'
import ImportWizard from '../../../shared/components/ImportWizard/ImportWizard.vue'
import ExportButton from '../../../shared/components/ExportButton.vue'
import type { RawMaterial } from '../types'

const store = useRawMaterialsStore()
const authStore = useAuthStore()
const toast = useToastStore()

const loadError = ref('')
const formOpen = ref(false)
const editing = ref<RawMaterial | null>(null)
const usageOpen = ref(false)
const usageMaterialId = ref<number | null>(null)
const historyMaterial = ref<RawMaterial | null>(null)
const showImportWizard = ref(false)

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize } = usePagination(computed(() => store.materials))

function closeModals() {
  formOpen.value = false
  editing.value = null
  usageOpen.value = false
  historyMaterial.value = null
}

function openForm(material: RawMaterial | null) {
  editing.value = material
  formOpen.value = true
}

function openUsage(material: RawMaterial | null) {
  usageMaterialId.value = material ? material.id : null
  usageOpen.value = true
}

function openHistory(material: RawMaterial) {
  historyMaterial.value = material
}

async function confirmDelete(material: RawMaterial) {
  if (!window.confirm(`Delete ${material.name} (${material.unit})?`)) return
  try {
    await acceptQueued(() => store.deleteMaterial(material.id))
  } catch (e) {
    toast.error('Could not delete raw material', errorMessageOf(e))
  }
}

function handleImportClose() {
  showImportWizard.value = false
  store.fetchMaterials()
}

onMounted(async () => {
  try {
    await store.fetchMaterials()
  } catch (e) {
    loadError.value = errorMessageOf(e)
  }
})
</script>

<style scoped>
.raw-materials-page { padding: 1.5rem; }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem; }
.page-title { font-size: 1.5rem; font-weight: 600; }
.header-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
.low-stock-banner { background: #fef3c7; color: #92400e; padding: 0.75rem 1rem; border-radius: 0.375rem; margin-bottom: 1rem; font-size: 0.875rem; }
.form-error { color: #b91c1c; margin-bottom: 0.75rem; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 50; }
.btn-primary:disabled, .btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
