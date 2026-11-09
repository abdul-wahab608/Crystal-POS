<template>
  <section class="panel">
    <form class="add-form" @submit.prevent="addUnit">
      <input v-model="form.code" class="form-input" placeholder="Code, e.g. CARTON" required maxlength="20" />
      <input v-model="form.name" class="form-input" placeholder="Name, e.g. Cartons" required maxlength="50" />
      <button type="submit" class="btn-primary" :disabled="saving">Add Unit</button>
    </form>

    <p v-if="error" class="form-error">{{ error }}</p>

    <table class="list-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Code</th>
          <th>Type</th>
          <th class="actions-col"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="unit in pageItems" :key="unit.id">
          <td>{{ unit.name }}</td>
          <td><code>{{ unit.code }}</code></td>
          <td>{{ unit.is_system ? 'System' : 'Custom' }}</td>
          <td class="actions-col">
            <button v-if="!unit.is_system" type="button" class="action-btn delete" @click="removeUnit(unit.id)">Delete</button>
          </td>
        </tr>
        <tr v-if="!unitsStore.units.length && !unitsStore.loading">
          <td colspan="4" class="empty">No units yet.</td>
        </tr>
      </tbody>
    </table>
    <PaginationBar
      v-if="unitsStore.units.length"
      :page="page"
      :totalPages="totalPages"
      :total="total"
      :pageSize="pageSize"
      @update:page="goTo"
      @update:pageSize="setPageSize"
    />
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useUnitsStore } from '../../../shared/stores/units'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'

const unitsStore = useUnitsStore()
const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize } = usePagination(computed(() => unitsStore.units))
const form = reactive({ code: '', name: '' })
const saving = ref(false)
const error = ref('')

onMounted(() => {
  unitsStore.fetchUnits().catch(() => { error.value = 'Could not load units.' })
})

async function addUnit() {
  saving.value = true
  error.value = ''
  try {
    await acceptQueued(() => unitsStore.createUnit(form.code.trim().toUpperCase(), form.name.trim()))
    form.code = ''
    form.name = ''
  } catch (e: any) {
    error.value = e.response?.data?.code?.[0] || e.response?.data?.detail || 'Could not add unit.'
  } finally {
    saving.value = false
  }
}

async function removeUnit(id: number) {
  error.value = ''
  if (!confirm('Delete this unit?')) return
  try {
    await acceptQueued(() => unitsStore.deleteUnit(id))
  } catch (e: any) {
    error.value = e.response?.data?.error || 'Could not delete unit.'
  }
}
</script>

<style scoped>
.panel { display: flex; flex-direction: column; gap: 12px; }
.add-form { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.list-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.list-table th, .list-table td { padding: 8px 10px; border-bottom: 1px solid #e5e7eb; text-align: left; }
.actions-col { width: 120px; text-align: right; }
.action-btn { background: none; border: none; cursor: pointer; font-size: 0.8125rem; }
.action-btn.delete { color: #b91c1c; }
.empty { text-align: center; color: #6b7280; }
.form-error { color: #b91c1c; font-size: 0.875rem; }
</style>
