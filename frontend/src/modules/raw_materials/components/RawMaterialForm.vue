<template>
  <div class="form-container">
    <div class="form-header">
      <h2>{{ isEditing ? 'Edit Raw Material' : 'Add Raw Material' }}</h2>
      <button class="close-btn" @click="$emit('cancel')">×</button>
    </div>
    
    <form @submit.prevent="handleSubmit" class="form">
      <div class="form-row">
        <div class="form-group">
          <label for="name">Name *</label>
          <input 
            id="name"
            v-model="form.name" 
            type="text" 
            required 
            class="form-input"
            placeholder="Enter material name"
          />
        </div>
        
        <div class="form-group">
          <label for="unit">Unit *</label>
          <select id="unit" v-model="form.unit" required class="form-input">
            <option value="">Select Unit</option>
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
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="quantity">Initial Quantity</label>
          <input 
            id="quantity"
            v-model.number="form.quantity" 
            type="number" 
            step="0.01"
            min="0"
            class="form-input"
            placeholder="0"
          />
          <small class="help-text">Optional: Set initial stock quantity</small>
        </div>
        
        <div class="form-group">
          <label for="reorder_level">Reorder Level *</label>
          <input 
            id="reorder_level"
            v-model.number="form.reorder_level" 
            type="number" 
            step="0.01"
            min="0"
            required 
            class="form-input"
            placeholder="Minimum stock level"
          />
          <small class="help-text">Alert when stock falls below this level</small>
        </div>
      </div>
      
      <div class="form-group">
        <label for="preferred_vendor">Preferred Vendor (Optional)</label>
        <select 
          id="preferred_vendor"
          v-model="selectedVendor" 
          class="form-input"
        >
          <option value="">No preferred vendor</option>
          <option 
            v-for="vendor in vendorsStore.vendors.filter(v => v.is_active)" 
            :key="vendor.id" 
            :value="vendor.name"
          >
            {{ vendor.name }}
          </option>
        </select>
        <small class="help-text">Select a preferred vendor for this material</small>
      </div>
      
      <div class="form-actions">
        <button type="button" @click="$emit('cancel')" class="btn-secondary">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Saving...' : (isEditing ? 'Update' : 'Create') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRawMaterialsStore } from '../stores/raw_materials'
import { useVendorsStore } from '@/modules/vendors/stores/vendors'
import type { RawMaterial, CreateRawMaterial } from '../types'

const props = defineProps<{ material?: RawMaterial }>()

const emit = defineEmits<{
  success: []
  cancel: []
}>()

const store = useRawMaterialsStore()
const vendorsStore = useVendorsStore()
const loading = ref(false)
const selectedVendor = ref('')

const isEditing = computed(() => !!props.material)

const form = ref<CreateRawMaterial>({
  name: '',
  unit: '',
  quantity: 0,
  reorder_level: 0
})

onMounted(() => {
  // Fetch vendors for dropdown
  if (vendorsStore.vendors.length === 0) {
    vendorsStore.fetchVendors()
  }
  
  if (props.material) {
    form.value = {
      name: props.material.name,
      unit: props.material.unit,
      quantity: props.material.quantity,
      reorder_level: props.material.reorder_level
    }
  }
})

async function handleSubmit() {
  loading.value = true
  try {
    if (isEditing.value && props.material) {
      await store.updateMaterial(props.material.id, form.value)
    } else {
      await store.createMaterial(form.value)
    }
    emit('success')
  } catch (error) {
    // Handle error silently
  } finally {
    loading.value = false
  }
}
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

.help-text {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
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