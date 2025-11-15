<template>
  <div class="mb-4">
    <div class="text-lg font-bold">Vendor Stats</div>
    <div class="flex gap-8 mt-2">
      <div>
        <div class="text-2xl font-semibold">{{ vendors.length }}</div>
        <div class="text-gray-500">Total Vendors</div>
      </div>
      <div>
        <div class="text-2xl font-semibold">{{ activeVendors }}</div>
        <div class="text-gray-500">Active Vendors</div>
      </div>
      <div>
        <div class="text-2xl font-semibold">{{ inactiveVendors }}</div>
        <div class="text-gray-500">Inactive Vendors</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Vendor } from '../types'

const props = defineProps<{ vendors: Vendor[] }>()

const activeVendors = computed(() => props.vendors.filter(v => v.is_active).length)
const inactiveVendors = computed(() => props.vendors.filter(v => !v.is_active).length)
</script> 