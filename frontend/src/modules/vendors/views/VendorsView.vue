<template>
  <div class="vendors-page">
    <div class="page-header">
      <h1 class="page-title">Vendors</h1>
      <button v-if="authStore.canImport" class="btn-secondary" @click="showImportWizard = true">Import</button>
      <button class="btn-primary" @click="openForm(null)">Add vendor</button>
    </div>

    <VendorStats :vendors="vendorsStore.vendors" />

    <div class="toolbar">
      <VendorFilters v-model="search" />
    </div>

    <p v-if="loadError" class="form-error">{{ loadError }}</p>
    <p v-if="deleteError" class="form-error">{{ deleteError }}</p>
    <ImportWizard v-if="showImportWizard" entityType="vendor" @close="handleImportClose" />

    <VendorTable
      :vendors="pageItems"
      :expandedId="expandedId"
      @toggle-ledger="toggleLedger"
      @edit="openForm"
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

    <div v-if="expandedVendor" class="ledger-panel">
      <div class="ledger-title">Ledger: {{ expandedVendor.name }}</div>
      <VendorLedger :key="expandedVendor.id" :vendor="expandedVendor" />
    </div>

    <div v-if="formOpen" class="modal-overlay" @click.self="closeForm">
      <VendorForm :vendor="editing" @success="closeForm" @cancel="closeForm" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useVendorsStore } from '../stores/vendors'
import { useToastStore } from '../../../shared/stores/toast'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { errorMessageOf } from '../../raw_materials/utils/errorMessage'
import VendorTable from '../components/VendorTable.vue'
import VendorForm from '../components/VendorForm.vue'
import VendorLedger from '../components/VendorLedger.vue'
import VendorFilters from '../components/VendorFilters.vue'
import VendorStats from '../components/VendorStats.vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import type { Vendor } from '../types'
import { useAuthStore } from '../../../shared/stores/auth'
import ImportWizard from '../../../shared/components/ImportWizard/ImportWizard.vue'

const vendorsStore = useVendorsStore()
const toast = useToastStore()
const route = useRoute()

const search = ref('')
const loadError = ref('')
const deleteError = ref('')
const showImportWizard = ref(false)
const authStore = useAuthStore()
const formOpen = ref(false)
const editing = ref<Vendor | null>(null)
const expandedId = ref<number | null>(null)

const filteredVendors = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return vendorsStore.vendors
  return vendorsStore.vendors.filter(vendor =>
    vendor.name.toLowerCase().includes(q)
    || (vendor.contact_person ?? '').toLowerCase().includes(q)
    || (vendor.city ?? '').toLowerCase().includes(q)
    || (vendor.phone ?? '').includes(q),
  )
})

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(filteredVendors)
watch(search, reset)

const expandedVendor = computed(() => vendorsStore.vendors.find(vendor => vendor.id === expandedId.value) ?? null)

function openForm(vendor: Vendor | null) {
  editing.value = vendor
  formOpen.value = true
}

function closeForm() {
  formOpen.value = false
  editing.value = null
}

function toggleLedger(vendor: Vendor) {
  expandedId.value = expandedId.value === vendor.id ? null : vendor.id
}

function handleImportClose() {
  showImportWizard.value = false
  vendorsStore.fetchVendors()
}

async function confirmDelete(vendor: Vendor) {
  if (!window.confirm(`Delete vendor ${vendor.name}?`)) return
  deleteError.value = ''
  try {
    await acceptQueued(() => vendorsStore.deleteVendor(vendor.id))
    if (expandedId.value === vendor.id) expandedId.value = null
  } catch (e) {
    deleteError.value = errorMessageOf(e)
    toast.error('Could not delete vendor', deleteError.value)
  }
}

onMounted(async () => {
  try {
    await vendorsStore.fetchVendors()
    const requested = Number(route.query.vendor)
    if (requested && vendorsStore.vendors.some(vendor => vendor.id === requested)) {
      expandedId.value = requested
    }
  } catch (e) {
    loadError.value = errorMessageOf(e)
  }
})
</script>

<style scoped>
.vendors-page { padding: 1.5rem; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.page-title { font-size: 1.5rem; font-weight: 600; }
.toolbar { max-width: 360px; margin: 1rem 0; }
.form-error { color: #b91c1c; margin-bottom: 0.75rem; }
.ledger-panel { margin-top: 1rem; background: white; border: 1px solid #e5e7eb; border-radius: 0.5rem; overflow: hidden; }
.ledger-title { padding: 0.75rem 1rem; font-weight: 600; border-bottom: 1px solid #e5e7eb; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 1rem; }
.btn-primary { cursor: pointer; border: none; }
</style>
