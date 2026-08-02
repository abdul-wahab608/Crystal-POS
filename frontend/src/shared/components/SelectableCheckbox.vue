<template>
  <input
    type="checkbox"
    :checked="isChecked"
    @change="toggle"
    class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useBatchActionsStore } from '../stores/batchActions'

const props = defineProps<{
  entityType: string
  id: number
}>()

const batchStore = useBatchActionsStore()

const isChecked = computed(() => batchStore.isSelected(props.entityType, props.id))

function toggle() {
  batchStore.toggleSelection(props.entityType, props.id)
}
</script>
