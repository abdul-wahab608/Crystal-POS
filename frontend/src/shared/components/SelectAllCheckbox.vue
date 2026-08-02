<template>
  <input
    type="checkbox"
    :checked="isAllSelected"
    :indeterminate="isPartiallySelected"
    @change="toggleAll"
    class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
    ref="checkbox"
  />
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useBatchActionsStore } from '../stores/batchActions'

const props = defineProps<{
  entityType: string
  allIds: number[]
}>()

const batchStore = useBatchActionsStore()
const checkbox = ref<HTMLInputElement | null>(null)

const selectedIds = computed(() => batchStore.getSelectedIds(props.entityType))

const isAllSelected = computed(() => {
  if (props.allIds.length === 0) return false
  return props.allIds.every(id => selectedIds.value.includes(id))
})

const isPartiallySelected = computed(() => {
  if (props.allIds.length === 0) return false
  const hasSelected = props.allIds.some(id => selectedIds.value.includes(id))
  return hasSelected && !isAllSelected.value
})

// Update indeterminate state manually (can't be set via attribute)
watch([isPartiallySelected, checkbox], ([indeterminate, el]) => {
  if (el) {
    el.indeterminate = indeterminate
  }
}, { immediate: true })

function toggleAll() {
  if (isAllSelected.value) {
    // Deselect all
    batchStore.clearSelection(props.entityType)
  } else {
    // Select all
    batchStore.selectAll(props.entityType, props.allIds)
  }
}
</script>
