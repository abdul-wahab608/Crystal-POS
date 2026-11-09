<template>
  <nav class="pagination-bar" aria-label="Pagination">
    <p class="pagination-summary">{{ summary }}</p>
    <div class="pagination-controls">
      <button
        type="button"
        class="btn-secondary"
        :disabled="page <= 1"
        @click="emit('update:page', page - 1)"
      >
        Previous
      </button>
      <span class="pagination-page" aria-live="polite">Page {{ page }} of {{ totalPages }}</span>
      <button
        type="button"
        class="btn-secondary"
        :disabled="page >= totalPages"
        @click="emit('update:page', page + 1)"
      >
        Next
      </button>
      <label class="pagination-size">
        <span>Rows</span>
        <select :value="pageSize" @change="emit('update:pageSize', Number(($event.target as HTMLSelectElement).value))">
          <option v-for="option in pageSizeOptions" :key="option" :value="option">{{ option }}</option>
        </select>
      </label>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PAGE_SIZE_OPTIONS } from '../composables/usePagination'

const props = withDefaults(defineProps<{
  page: number
  totalPages: number
  total: number
  pageSize: number
  pageSizeOptions?: number[]
}>(), {
  pageSizeOptions: () => PAGE_SIZE_OPTIONS,
})

const emit = defineEmits<{
  'update:page': [value: number]
  'update:pageSize': [value: number]
}>()

const summary = computed(() => {
  if (props.total === 0) return 'Showing 0 of 0'
  const start = (props.page - 1) * props.pageSize + 1
  const end = Math.min(props.page * props.pageSize, props.total)
  return `Showing ${start}-${end} of ${props.total}`
})
</script>

<style scoped>
.pagination-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  padding: 0.75rem 0;
}

.pagination-summary {
  margin: 0;
  font-size: 0.875rem;
  color: #4b5563;
}

.pagination-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.pagination-page {
  font-size: 0.875rem;
  color: #4b5563;
  white-space: nowrap;
}

.pagination-size {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: #4b5563;
}

.pagination-size select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: #fff;
}

.pagination-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .pagination-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .pagination-controls {
    justify-content: space-between;
  }
}
</style>
