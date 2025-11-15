<template>
  <div class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
    <form @submit.prevent="onSubmit" class="bg-white p-6 rounded shadow w-96">
      <h2 class="text-lg font-bold mb-4">{{ product?.id ? 'Edit' : 'Add' }} Product</h2>
      <div class="mb-3">
        <label for="name" class="block text-sm font-medium mb-1">Name</label>
        <input v-model="form.name" id="name" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div v-if="!isExistingProduct" class="mb-3">
        <label for="unit" class="block text-sm font-medium mb-1">Unit</label>
        <select v-model="form.unit" id="unit" class="w-full border px-2 py-1 rounded" required>
          <option value="BAG">Bag</option>
          <option value="KILO">Kilo</option>
          <option value="PCS">Pieces</option>
          <option value="KG">Kilograms</option>
          <option value="L">Liters</option>
          <option value="M">Meters</option>
          <option value="BOX">Box</option>
          <option value="PACK">Pack</option>
          <option value="UNIT">Unit</option>
          <option value="GRAM">Grams</option>
          <option value="TON">Tons</option>
          <option value="GALLON">Gallons</option>
          <option value="FOOT">Feet</option>
          <option value="YARD">Yards</option>
          <option value="CM">Centimeters</option>
          <option value="MM">Millimeters</option>
          <option value="INCH">Inches</option>
          <option value="POUND">Pounds</option>
          <option value="OUNCE">Ounces</option>
          <option value="CUP">Cups</option>
          <option value="TABLESPOON">Tablespoons</option>
          <option value="TEASPOON">Teaspoons</option>
        </select>
      </div>
      <div v-if="!isExistingProduct" class="mb-3">
        <label for="cop" class="block text-sm font-medium mb-1">Cost of Production (COP) per unit</label>
        <input v-model.number="form.cop" id="cop" type="number" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="quantity" class="block text-sm font-medium mb-1">Quantity</label>
        <input v-model.number="form.quantity" id="quantity" type="number" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <button type="button" @click="$emit('close')" class="px-3 py-1 bg-gray-200 rounded">Cancel</button>
        <button type="submit" class="px-3 py-1 bg-blue-600 text-white rounded">Save</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, defineProps, defineEmits } from 'vue'
import { useProductsStore } from '../stores/products'
import type { Product, CreateProductRequest } from '../types'

interface Props {
  product?: Product | null
}

const props = defineProps<Props>()
const emit = defineEmits(['save', 'close'])
const store = useProductsStore()

const form = ref<CreateProductRequest>({
  name: '',
  unit: 'BAG',
  cop: 0,
  quantity: 0
})

const isExistingProduct = computed(() => {
  return !!store.products.find(p => p.name.trim().toLowerCase() === form.value.name.trim().toLowerCase())
})

watch(() => props.product, (val) => {
  if (val) {
    form.value = { 
      name: val.name, 
      unit: val.unit, 
      cop: val.cop, 
      quantity: val.quantity 
    }
  } else {
    form.value = { 
      name: '', 
      unit: 'BAG', 
      cop: 0, 
      quantity: 0 
    }
  }
}, { immediate: true })

function onSubmit() {
  emit('save', { ...form.value })
}
</script> 