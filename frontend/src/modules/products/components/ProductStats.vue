<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
    <!-- Total Products -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-600">Total Products</p>
          <p class="text-2xl font-semibold text-gray-900">{{ products.length }}</p>
        </div>
      </div>
      <div class="mt-4">
        <div class="flex items-center text-sm">
          <span class="text-green-600 font-medium">+{{ newThisMonth }}</span>
          <span class="text-gray-500 ml-1">this month</span>
        </div>
      </div>
    </div>

    <!-- Total Stock Value -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-600">Total Stock Value</p>
          <p class="text-2xl font-semibold text-gray-900">₨{{ totalStockValue.toFixed(2) }}</p>
        </div>
      </div>
      <div class="mt-4">
        <div class="flex items-center text-sm">
          <span :class="stockValueChange >= 0 ? 'text-green-600' : 'text-red-600'" class="font-medium">
            {{ stockValueChange >= 0 ? '+' : '' }}{{ stockValueChange.toFixed(2) }}%
          </span>
          <span class="text-gray-500 ml-1">vs last month</span>
        </div>
      </div>
    </div>

    <!-- Low Stock Items -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-600">Low Stock Items</p>
          <p class="text-2xl font-semibold text-gray-900">{{ lowStockCount }}</p>
        </div>
      </div>
      <div class="mt-4">
        <div class="flex items-center text-sm">
          <span class="text-red-600 font-medium">{{ lowStockPercentage }}%</span>
          <span class="text-gray-500 ml-1">of total products</span>
        </div>
      </div>
    </div>

    <!-- Out of Stock -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-600">Out of Stock</p>
          <p class="text-2xl font-semibold text-gray-900">{{ outOfStockItems }}</p>
        </div>
      </div>
      <div class="mt-4">
        <div class="flex items-center text-sm">
          <span class="text-yellow-600 font-medium">{{ outOfStockPercentage }}%</span>
          <span class="text-gray-500 ml-1">of total products</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Product } from '../types'

interface Props {
  products: Product[]
}

const props = defineProps<Props>()

const totalStockValue = computed(() => props.products.reduce((sum, p) => sum + (p.quantity * p.cop), 0))
const lowStockCount = computed(() => props.products.filter(p => p.quantity < 10).length)

const outOfStockItems = computed(() => props.products.filter(product => product.quantity === 0).length)

const lowStockPercentage = computed(() => {
  const totalProducts = props.products.length
  const lowStockItems = lowStockCount.value
  return totalProducts > 0 ? Math.round((lowStockItems / totalProducts) * 100) : 0
})

const outOfStockPercentage = computed(() => {
  const totalProducts = props.products.length
  const outOfStockItemsCount = outOfStockItems.value
  return totalProducts > 0 ? Math.round((outOfStockItemsCount / totalProducts) * 100) : 0
})

// Mock data for demonstration - in real app, this would come from API
const newThisMonth = Math.floor(Math.random() * 10) + 1
const stockValueChange = (Math.random() * 20) - 10 // -10 to +10%
</script> 