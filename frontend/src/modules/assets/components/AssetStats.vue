<template>
  <div class="mb-4">
    <div class="text-lg font-bold">Asset Stats</div>
    <div class="flex gap-8 mt-2">
      <div>
        <div class="text-2xl font-semibold">{{ assets.length }}</div>
        <div class="text-gray-500">Total Assets</div>
      </div>
      <div>
        <div class="text-2xl font-semibold">{{ totalValue }}</div>
        <div class="text-gray-500">Total Value</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { Asset } from '../types'
const props = defineProps<{ assets: Asset[] }>()
const totalValue = computed(() => props.assets.reduce((sum, a) => sum + a.value, 0))
</script> 