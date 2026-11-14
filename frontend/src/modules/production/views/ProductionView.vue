<template>
  <div class="production-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Production</h1>
        <p class="muted">Turn raw materials into finished stock. Stock on each run is reversed when it is deleted.</p>
      </div>
      <button class="btn-primary" @click="formOpen = true">New run</button>
    </div>

    <p v-if="loadError" class="form-error">{{ loadError }}</p>
    <p v-if="loading" class="muted">Loading runs...</p>

    <div v-else class="table-container">
      <table v-if="productionStore.runs.length" class="runs-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Reference</th>
            <th>Outputs</th>
            <th>Inputs</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="run in pageItems" :key="run.id">
            <td>{{ new Date(run.date).toLocaleDateString() }}</td>
            <td>
              {{ run.reference || `Run #${run.id}` }}
              <div v-if="run.notes" class="muted small">{{ run.notes }}</div>
            </td>
            <td>
              <div v-for="item in run.items" :key="item.id">
                {{ item.variant_label }}: <strong>{{ Number(item.quantity).toFixed(2) }} {{ item.unit }}</strong>
              </div>
            </td>
            <td>
              <div v-for="input in run.inputs" :key="input.id">
                {{ input.raw_material_name }}: {{ Number(input.quantity).toFixed(2) }} {{ input.unit }}
              </div>
              <span v-if="!run.inputs.length" class="muted">None</span>
            </td>
            <td>
              <button v-if="authStore.isManager" class="link-btn danger" @click="confirmDelete(run)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No production runs yet.</p>
      <PaginationBar
        v-if="productionStore.runs.length"
        :page="page"
        :totalPages="totalPages"
        :total="total"
        :pageSize="pageSize"
        @update:page="goTo"
        @update:pageSize="setPageSize"
      />
    </div>

    <div v-if="formOpen" class="modal-overlay" @click.self="formOpen = false">
      <ProductionRunForm @saved="onSaved" @cancel="formOpen = false" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProductionStore } from '../stores/production'
import { useToastStore } from '../../../shared/stores/toast'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { usePagination } from '../../../shared/composables/usePagination'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { errorMessageOf } from '../../raw_materials/utils/errorMessage'
import ProductionRunForm from '../components/ProductionRunForm.vue'
import type { ProductionRun } from '../types'
import { useAuthStore } from '../../../shared/stores/auth'
const authStore = useAuthStore()

const productionStore = useProductionStore()
const toast = useToastStore()
const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize } = usePagination(computed(() => productionStore.runs))

const loading = ref(false)
const loadError = ref('')
const formOpen = ref(false)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    await productionStore.fetchRuns()
  } catch (e) {
    loadError.value = errorMessageOf(e)
  } finally {
    loading.value = false
  }
}

async function confirmDelete(run: ProductionRun) {
  if (!window.confirm(`Delete ${run.reference || `run #${run.id}`}? Its outputs are removed and its raw materials are restored.`)) return
  try {
    await acceptQueued(() => productionStore.deleteRun(run.id))
  } catch (e) {
    toast.error('Could not delete production run', errorMessageOf(e))
  }
}

async function onSaved() {
  formOpen.value = false
  await load()
}

onMounted(load)
</script>

<style scoped>
.production-page { padding: 1.5rem; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 1.25rem; }
.page-title { font-size: 1.5rem; font-weight: 600; }
.muted { color: #6b7280; font-size: 0.875rem; }
.small { font-size: 0.8125rem; }
.form-error { color: #b91c1c; margin-bottom: 0.75rem; }
.table-container { background: white; border-radius: 0.5rem; border: 1px solid #e5e7eb; overflow-x: auto; }
.runs-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.runs-table th, .runs-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: left; vertical-align: top; }
.runs-table th { background: #f9fafb; font-weight: 600; }
.link-btn { background: none; border: none; cursor: pointer; font-size: 0.875rem; color: #2563eb; }
.link-btn.danger { color: #b91c1c; }
.empty-state { padding: 2rem; text-align: center; color: #6b7280; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 1rem; }
.btn-primary { cursor: pointer; border: none; }
</style>
