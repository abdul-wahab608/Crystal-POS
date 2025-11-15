<template>
  <div class="mb-4">
    <div class="text-lg font-bold">Customer Stats</div>
    <div class="flex gap-8 mt-2">
      <div>
        <div class="text-2xl font-semibold">{{ customers.length }}</div>
        <div class="text-gray-500">Total Customers</div>
      </div>
      <div>
        <div class="text-2xl font-semibold">{{ totalBalance }}</div>
        <div class="text-gray-500">Total Receivables</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { Customer } from '../types'
const props = defineProps<{ customers: Customer[] }>()
const totalBalance = computed(() => props.customers.reduce((sum, c) => sum + c.balance, 0))
</script> 