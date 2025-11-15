<template>
  <div class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
    <form @submit.prevent="onSubmit" class="bg-white p-6 rounded shadow w-96">
      <h2 class="text-lg font-bold mb-4">Generate Report</h2>
      <div class="mb-3">
        <label for="type" class="block text-sm font-medium mb-1">Report Type</label>
        <select v-model="form.type" id="type" class="w-full border px-2 py-1 rounded" required>
          <option value="SALES">Sales Report</option>
          <option value="INVENTORY">Inventory Report</option>
          <option value="FINANCIAL">Financial Report</option>
        </select>
      </div>
      <div class="mb-3">
        <label for="period" class="block text-sm font-medium mb-1">Period</label>
        <select v-model="form.period" id="period" class="w-full border px-2 py-1 rounded" required>
          <option value="DAILY">Daily</option>
          <option value="WEEKLY">Weekly</option>
          <option value="MONTHLY">Monthly</option>
          <option value="YEARLY">Yearly</option>
        </select>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <button type="button" @click="$emit('close')" class="px-3 py-1 bg-gray-200 rounded">Cancel</button>
        <button type="submit" class="px-3 py-1 bg-blue-600 text-white rounded">Generate</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'

interface Props {
  report?: any
}

const props = defineProps<Props>()
const emit = defineEmits(['save', 'close'])

const form = ref({
  type: 'SALES',
  period: 'MONTHLY'
})

watch(() => props.report, (val) => {
  if (val) {
    form.value = { ...val }
  } else {
    form.value = {
      type: 'SALES',
      period: 'MONTHLY'
    }
  }
}, { immediate: true })

function onSubmit() {
  emit('save', { ...form.value })
}
</script> 