<template>
  <section class="panel">
    <form class="add-form" @submit.prevent="submitAdd">
      <input v-model="newName" class="form-input" :placeholder="`New ${label} name`" maxlength="100" required />
      <button type="submit" class="btn-primary" :disabled="!newName.trim()">Add {{ label }}</button>
    </form>

    <p v-if="error" class="form-error">{{ error }}</p>

    <table class="list-table">
      <thead>
        <tr>
          <th>Name</th>
          <th class="actions-col"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in pageItems" :key="item.id">
          <td>
            <input
              v-if="editingId === item.id"
              v-model="editName"
              class="form-input"
              maxlength="100"
              @keydown.enter.prevent="saveRename(item.id)"
              @keydown.esc="cancelRename"
            />
            <span v-else>{{ item.name }}</span>
          </td>
          <td class="actions-col">
            <template v-if="editingId === item.id">
              <button type="button" class="action-btn edit" @click="saveRename(item.id)">Save</button>
              <button type="button" class="action-btn" @click="cancelRename">Cancel</button>
            </template>
            <template v-else>
              <button type="button" class="action-btn edit" @click="startRename(item)">Rename</button>
              <button type="button" class="action-btn delete" @click="confirmRemove(item)">Delete</button>
            </template>
          </td>
        </tr>
        <tr v-if="!items.length">
          <td colspan="2" class="empty">No {{ plural }} yet.</td>
        </tr>
      </tbody>
    </table>
    <PaginationBar
      v-if="items.length"
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
import { ref, computed } from 'vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'

interface NamedItem {
  id: number
  name: string
}

const props = defineProps<{
  items: NamedItem[]
  label: string
  plural: string
  error: string
}>()

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize } = usePagination(computed(() => props.items))

const emit = defineEmits<{
  add: [name: string]
  rename: [id: number, name: string]
  remove: [id: number]
}>()

const newName = ref('')
const editingId = ref<number | null>(null)
const editName = ref('')

function submitAdd() {
  const name = newName.value.trim()
  if (!name) return
  emit('add', name)
  newName.value = ''
}

function startRename(item: NamedItem) {
  editingId.value = item.id
  editName.value = item.name
}

function cancelRename() {
  editingId.value = null
}

function saveRename(id: number) {
  const name = editName.value.trim()
  const current = props.items.find(i => i.id === id)
  if (name && current && name !== current.name) emit('rename', id, name)
  editingId.value = null
}

function confirmRemove(item: NamedItem) {
  if (confirm(`Delete ${props.label} "${item.name}"?`)) emit('remove', item.id)
}
</script>

<style scoped>
.panel { display: flex; flex-direction: column; gap: 12px; }
.add-form { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.add-form .form-input { min-width: 240px; }
.list-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.list-table th, .list-table td { padding: 8px 10px; border-bottom: 1px solid #e5e7eb; text-align: left; }
.actions-col { width: 200px; text-align: right; white-space: nowrap; }
.action-btn { background: none; border: none; cursor: pointer; font-size: 0.8125rem; margin-left: 10px; }
.action-btn.edit { color: #4338ca; }
.action-btn.delete { color: #b91c1c; }
.empty { text-align: center; color: #6b7280; }
.form-error { color: #b91c1c; font-size: 0.875rem; }
</style>
