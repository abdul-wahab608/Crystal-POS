<template>
  <div class="form-container">
    <div class="form-header">
      <h2>Record Material Usage</h2>
      <button class="close-btn" @click="$emit('cancel')">×</button>
    </div>
    
    <form @submit.prevent="handleSubmit" class="form">
      <div class="form-group">
        <label>Material</label>
        <div class="material-info">
          <strong>{{ material.name }}</strong>
          <span class="stock-info">Available: {{ material.available_stock }} {{ material.unit }}</span>
        </div>
      </div>
      
      <div class="form-group">
        <label for="quantity_used">Quantity Used *</label>
        <input 
          id="quantity_used"
          v-model.number="form.quantity_used" 
          type="number" 
          step="0.01"
          min="0.01"
          :max="material.available_stock"
          required 
          class="form-input"
          :class="{ 'error': quantityError }"
          placeholder="Enter quantity used"
        />
        <div v-if="quantityError" class="error-message">
          ⚠️ Insufficient stock! Available: {{ material.available_stock }} {{ material.unit }}
        </div>
      </div>
      
      <div class="form-group">
        <label for="reference">Reference</label>
        <input 
          id="reference"
          v-model="form.reference" 
          type="text" 
          class="form-input"
          placeholder="e.g., Production Batch #123"
        />
      </div>
      
      <div class="form-group">
        <label for="notes">Notes</label>
        <textarea 
          id="notes"
          v-model="form.notes" 
          class="form-input"
          rows="3"
          placeholder="Additional notes about this usage"
        ></textarea>
      </div>
      
      <div class="form-actions">
        <button type="button" @click="$emit('cancel')" class="btn-secondary">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="loading || quantityError">
          {{ loading ? 'Recording...' : 'Record Usage' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRawMaterialsStore } from '../stores/raw_materials'
import type { RawMaterial, CreateRawMaterialUsage } from '../types'

const props = defineProps<{
  material: RawMaterial
}>()

const emit = defineEmits<{
  success: []
  cancel: []
}>()

const store = useRawMaterialsStore()
const loading = ref(false)

const form = ref<CreateRawMaterialUsage>({
  raw_material: props.material.id,
  quantity_used: 0,
  reference: '',
  notes: ''
})

const quantityError = computed(() => {
  return form.value.quantity_used > props.material.available_stock
})

async function handleSubmit() {
  if (quantityError.value) return
  
  loading.value = true
  try {
    await store.createUsage(form.value)
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
  max-width: 500px;
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
}

.stock-info {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
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

.form-input.error {
  border-color: #dc2626;
  background-color: #fef2f2;
}

.error-message {
  color: #dc2626;
  font-size: 0.75rem;
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