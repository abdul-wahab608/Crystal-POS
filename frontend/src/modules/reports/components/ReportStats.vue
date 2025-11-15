<template>
  <div class="mb-4">
    <div class="text-lg font-bold">Report Stats</div>
    <div class="flex gap-8 mt-2">
      <div>
        <div class="text-2xl font-semibold">{{ reports.length }}</div>
        <div class="text-gray-500">Total Reports</div>
      </div>
      <div>
        <div class="text-2xl font-semibold">{{ recentReports }}</div>
        <div class="text-gray-500">This Month</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { Report } from '../types'
const props = defineProps<{ reports: Report[] }>()
const recentReports = computed(() => {
  const now = new Date()
  const thisMonth = now.getMonth()
  const thisYear = now.getFullYear()
  return props.reports.filter(r => {
    const reportDate = new Date(r.generated_at)
    return reportDate.getMonth() === thisMonth && reportDate.getFullYear() === thisYear
  }).length
})
</script> 