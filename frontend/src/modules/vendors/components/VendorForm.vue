<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <form @submit.prevent="onSubmit" class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <h2 class="modal-title">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            {{ vendor?.id ? 'Edit Vendor' : 'Add New Vendor' }}
          </h2>
          <button type="button" @click="$emit('close')" class="close-button">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Body -->
        <div class="modal-body">
          <!-- Vendor Information Section -->
          <div class="section">
            <h3 class="section-title">Vendor Information</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="name" class="form-label">
                  Vendor Name <span class="required">*</span>
                </label>
                <input 
                  v-model="form.name" 
                  id="name" 
                  class="form-input" 
                  placeholder="Enter vendor name"
                  required 
                />
              </div>
              
              <div class="form-group">
                <label for="email" class="form-label">
                  Email <span class="required">*</span>
                </label>
                <input 
                  v-model="form.email" 
                  id="email" 
                  type="email" 
                  class="form-input"
                  placeholder="vendor@example.com"
                  required 
                />
              </div>
              
              <div class="form-group">
                <label for="phone" class="form-label">
                  Phone <span class="required">*</span>
                </label>
                <input 
                  v-model="form.phone" 
                  id="phone" 
                  class="form-input"
                  placeholder="+1 (555) 123-4567"
                  required 
                />
              </div>
              
              <div class="form-group">
                <label for="contact_person" class="form-label">Contact Person</label>
                <input 
                  v-model="form.contact_person" 
                  id="contact_person" 
                  class="form-input"
                  placeholder="John Doe"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label for="address" class="form-label">Address</label>
              <textarea 
                v-model="form.address" 
                id="address" 
                class="form-input" 
                rows="2"
                placeholder="Enter complete address..."
              ></textarea>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="form.is_active" type="checkbox" class="checkbox-input" />
                <span class="checkbox-text">Active Vendor</span>
                <span class="checkbox-hint">Vendor can be used in transactions</span>
              </label>
            </div>
          </div>
        </div>
        
        <!-- Footer -->
        <div class="modal-footer">
          <button type="button" @click="$emit('close')" class="btn-cancel">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Cancel
          </button>
          <button type="submit" class="btn-save">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            {{ vendor?.id ? 'Update Vendor' : 'Create Vendor' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'
import type { Vendor, CreateVendorRequest } from '../types'

interface Props {
  vendor?: Vendor | null
}

const props = defineProps<Props>()
const emit = defineEmits(['save', 'close'])

const form = ref<CreateVendorRequest>({
  name: '',
  email: '',
  phone: '',
  address: '',
  contact_person: '',
  is_active: true
})

watch(() => props.vendor, (val) => {
  if (val) {
    form.value = {
      name: val.name,
      email: val.email,
      phone: val.phone,
      address: val.address,
      contact_person: val.contact_person,
      is_active: val.is_active
    }
  } else {
    form.value = {
      name: '',
      email: '',
      phone: '',
      address: '',
      contact_person: '',
      is_active: true
    }
  }
}, { immediate: true })

function onSubmit() {
  emit('save', { ...form.value })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-container {
  width: 100%;
  max-width: 1000px;
  max-height: 90vh;
  display: flex;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 2px solid #f0f0f0;
  background: linear-gradient(to bottom, #ffffff, #fafafa);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
  border-radius: 8px;
}

.close-button:hover {
  background: #f3f4f6;
  color: #1f2937;
  transform: scale(1.1);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background: #fafafa;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.required {
  color: #ef4444;
  font-weight: bold;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9375rem;
  transition: all 0.2s;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
  background: #f9fafb;
}

.checkbox-label:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.checkbox-input {
  width: 1.25rem;
  height: 1.25rem;
  margin-top: 0.125rem;
  cursor: pointer;
  accent-color: #3b82f6;
}

.checkbox-text {
  font-weight: 600;
  color: #1f2937;
}

.checkbox-hint {
  font-size: 0.8125rem;
  color: #6b7280;
  display: block;
  margin-top: 0.25rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-top: 2px solid #f0f0f0;
  background: white;
}

.btn-cancel {
  padding: 0.75rem 1.5rem;
  border: 2px solid #e5e7eb;
  background: white;
  color: #6b7280;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}

.btn-cancel:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #374151;
  transform: translateY(-1px);
}

.btn-save {
  padding: 0.75rem 2rem;
  border: none;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-save:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

.btn-save:active {
  transform: translateY(0);
}

/* Responsive */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-body {
    padding: 1.5rem;
  }
  
  .modal-header,
  .modal-footer {
    padding: 1rem 1.5rem;
  }
}
</style> 