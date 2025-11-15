<template>
  <div class="mb-4">
    <div class="text-lg font-bold">Purchase Stats</div>
    <div class="flex gap-8 mt-2">
      <div>
        <div class="text-2xl font-semibold">{{ purchases.length }}</div>
        <div class="text-gray-500">Total Purchases</div>
      </div>
      <div>
        <div class="text-2xl font-semibold">{{ totalSpent }}</div>
        <div class="text-gray-500">Total Spent</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { Purchase } from '../types'
const props = defineProps<{ purchases: Purchase[] }>()
const totalSpent = computed(() => props.purchases.reduce((sum, p) => sum + p.total, 0))
</script> 