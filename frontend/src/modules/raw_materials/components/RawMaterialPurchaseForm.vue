<template>
  <div class="form-container">
    <div class="form-header">
      <h2>Record Material Purchase</h2>
      <button class="close-btn" @click="$emit('cancel')">×</button>
    </div>
    
    <form @submit.prevent="handleSubmit" class="form">
      <div class="form-group">
        <label for="raw_material">Material *</label>
        <select 
          id="raw_material"
          v-model="form.raw_material" 
          required 
          class="form-input"
          @change="onMaterialChange"
        >
          <option value="">Select a material</option>
          <option 
            v-for="material in store.materials" 
            :key="material.id" 
            :value="material.id"
          >
            {{ material.name }} ({{ material.unit }}) - Stock: {{ material.available_stock || material.quantity }}
          </option>
        </select>
      </div>

      <div v-if="selectedMaterial" class="material-info">
        <strong>{{ selectedMaterial.name }}</strong>
        <span class="stock-info">Current Stock: {{ selectedMaterial.available_stock || selectedMaterial.quantity }} {{ selectedMaterial.unit }}</span>
        <span class="unit-price">Unit Price: ₨{{ selectedMaterial.unit_price }}</span>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="quantity_purchased">Quantity Purchased *</label>
          <input 
            id="quantity_purchased"
            v-model.number="form.quantity_purchased" 
            type="number" 
            step="0.01"
            min="0.01"
            required 
            class="form-input"
            placeholder="Enter quantity purchased"
          />
        </div>
        
        <div class="form-group">
          <label for="unit_price">Unit Price *</label>
          <input 
            id="unit_price"
            v-model.number="form.unit_price" 
            type="number" 
            step="0.01"
            min="0"
            required 
            class="form-input"
            placeholder="0.00"
          />
        </div>
      </div>
      
      <div class="form-group">
        <label>Total Amount</label>
        <div class="total-display">
          ₨{{ totalAmount.toFixed(2) }}
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="supplier">Supplier / Vendor *</label>
          <select 
            id="supplier"
            v-model="form.supplier" 
            class="form-input"
            required
          >
            <option value="">Select vendor</option>
            <option 
              v-for="vendor in vendorsStore.vendors.filter(v => v.is_active)" 
              :key="vendor.id" 
              :value="vendor.name"
            >
              {{ vendor.name }}
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="invoice_number">Invoice Number</label>
          <input 
            id="invoice_number"
            v-model="form.invoice_number" 
            type="text" 
            class="form-input"
            placeholder="Invoice #"
          />
        </div>
      </div>
      
      <div class="form-group">
        <label for="notes">Notes</label>
        <textarea 
          id="notes"
          v-model="form.notes" 
          class="form-input"
          rows="3"
          placeholder="Additional notes about this purchase"
        ></textarea>
      </div>
      
      <div class="form-actions">
        <button type="button" @click="$emit('cancel')" class="btn-secondary">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="loading || !form.raw_material">
          {{ loading ? 'Recording...' : 'Record Purchase' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRawMaterialsStore } from '../stores/raw_materials'
import { useVendorsStore } from '@/modules/vendors/stores/vendors'
import type { RawMaterial, CreateRawMaterialPurchase } from '../types'

const emit = defineEmits<{
  success: []
  cancel: []
}>()

const store = useRawMaterialsStore()
const vendorsStore = useVendorsStore()
const loading = ref(false)

const form = ref<CreateRawMaterialPurchase>({
  raw_material: 0,
  quantity_purchased: 0,
  unit_price: 0,
  supplier: '',
  invoice_number: '',
  notes: ''
})

const selectedMaterial = computed(() => {
  if (!form.value.raw_material) return null
  return store.materials.find(m => m.id === form.value.raw_material) || null
})

const totalAmount = computed(() => {
  return form.value.quantity_purchased * form.value.unit_price
})

function onMaterialChange() {
  if (selectedMaterial.value) {
    form.value.unit_price = selectedMaterial.value.unit_price
    form.value.supplier = selectedMaterial.value.supplier || ''
  }
}

async function handleSubmit() {
  if (!form.value.raw_material) {
    alert('Please select a material')
    return
  }
  
  loading.value = true
  try {
    await store.createPurchase(form.value)
    emit('success')
  } catch (error) {
    // Handle error silently
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Fetch materials if not already loaded
  if (store.materials.length === 0) {
    store.fetchMaterials()
  }
  // Fetch vendors for the dropdown
  if (vendorsStore.vendors.length === 0) {
    vendorsStore.fetchVendors()
  }
})
</script>

<style scoped>
.form-container {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 600px;
  margin: 1rem;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.form-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
}

.form {
  padding: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.material-info {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  padding: 0.75rem;
  margin-bottom: 1rem;
}

.stock-info {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.unit-price {
  display: block;
  font-size: 0.875rem;
  color: #059669;
  margin-top: 0.25rem;
}

.total-display {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 0.375rem;
  padding: 0.75rem;
  font-size: 1.25rem;
  font-weight: bold;
  color: #0369a1;
  text-align: center;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-primary {
  background: #2563eb;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #d1d5db;
}
</style> 