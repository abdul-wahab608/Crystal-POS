<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <h2 class="modal-title">Usage history: {{ material.name }} ({{ material.unit }})</h2>
        <button class="close-btn" aria-label="Close" @click="$emit('close')">&times;</button>
      </div>
      <p v-if="loading" class="muted">Loading...</p>
      <p v-else-if="error" class="form-error">{{ error }}</p>
      <p v-else-if="!usage.length" class="muted">No usage recorded yet.</p>
      <table v-else class="history-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Quantity</th>
            <th>Reference</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in usage" :key="row.id">
            <td>{{ formatDate(row.date_used) }}</td>
            <td>{{ Number(row.quantity_used).toFixed(2) }} {{ material.unit }}</td>
            <td>{{ row.reference || '-' }}</td>
            <td>{{ row.notes || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRawMaterialsStore } from '../stores/raw_materials'
import { errorMessageOf } from '../utils/errorMessage'
import type { RawMaterial, RawMaterialUsage } from '../types'

const props = defineProps<{ material: RawMaterial }>()
defineEmits<{ close: [] }>()

const materialsStore = useRawMaterialsStore()
const usage = ref<RawMaterialUsage[]>([])
const loading = ref(true)
const error = ref('')

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

onMounted(async () => {
  try {
    usage.value = await materialsStore.fetchUsage(props.material.id)
  } catch (e) {
    error.value = errorMessageOf(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 50; }
.modal-card { background: white; border-radius: 0.5rem; padding: 1.5rem; width: min(680px, 94vw); max-height: 80vh; overflow: auto; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.modal-title { font-size: 1.125rem; font-weight: 600; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #6b7280; }
.history-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.history-table th, .history-table td { text-align: left; padding: 0.5rem; border-bottom: 1px solid #e5e7eb; }
.muted { color: #6b7280; }
.form-error { color: #b91c1c; }
</style>
