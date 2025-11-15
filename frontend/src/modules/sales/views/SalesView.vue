<template>
  <div class="sales-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Sales Management</h1>
      <button @click="showAddForm = true" class="btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        New Sale
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading sales...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="error-state">
      <p class="error-message">{{ store.error }}</p>
      <button @click="store.fetchSales()" class="btn-secondary">Try Again</button>
    </div>

    <!-- Content -->
    <div v-else class="content">
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ sales.length }}</div>
          <div class="stat-label">Total Sales</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">₨{{ totalSpent.toFixed(2) }}</div>
          <div class="stat-label">Total Revenue</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ thisMonthSales }}</div>
          <div class="stat-label">This Month's Sales</div>
        </div>
      </div>

      <!-- Search -->
      <div class="filters-section">
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Search sales..." 
          class="search-input"
        />
      </div>

      <!-- Sales Table -->
      <div class="table-container">
        <table class="sales-table">
          <thead>
            <tr>
              <th>Receipt #</th>
              <th>Customer</th>
              <th>Items</th>
              <th>Total Amount</th>
              <th>Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sale in filteredSales" :key="sale.id" class="table-row">
              <td>{{ sale.id }}</td>
              <td>{{ sale.customer_name || 'Unknown Customer' }}</td>
              <td>{{ sale.sale_items.length }} items</td>
              <td>₨{{ Number(sale.total_amount || 0).toFixed(2) }}</td>
              <td>{{ sale.date ? formatDate(sale.date) : 'N/A' }}</td>
              <td>
                <label class="status-checkbox-label">
                  <input 
                    type="checkbox" 
                    :checked="sale.payment_status === 'PAID'"
                    @change="togglePaymentStatus(sale)"
                    class="payment-checkbox"
                  />
                  <span :class="getStatusClass(sale.payment_status)">
                    {{ sale.payment_status || 'UNPAID' }}
                  </span>
                </label>
              </td>
              <td>
                <div class="actions">
                  <button @click="viewSale(sale)" class="action-btn view">View</button>
                  <button @click="deleteSale(sale.id)" class="action-btn delete">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredSales.length === 0" class="empty-state">
          <p>No sales found.</p>
          <button @click="showAddForm = true" class="btn-primary">Create Your First Sale</button>
        </div>
      </div>
    </div>

    <!-- Add Sale Modal -->
    <div v-if="showAddForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal large">
        <div class="modal-header">
          <h2>Create New Sale</h2>
          <button @click="closeForm" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveSale" class="modal-form">
          <div class="form-row">
            <div class="form-group">
              <label for="customer">Customer</label>
              <select id="customer" v-model="form.customer_id" required class="form-input">
                <option value="">Select Customer</option>
                <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                  {{ customer.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="sale_date">Sale Date</label>
              <input 
                id="sale_date"
                v-model="form.sale_date" 
                type="date" 
                required 
                class="form-input"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>Products</label>
            <div class="products-section">
              <div v-for="(item, index) in form.items" :key="index" class="product-item">
                <select v-model="item.product_id" required class="form-input product-select">
                  <option value="">Select Product</option>
                  <option 
                    v-for="product in products.filter(p => p.available_stock > 0)" 
                    :key="product.id" 
                    :value="product.id"
                    :class="{ 'low-stock': product.available_stock <= 10 }"
                  >
                    {{ product.name }} (Stock: {{ product.available_stock }})
                  </option>
                  <option v-if="products.filter(p => p.available_stock > 0).length === 0" value="" disabled>
                    No products with available stock
                  </option>
                </select>
                <input 
                  v-model.number="item.quantity" 
                  type="number" 
                  step="0.01"
                  min="0.01" 
                  required 
                  placeholder="Quantity"
                  class="form-input quantity-input"
                  :class="{ 'error': isInsufficientStock(item) }"
                />
                <input 
                  v-model.number="item.unit_price" 
                  type="number" 
                  step="0.01"
                  min="0" 
                  required 
                  placeholder="Price per unit"
                  class="form-input price-input"
                />
                <div class="item-total">
                  ₨{{ (item.quantity * (item.unit_price || 0)).toFixed(2) }}
                </div>
                <button type="button" @click="removeProduct(index)" class="btn-remove">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div v-if="isInsufficientStock(form.items[0])" class="stock-error">
                ⚠️ Insufficient stock! Available: {{ getAvailableStock(form.items[0].product_id) }}
              </div>
              <button type="button" @click="addProduct" class="btn-add-product">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add Product
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label for="notes">Notes</label>
            <textarea 
              id="notes"
              v-model="form.notes" 
              class="form-input"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.is_paid" class="payment-checkbox" />
              <span>Payment Received</span>
            </label>
          </div>
          
          <!-- Total Amount Display -->
          <div class="form-group total-display">
            <label>Total Amount</label>
            <div class="total-amount">
              ₨{{ formTotal.toFixed(2) }}
            </div>
          </div>
          
          <!-- Stock Issues Summary -->
          <div v-if="stockIssues.length > 0" class="stock-issues-summary">
            <h4>⚠️ Stock Issues Found:</h4>
            <ul>
              <li v-for="issue in stockIssues" :key="issue.productName">
                <strong>{{ issue.productName }}</strong>: Requested {{ issue.requested }}, Available {{ issue.available }}
              </li>
            </ul>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn-secondary">Cancel</button>
            <button 
              type="submit" 
              class="btn-primary"
              :disabled="hasInsufficientStock()"
              :title="hasInsufficientStock() ? 'Cannot save: Insufficient stock for some items' : 'Save Sale'"
            >
              {{ hasInsufficientStock() ? '❌ Insufficient Stock' : 'Save Sale' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSalesStore } from '../stores/sales'
import { useCustomersStore } from '../../customers/stores/customers'
import { useProductsStore } from '../../products/stores/products'
import { useAuthStore } from '../../../shared/stores/auth'
import type { Sale, CreateSaleRequest } from '../types'

const store = useSalesStore()
const customersStore = useCustomersStore()
const productsStore = useProductsStore()
const authStore = useAuthStore()

const searchTerm = ref('')
const showAddForm = ref(false)
const selectedSale = ref<Sale | null>(null)
const loading = ref(false)

const form = ref({
  customer_id: 0,
  sale_date: new Date().toISOString().split('T')[0],
  items: [{ product_id: 0, quantity: 1, unit_price: 0 }],
  notes: '',
  is_paid: false
})

onMounted(() => {
  store.fetchSales()
  customersStore.fetchCustomers()
  productsStore.fetchProducts()
})

const sales = computed(() => store.sales || [])
const customers = computed(() => customersStore.customers || [])
const products = computed(() => productsStore.products || [])

const filteredSales = computed(() => {
  if (!searchTerm.value) return sales.value
  return sales.value.filter(sale => 
    sale.customer_name?.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    sale.id.toString().includes(searchTerm.value)
  )
})

const totalSpent = computed(() => 
  sales.value.reduce((sum, sale) => sum + Number(sale.total_amount || 0), 0)
)

const thisMonthSales = computed(() => {
  const thisMonth = new Date().getMonth()
  const thisYear = new Date().getFullYear()
  return sales.value.filter(s => {
    const created = new Date(s.date)
    return created.getMonth() === thisMonth && created.getFullYear() === thisYear
  }).length
})

const stockIssues = computed(() => {
  return form.value.items
    .filter(item => isInsufficientStock(item))
    .map(item => {
      const product = products.value.find(p => p.id === item.product_id)
      return {
        productName: product?.name || 'Unknown Product',
        requested: item.quantity,
        available: getAvailableStock(item.product_id)
      }
    })
})

const formTotal = computed(() => {
  return form.value.items.reduce((total, item) => {
    return total + (Number(item.unit_price || 0) * Number(item.quantity || 0))
  }, 0)
})

function addProduct() {
  form.value.items.push({ product_id: 0, quantity: 1, unit_price: 0 })
}

function removeProduct(index: number) {
  if (form.value.items.length > 1) {
    form.value.items.splice(index, 1)
  }
}

function viewSale(sale: Sale) {
  // Create a detailed sale view
  let details = `Receipt: ${sale.id}\n`
  details += `Customer: ${sale.customer_name}\n`
  details += `Date: ${sale.date ? formatDate(sale.date) : 'N/A'}\n`
        details += `Total: ₨${Number(sale.total_amount || 0).toFixed(2)}\n`
  details += `Status: ${sale.payment_status || 'UNKNOWN'}\n\n`
  
  if (sale.sale_items && sale.sale_items.length > 0) {
    details += 'Items:\n'
    sale.sale_items.forEach(item => {
      details += `• ${item.product_name} x ${item.quantity} @ ₨${item.total_price} = ₨${item.total_price}\n`
    })
  } else {
    details += 'Items: No items found'
  }
  
  alert(details)
}

function deleteSale(id: number) {
  if (confirm('Are you sure you want to delete this sale?')) {
    store.deleteSale(id)
  }
}

async function saveSale() {
  try {
    // Check for insufficient stock before proceeding
    if (hasInsufficientStock()) {
      alert('❌ Cannot create sale: Some items have insufficient stock!')
      return
    }
    
    // Transform form data to match API expectations
    const saleData = {
      customer: form.value.customer_id,
      total_amount: formTotal.value,
      date: form.value.sale_date,
      items: form.value.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.unit_price
      })),
      payment_status: form.value.is_paid ? 'PAID' : 'UNPAID'
    }
    
    await store.createSale(saleData)
    
    // Refresh products data to update available stock
    await productsStore.fetchProducts()
    
    closeForm()
    
    // Show success message
    alert('✅ Sale created successfully! Stock has been updated.')
  } catch (error: any) {
    // Show user-friendly error message
    if (error && error.response && error.response.data && error.response.data.message) {
      alert(`❌ Sale creation failed: ${error.response.data.message}`)
    } else {
      alert('❌ Sale creation failed. Please try again.')
    }
  }
}

function calculateTotal() {
  return form.value.items.reduce((total, item) => {
    const product = products.value.find(p => p.id === item.product_id)
    if (product) {
      return total + (Number(product.cop) * Number(item.quantity))
    }
    return total
  }, 0)
}

function closeForm() {
  showAddForm.value = false
  form.value = {
    customer_id: 0,
    sale_date: new Date().toISOString().split('T')[0],
    items: [{ product_id: 0, quantity: 1, unit_price: 0 }],
    notes: '',
    is_paid: false
  }
}

async function togglePaymentStatus(sale: Sale) {
  try {
    const newStatus = sale.payment_status === 'PAID' ? 'UNPAID' : 'PAID'
    await store.updateSale(sale.id, { payment_status: newStatus })
  } catch (error) {
    alert('Failed to update payment status')
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString()
}

function getStatusClass(status: string) {
  if (!status) return 'status-default'
  
  switch (status.toUpperCase()) {
    case 'PAID':
      return 'status-completed'
    case 'PARTIAL':
      return 'status-pending'
    case 'UNPAID':
      return 'status-cancelled'
    default:
      return 'status-default'
  }
}

function isInsufficientStock(item: any) {
  if (!item.product_id || !item.quantity) return false
  const product = products.value.find(p => p.id === item.product_id)
  return product && item.quantity > Number(product.available_stock || 0)
}

function getAvailableStock(productId: number) {
  const product = products.value.find(p => p.id === productId)
  return product ? Number(product.available_stock || 0) : 0
}

function hasInsufficientStock() {
  return form.value.items.some(item => isInsufficientStock(item))
}
</script>

<style scoped>
.sales-page {
  padding: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.875rem;
  font-weight: bold;
  color: #111827;
}

.loading-state, .error-state {
  text-align: center;
  padding: 3rem;
}

.spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #dc2626;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #2563eb;
}

.stat-label {
  color: #6b7280;
  margin-top: 0.5rem;
}

.filters-section {
  margin-bottom: 1.5rem;
}

.search-input {
  width: 100%;
  max-width: 400px;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.table-container {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
}

.sales-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.sales-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.table-row:hover {
  background: #f9fafb;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-cancelled {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-default {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
}

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.delete {
  background: #fee2e2;
  color: #dc2626;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

/* Stock validation styles */
.quantity.error {
  border-color: #dc2626;
  background-color: #fef2f2;
}

.stock-error {
  color: #dc2626;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  font-weight: 500;
}

.product-item {
  position: relative;
  margin-bottom: 1rem;
}

.product-item .form-input {
  margin-right: 0.5rem;
}

.product-item .quantity {
  width: 80px;
}

.stock-issues-summary {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.stock-issues-summary h4 {
  color: #dc2626;
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.stock-issues-summary ul {
  margin: 0;
  padding-left: 1.5rem;
}

.stock-issues-summary li {
  color: #dc2626;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.total-display {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.total-amount {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2563eb;
  text-align: center;
  margin-top: 0.5rem;
}

.low-stock {
  color: #dc2626;
  font-weight: 600;
}

option.low-stock {
  background-color: #fef2f2;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 500px;
  margin: 1rem;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal.large {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
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

.modal-form {
  padding: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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

.products-section {
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 1rem;
  background: #f9fafb;
}

.product-item {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto auto;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  align-items: center;
  background: white;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
}

.product-select {
  min-width: 200px;
}

.quantity-input {
  width: 100px;
}

.price-input {
  width: 120px;
}

.item-total {
  font-weight: 600;
  color: #059669;
  font-size: 0.9375rem;
  text-align: right;
  min-width: 100px;
}

.btn-remove {
  background: #fee2e2;
  color: #dc2626;
  border: none;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-remove:hover {
  background: #fecaca;
}

.btn-add-product {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  margin-top: 0.5rem;
  transition: all 0.2s;
}

.btn-add-product:hover {
  background: #059669;
}

.stock-error {
  grid-column: 1 / -1;
  background: #fee2e2;
  color: #dc2626;
  padding: 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  margin-top: -0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9375rem;
}

.payment-checkbox {
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
}

.status-checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
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
  display: inline-flex;
  align-items: center;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-primary:disabled:hover {
  background-color: #9ca3af;
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