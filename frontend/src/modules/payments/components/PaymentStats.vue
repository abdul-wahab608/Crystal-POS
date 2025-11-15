<template>
  <div class="mb-4">
    <div class="text-lg font-bold">Payment Stats</div>
    <div class="flex gap-8 mt-2">
      <div>
        <div class="text-2xl font-semibold">{{ payments.length }}</div>
        <div class="text-gray-500">Total Payments</div>
      </div>
      <div>
        <div class="text-2xl font-semibold">{{ totalAmount }}</div>
        <div class="text-gray-500">Total Amount</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { Payment } from '../types'
const props = defineProps<{ payments: Payment[] }>()
const totalAmount = computed(() => props.payments.reduce((sum, p) => sum + p.amount, 0))
</script> 