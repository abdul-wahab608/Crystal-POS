<template>
  <div class="mb-4">
    <div class="text-lg font-bold">Sales Stats</div>
    <div class="flex gap-8 mt-2">
      <div>
        <div class="text-2xl font-semibold">{{ sales.length }}</div>
        <div class="text-gray-500">Total Sales</div>
      </div>
      <div>
        <div class="text-2xl font-semibold">{{ totalRevenue }}</div>
        <div class="text-gray-500">Total Revenue</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { Sale } from '../types'
const props = defineProps<{ sales: Sale[] }>()
const totalRevenue = computed(() => props.sales.reduce((sum, s) => sum + s.total, 0))
</script> 