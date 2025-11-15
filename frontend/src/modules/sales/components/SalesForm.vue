<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <form @submit.prevent="onSubmit" class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <h2 class="modal-title">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            {{ sale?.id ? 'Edit Sale' : 'New Sale' }}
          </h2>
          <button type="button" @click="$emit('close')" class="close-button">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Body -->
        <div class="modal-body">
          <!-- Sale Information -->
          <div class="section">
            <h3 class="section-title">Sale Information</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="customer" class="form-label">
                  Customer <span class="required">*</span>
                </label>
                <select 
                  v-model="form.customer" 
                  id="customer" 
                  class="form-input" 
                  required
                >
                  <option value="">Select Customer</option>
                  <option 
                    v-for="customer in customers" 
                    :key="customer.id" 
                    :value="customer.id"
                  >
                    {{ customer.name }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="date" class="form-label">
                  Date <span class="required">*</span>
                </label>
                <input 
                  v-model="form.date" 
                  id="date" 
                  type="date" 
                  class="form-input" 
                  required 
                />
              </div>
              
              <div class="form-group">
                <label for="payment_status" class="form-label">
                  Payment Status <span class="required">*</span>
                </label>
                <select 
                  v-model="form.payment_status" 
                  id="payment_status" 
                  class="form-input" 
                  required
                >
                  <option value="UNPAID">Unpaid</option>
                  <option value="PARTIAL">Partial</option>
                  <option value="PAID">Paid</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Products Section -->
          <div class="section">
            <h3 class="section-title">Products</h3>
            
            <!-- Add Product -->
            <div class="add-product-section">
              <div class="add-product-grid">
                <div class="form-group">
                  <label class="form-label">Product</label>
                  <select v-model="newItem.product_id" class="form-input">
                    <option value="">Select Product</option>
                    <option 
                      v-for="product in products" 
                      :key="product.id" 
                      :value="product.id"
                    >
                      {{ product.name }} ({{ product.unit }}) - Stock: {{ product.available_stock || product.quantity }}
                    </option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label class="form-label">Quantity</label>
                  <input 
                    v-model.number="newItem.quantity" 
                    type="number" 
                    step="0.01"
                    min="0.01"
                    class="form-input"
                    placeholder="0"
                  />
                </div>
                
                <div class="form-group">
                  <label class="form-label">Unit Price</label>
                  <input 
                    v-model.number="newItem.unit_price" 
                    type="number" 
                    step="0.01"
                    min="0"
                    class="form-input"
                    placeholder="0.00"
                  />
                </div>
                
                <div class="form-group">
                  <label class="form-label">&nbsp;</label>
                  <button 
                    type="button" 
                    @click="addProduct" 
                    class="btn-add"
                    :disabled="!newItem.product_id || !newItem.quantity || !newItem.unit_price"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Add
                  </button>
                </div>
              </div>
            </div>

            <!-- Products List -->
            <div v-if="saleItems.length > 0" class="products-list">
              <div 
                v-for="(item, index) in saleItems" 
                :key="index"
                class="product-item"
              >
                <div class="product-info">
                  <div class="product-name">{{ getProductName(item.product_id) }}</div>
                  <div class="product-details">
                    {{ item.quantity }} {{ getProductUnit(item.product_id) }} × ₨{{ item.unit_price.toFixed(2) }} = ₨{{ (item.quantity * item.unit_price).toFixed(2) }}
                  </div>
                </div>
                <button 
                  type="button"
                  @click="removeProduct(index)" 
                  class="btn-remove"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div v-else class="empty-products">
              <p>No products added. Add products above to create a sale.</p>
            </div>

            <!-- Total -->
            <div class="total-section">
              <div class="total-row">
                <span class="total-label">Total Amount:</span>
                <span class="total-value">₨{{ totalAmount.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer -->
        <div class="modal-footer">
          <button type="button" @click="$emit('close')" class="btn-cancel">
            Cancel
          </button>
          <button type="submit" class="btn-save" :disabled="saleItems.length === 0">
            {{ sale?.id ? 'Update Sale' : 'Create Sale' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useProductsStore } from '@/modules/products/stores/products'
import type { Sale, CreateSaleRequest } from '../types'

interface Props {
  sale?: Sale | null
  customers: any[]
}

const props = defineProps<Props>()
const emit = defineEmits(['save', 'close'])

const productsStore = useProductsStore()
const products = computed(() => productsStore.products || [])

const form = ref<CreateSaleRequest>({
  customer: 0,
  total_amount: 0,
  total: 0,
  date: new Date().toISOString().split('T')[0],
  payment_status: 'UNPAID',
  items: []
})

const saleItems = ref<Array<{ product_id: number; quantity: number; unit_price: number }>>([])

const newItem = ref({
  product_id: 0,
  quantity: 0,
  unit_price: 0
})

const totalAmount = computed(() => {
  return saleItems.value.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0)
})

watch(() => props.sale, (val) => {
  if (val) {
    form.value = {
      customer: val.customer,
      total_amount: val.total_amount,
      total: val.total,
      date: val.date,
      payment_status: val.payment_status,
      items: []
    }
    saleItems.value = val.sale_items?.map(item => ({
      product_id: item.product,
      quantity: item.quantity,
      unit_price: item.unit_price || 0
    })) || []
  } else {
    form.value = {
      customer: 0,
      total_amount: 0,
      total: 0,
      date: new Date().toISOString().split('T')[0],
      payment_status: 'UNPAID',
      items: []
    }
    saleItems.value = []
  }
}, { immediate: true })

function getProductName(productId: number): string {
  const product = products.value.find(p => p.id === productId)
  return product ? product.name : 'Unknown Product'
}

function getProductUnit(productId: number): string {
  const product = products.value.find(p => p.id === productId)
  return product ? product.unit : ''
}

function addProduct() {
  if (!newItem.value.product_id || !newItem.value.quantity || !newItem.value.unit_price) {
    return
  }
  
  saleItems.value.push({
    product_id: newItem.value.product_id,
    quantity: newItem.value.quantity,
    unit_price: newItem.value.unit_price
  })
  
  // Reset form
  newItem.value = {
    product_id: 0,
    quantity: 0,
    unit_price: 0
  }
}

function removeProduct(index: number) {
  saleItems.value.splice(index, 1)
}

function onSubmit() {
  form.value.total_amount = totalAmount.value
  form.value.total = totalAmount.value
  form.value.items = saleItems.value
  emit('save', { ...form.value })
}

onMounted(() => {
  if (productsStore.products.length === 0) {
    productsStore.fetchProducts()
  }
})
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
}

.modal-container {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
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
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
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
}

.required {
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9375rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.add-product-section {
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.add-product-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 1rem;
  align-items: end;
}

.btn-add {
  padding: 0.75rem 1.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-add:hover:not(:disabled) {
  background: #059669;
}

.btn-add:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.products-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.product-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.product-info {
  flex: 1;
}

.product-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.product-details {
  font-size: 0.875rem;
  color: #6b7280;
}

.btn-remove {
  background: #fee2e2;
  color: #dc2626;
  border: none;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-remove:hover {
  background: #fecaca;
}

.empty-products {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.total-section {
  border-top: 2px solid #e5e7eb;
  padding-top: 1rem;
  margin-top: 1rem;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-label {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.total-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #10b981;
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
}

.btn-cancel:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.btn-save {
  padding: 0.75rem 2rem;
  border: none;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.btn-save:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  box-shadow: none;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .add-product-grid {
    grid-template-columns: 1fr;
  }
}
</style> 