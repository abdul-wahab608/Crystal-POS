<template>
  <div class="bg-white rounded-lg shadow p-6 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Search -->
      <div>
        <label for="search" class="block text-sm font-medium text-gray-700 mb-1">
          Search Products
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <input
            id="search"
            v-model="localFilters.search"
            type="text"
            class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            placeholder="Search by name..."
            @input="debouncedApplyFilters"
          />
        </div>
      </div>

      <!-- Unit Filter -->
      <div>
        <label for="unit" class="block text-sm font-medium text-gray-700 mb-1">
          Unit Type
        </label>
        <select
          id="unit"
          v-model="localFilters.unit"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          @change="applyFilters"
        >
          <option value="">All Units</option>
          <option value="BAG">Bag</option>
          <option value="KILO">Kilo</option>
        </select>
      </div>

      <!-- Price Range -->
      <div>
        <label for="min_price" class="block text-sm font-medium text-gray-700 mb-1">
          Min Price
        </label>
        <div class="relative">
          <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">
            $
          </span>
          <input
            id="min_price"
            v-model.number="localFilters.min_price"
            type="number"
            step="0.01"
            min="0"
            class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            placeholder="0.00"
            @input="debouncedApplyFilters"
          />
        </div>
      </div>

      <div>
        <label for="max_price" class="block text-sm font-medium text-gray-700 mb-1">
          Max Price
        </label>
        <div class="relative">
          <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">
            $
          </span>
          <input
            id="max_price"
            v-model.number="localFilters.max_price"
            type="number"
            step="0.01"
            min="0"
            class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            placeholder="0.00"
            @input="debouncedApplyFilters"
          />
        </div>
      </div>
    </div>

    <!-- Additional Filters -->
    <div class="mt-4 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <!-- Stock Status -->
        <div class="flex items-center">
          <input
            id="in_stock"
            v-model="localFilters.in_stock"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            @change="applyFilters"
          />
          <label for="in_stock" class="ml-2 text-sm text-gray-700">
            In Stock Only
          </label>
        </div>

        <!-- Low Stock -->
        <div class="flex items-center">
          <input
            id="low_stock"
            v-model="localFilters.low_stock"
            type="checkbox"
            class="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
            @change="applyFilters"
          />
          <label for="low_stock" class="ml-2 text-sm text-gray-700">
            Low Stock Only
          </label>
        </div>
      </div>

      <!-- Clear Filters -->
      <button
        @click="clearFilters"
        class="text-sm text-gray-600 hover:text-gray-900 flex items-center"
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
        Clear Filters
      </button>
    </div>

    <!-- Active Filters Summary -->
    <div v-if="hasActiveFilters" class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex items-center flex-wrap gap-2">
        <span class="text-sm text-gray-600">Active filters:</span>
        
        <span v-if="localFilters.search" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          Search: "{{ localFilters.search }}"
          <button @click="removeFilter('search')" class="ml-1 text-blue-600 hover:text-blue-800">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </span>

        <span v-if="localFilters.unit" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Unit: {{ localFilters.unit }}
          <button @click="removeFilter('unit')" class="ml-1 text-green-600 hover:text-green-800">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </span>

        <span v-if="localFilters.min_price" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Min Price: ₨{{ localFilters.min_price }}
          <button @click="removeFilter('min_price')" class="ml-1 text-yellow-600 hover:text-yellow-800">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </span>

        <span v-if="localFilters.max_price" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Max Price: ₨{{ localFilters.max_price }}
          <button @click="removeFilter('max_price')" class="ml-1 text-yellow-600 hover:text-yellow-800">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </span>

        <span v-if="localFilters.in_stock" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          In Stock Only
          <button @click="removeFilter('in_stock')" class="ml-1 text-green-600 hover:text-green-800">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </span>

        <span v-if="localFilters.low_stock" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          Low Stock Only
          <button @click="removeFilter('low_stock')" class="ml-1 text-red-600 hover:text-red-800">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type { ProductFilters } from '../types'

interface Props {
  filters: ProductFilters
}

interface Emits {
  (e: 'update:filters', filters: ProductFilters): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const localFilters = reactive<ProductFilters & { low_stock?: boolean }>({
  search: '',
  unit: undefined,
  min_price: undefined,
  max_price: undefined,
  in_stock: undefined,
  low_stock: false
})

// Initialize local filters with props
watch(() => props.filters, (newFilters) => {
  Object.assign(localFilters, newFilters)
}, { immediate: true })

const hasActiveFilters = computed(() => {
  return localFilters.search || 
         localFilters.unit || 
         localFilters.min_price !== undefined || 
         localFilters.max_price !== undefined || 
         localFilters.in_stock !== undefined ||
         localFilters.low_stock
})

// Debounced filter application
let debounceTimer: number | null = null

const debouncedApplyFilters = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    applyFilters()
  }, 300)
}

const applyFilters = () => {
  const filtersToEmit: ProductFilters = {
    search: localFilters.search || undefined,
    unit: localFilters.unit || undefined,
    min_price: localFilters.min_price,
    max_price: localFilters.max_price,
    in_stock: localFilters.in_stock
  }
  
  emit('update:filters', filtersToEmit)
}

const clearFilters = () => {
  Object.assign(localFilters, {
    search: '',
    unit: undefined,
    min_price: undefined,
    max_price: undefined,
    in_stock: undefined,
    low_stock: false
  })
  applyFilters()
}

const removeFilter = (key: keyof typeof localFilters) => {
  if (key === 'search') localFilters.search = ''
  else if (key === 'unit') localFilters.unit = undefined
  else if (key === 'min_price') localFilters.min_price = undefined
  else if (key === 'max_price') localFilters.max_price = undefined
  else if (key === 'in_stock') localFilters.in_stock = undefined
  else if (key === 'low_stock') localFilters.low_stock = false
  
  applyFilters()
}
</script> 