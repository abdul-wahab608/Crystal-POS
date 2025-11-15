<template>
  <div class="vendor-products-section">
    <h4 class="products-heading">Products Supplied by This Vendor</h4>
    
    <!-- Add Product Section -->
    <div class="bg-gray-50 p-3 rounded mb-4">
      <h4 class="text-sm font-medium mb-2">Add Product/Raw Material</h4>
      <div class="grid grid-cols-2 gap-2 mb-2">
        <div>
          <label class="block text-xs mb-1">Product Type</label>
          <select v-model="newItem.product_type" class="w-full border px-2 py-1 rounded text-sm">
            <option value="PRODUCT">Finished Product</option>
            <option value="RAW_MATERIAL">Raw Material</option>
          </select>
        </div>
        <div>
          <label class="block text-xs mb-1">
            {{ newItem.product_type === 'PRODUCT' ? 'Product' : 'Raw Material' }}
          </label>
          <select 
            v-model="newItem.item_id" 
            class="w-full border px-2 py-1 rounded text-sm"
            required
          >
            <option value="">Select...</option>
            <option 
              v-for="item in availableItems" 
              :key="item.id" 
              :value="item.id"
            >
              {{ item.name }} ({{ item.unit }})
            </option>
          </select>
        </div>
      </div>
      <div class="grid grid-cols-3 gap-2 mb-2">
        <div>
          <label class="block text-xs mb-1">Unit Price ($)</label>
          <input 
            v-model.number="newItem.unit_price" 
            type="number" 
            step="0.01"
            class="w-full border px-2 py-1 rounded text-sm"
            required
          />
        </div>
        <div>
          <label class="block text-xs mb-1">Min Order Qty</label>
          <input 
            v-model.number="newItem.minimum_order_quantity" 
            type="number" 
            step="0.01"
            class="w-full border px-2 py-1 rounded text-sm"
          />
        </div>
        <div>
          <label class="block text-xs mb-1">Lead Time (days)</label>
          <input 
            v-model.number="newItem.lead_time_days" 
            type="number"
            class="w-full border px-2 py-1 rounded text-sm"
          />
        </div>
      </div>
      <div class="mb-2">
        <label class="block text-xs mb-1">Notes</label>
        <input 
          v-model="newItem.notes" 
          class="w-full border px-2 py-1 rounded text-sm"
        />
      </div>
      <div class="flex gap-2 items-center mb-2">
        <label class="flex items-center text-sm">
          <input v-model="newItem.is_preferred" type="checkbox" class="mr-1" />
          Preferred Supplier
        </label>
        <label class="flex items-center text-sm">
          <input v-model="newItem.is_active" type="checkbox" class="mr-1" />
          Active
        </label>
      </div>
      <button 
        type="button"
        @click="addProduct" 
        class="px-3 py-1 bg-green-600 text-white rounded text-sm"
        :disabled="!newItem.item_id || !newItem.unit_price"
      >
        Add to List
      </button>
    </div>

    <!-- Products List -->
    <div v-if="vendorProducts.length > 0" class="space-y-2">
      <div 
        v-for="(item, index) in vendorProducts" 
        :key="index"
        class="border rounded p-3 flex justify-between items-start"
      >
        <div class="flex-1">
          <div class="font-medium text-sm">{{ item.item_name }}</div>
          <div class="text-xs text-gray-600">
            Price: ${{ item.unit_price }} | 
            Min Order: {{ item.minimum_order_quantity }} | 
            Lead Time: {{ item.lead_time_days }} days
          </div>
          <div v-if="item.notes" class="text-xs text-gray-500 mt-1">{{ item.notes }}</div>
          <div class="flex gap-2 mt-1">
            <span v-if="item.is_preferred" class="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">
              Preferred
            </span>
            <span 
              :class="item.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              class="text-xs px-2 py-0.5 rounded"
            >
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
        <button 
          type="button"
          @click="removeProduct(index)" 
          class="text-red-600 hover:text-red-800 ml-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
    <div v-else class="text-sm text-gray-500 text-center py-4">
      No products added yet. Add products above to start tracking.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useProductsStore } from '@/modules/products/stores/products'
import { useRawMaterialsStore } from '@/modules/raw_materials/stores/raw_materials'

interface VendorProduct {
  product_type: 'PRODUCT' | 'RAW_MATERIAL'
  item_id: number
  item_name: string
  unit_price: number
  minimum_order_quantity: number
  lead_time_days: number
  is_preferred: boolean
  is_active: boolean
  notes: string
}

const props = defineProps<{
  modelValue: VendorProduct[]
}>()

const emit = defineEmits(['update:modelValue'])

const productsStore = useProductsStore()
const rawMaterialsStore = useRawMaterialsStore()

const vendorProducts = ref<VendorProduct[]>([...props.modelValue])

const newItem = ref({
  product_type: 'PRODUCT' as 'PRODUCT' | 'RAW_MATERIAL',
  item_id: null as number | null,
  unit_price: 0,
  minimum_order_quantity: 0,
  lead_time_days: 0,
  is_preferred: false,
  is_active: true,
  notes: ''
})

const availableItems = computed(() => {
  if (newItem.value.product_type === 'PRODUCT') {
    return productsStore.products
  } else {
    return rawMaterialsStore.materials
  }
})

watch(vendorProducts, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

watch(() => props.modelValue, (newVal) => {
  vendorProducts.value = [...newVal]
}, { deep: true })

watch(() => newItem.value.product_type, () => {
  newItem.value.item_id = null
})

function addProduct() {
  if (!newItem.value.item_id || !newItem.value.unit_price) return
  
  const selectedItem = availableItems.value.find(item => item.id === newItem.value.item_id)
  if (!selectedItem) return
  
  vendorProducts.value.push({
    product_type: newItem.value.product_type,
    item_id: newItem.value.item_id,
    item_name: `${selectedItem.name} (${selectedItem.unit})`,
    unit_price: newItem.value.unit_price,
    minimum_order_quantity: newItem.value.minimum_order_quantity,
    lead_time_days: newItem.value.lead_time_days,
    is_preferred: newItem.value.is_preferred,
    is_active: newItem.value.is_active,
    notes: newItem.value.notes
  })
  
  // Reset form
  newItem.value = {
    product_type: 'PRODUCT',
    item_id: null,
    unit_price: 0,
    minimum_order_quantity: 0,
    lead_time_days: 0,
    is_preferred: false,
    is_active: true,
    notes: ''
  }
}

function removeProduct(index: number) {
  vendorProducts.value.splice(index, 1)
}

onMounted(async () => {
  await productsStore.fetchProducts()
  await rawMaterialsStore.fetchMaterials()
})
</script>

<style scoped>
.vendor-products-section {
  margin-top: 1rem;
}

.products-heading {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}
</style>
