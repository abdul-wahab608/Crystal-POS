<template>
  <div class="purchases-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Purchases</h1>
      <button @click="handleAddClick" class="btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        New Purchase
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="purchasesStore.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading purchases...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="false" class="error-state">
      <p class="error-message">Error loading purchases</p>
      <button @click="loadPurchases()" class="btn-secondary">Try Again</button>
    </div>

    <!-- Content -->
    <div v-else class="content">
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ purchases.length }}</div>
          <div class="stat-label">Total Purchases</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">₨{{ typeof totalSpent === 'number' ? totalSpent.toFixed(2) : '0.00' }}</div>
          <div class="stat-label">Total Spent</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ thisMonthPurchases }}</div>
          <div class="stat-label">This Month</div>
        </div>
      </div>

      <!-- Search -->
      <div class="filters-section">
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Search purchases..." 
          class="search-input"
        />
      </div>

      <!-- Purchases Table -->
      <div class="table-container">
        <table class="purchases-table">
          <thead>
            <tr>
              <th>Purchase ID</th>
              <th>Vendor</th>
              <th>Invoice Number</th>
              <th>Items</th>
              <th>Total Amount</th>
              <th>Payment Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="purchase in filteredPurchases" :key="purchase.id" class="table-row">
              <td>#{{ purchase.id }}</td>
              <td>{{ purchase.vendor_name || 'N/A' }}</td>
              <td>{{ purchase.invoice_number || 'N/A' }}</td>
              <td>
                <div class="items-list">
                  <div v-if="purchase.items && purchase.items.length > 0">
                    <div v-for="item in purchase.items" :key="item.id" class="item-entry">
                      {{ item.product_name }} ({{ item.quantity }} × ₨{{ item.unit_cost }})
                    </div>
                  </div>
                  <span v-else>No items</span>
                </div>
              </td>
              <td>₨{{ (Number(purchase.total_amount) || 0).toFixed(2) }}</td>
              <td>
                <span :class="getStatusBadge(purchase.payment_status)">
                  {{ purchase.payment_status || 'UNPAID' }}
                </span>
              </td>
              <td>{{ formatDate(purchase.date || purchase.created_at) }}</td>
              <td>
                <div class="actions">
                  <button @click="viewPurchase(purchase)" class="action-btn view">View</button>
                  <button @click="deletePurchase(purchase.id)" class="action-btn delete">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredPurchases.length === 0" class="empty-state">
          <p>No purchases found.</p>
          <button @click="handleAddClick" class="btn-primary">Create Your First Purchase</button>
        </div>
      </div>
    </div>

    <!-- Add Purchase Modal -->
    <div v-if="showAddForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal large">
        <div class="modal-header">
          <h2>Create New Purchase</h2>
          <button @click="closeForm" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="savePurchase" class="modal-form">
          <div class="form-row">
            <div class="form-group">
              <label for="vendor">Vendor *</label>
              <select id="vendor" v-model="form.vendor" required class="form-input">
                <option value="">Select Vendor</option>
                <option v-for="vendor in vendors" :key="vendor.id" :value="vendor.id">
                  {{ vendor.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="invoice_number">Invoice Number *</label>
              <input 
                id="invoice_number"
                v-model="form.invoice_number" 
                type="text" 
                required
                class="form-input"
                placeholder="Invoice #"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="purchase_date">Purchase Date</label>
              <input 
                id="purchase_date"
                v-model="form.purchase_date" 
                type="date" 
                required 
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label for="payment_status">Payment Status</label>
              <select id="payment_status" v-model="form.payment_status" required class="form-input">
                <option value="PAID">Paid</option>
                <option value="PARTIAL">Partial</option>
                <option value="UNPAID">Unpaid</option>
              </select>
            </div>
          </div>

          <!-- Purchase Items Section -->
          <div class="form-group">
            <label>Purchase Items</label>
            <div class="items-section">
              <div v-for="(item, index) in form.items" :key="index" class="item-row">
                <select v-model="item.type" class="form-input item-type">
                  <option value="existing_product">Purchased Item</option>
                  <option value="existing_material">Raw Material</option>
                  <option value="new_item">New Item (Not in DB)</option>
                </select>
                
                <select 
                  v-if="item.type === 'existing_product'" 
                  v-model="item.product_id" 
                  class="form-input item-select"
                  required
                >
                  <option value="">Select Purchased Item</option>
                  <option v-for="product in purchasedProducts" :key="product.id" :value="product.id">
                    {{ product.name }}
                  </option>
                </select>
                
                <select 
                  v-if="item.type === 'existing_material'" 
                  v-model="item.product_id" 
                  class="form-input item-select"
                  required
                >
                  <option value="">Select Raw Material</option>
                  <option v-for="material in rawMaterials" :key="material.id" :value="material.id">
                    {{ material.name }}
                  </option>
                </select>
                
                <input 
                  v-if="item.type === 'new_item'" 
                  v-model="item.item_name" 
                  type="text" 
                  placeholder="Item name"
                  class="form-input item-select"
                  required
                />
                
                <input 
                  v-model.number="item.quantity" 
                  type="number" 
                  step="0.01"
                  min="0.01"
                  placeholder="Qty"
                  class="form-input item-qty"
                  required
                />
                
                <input 
                  v-model.number="item.unit_cost" 
                  type="number" 
                  step="0.01"
                  min="0"
                  placeholder="Unit Cost"
                  class="form-input item-price"
                  required
                />
                
                <div class="item-subtotal">
                  ₨{{ (item.quantity * item.unit_cost).toFixed(2) }}
                </div>
                
                <button type="button" @click="removeItem(index)" class="btn-remove-item">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <button type="button" @click="addItem" class="btn-add-item">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add Item
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
              placeholder="Additional notes about this purchase"
            ></textarea>
          </div>
          
          <!-- Total Amount Display -->
          <div class="form-group total-display">
            <label>Total Amount</label>
            <div class="total-amount">
              ₨{{ formTotal.toFixed(2) }}
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">Create Purchase</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePurchasesStore } from '../stores/purchases'
import { useRawMaterialsStore } from '../../raw_materials/stores/raw_materials'
import { useProductsStore } from '../../products/stores/products'
import { useVendorsStore } from '../../vendors/stores/vendors'

const purchasesStore = usePurchasesStore()
const rawMaterialsStore = useRawMaterialsStore()
const productsStore = useProductsStore()
const vendorsStore = useVendorsStore()

const searchTerm = ref('')
const showAddForm = ref(false)

const form = ref({
  vendor: '',
  invoice_number: '',
  payment_status: 'UNPAID',
  purchase_date: new Date().toISOString().split('T')[0],
  items: [{ type: 'existing_material', product_id: '', item_name: '', quantity: 1, unit_cost: 0 }],
  notes: ''
})

function handleAddClick() {
  showAddForm.value = true
}

// Computed properties
const purchases = computed(() => purchasesStore.purchases)
const rawMaterials = computed(() => rawMaterialsStore.materials)
const allProducts = computed(() => productsStore.products)
const purchasedProducts = computed(() => {
  return Array.isArray(allProducts.value) 
    ? allProducts.value.filter(p => p.product_type === 'PURCHASED')
    : []
})
const vendors = computed(() => vendorsStore.vendors.filter(v => v.is_active))

const filteredPurchases = computed(() => {
  if (!searchTerm.value) return purchases.value
  return purchases.value.filter(purchase => 
    (purchase.vendor_name || '').toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    (purchase.invoice_number || '').toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

const totalSpent = computed(() => {
  if (!Array.isArray(purchases.value)) {
    return 0
  }
  const total = purchases.value.reduce((total, purchase) => {
    const amount = purchase.total_amount || 0
    return total + Number(amount)
  }, 0)
  return total
})

const thisMonthPurchases = computed(() => {
  const thisMonth = new Date().getMonth()
  const thisYear = new Date().getFullYear()
  return purchases.value.filter(purchase => {
    const purchaseDate = new Date(purchase.purchase_date)
    return purchaseDate.getMonth() === thisMonth && purchaseDate.getFullYear() === thisYear
  }).length
})

// Methods
function formatDate(date: string) {
  return new Date(date).toLocaleDateString()
}

function closeForm() {
  showAddForm.value = false
  resetForm()
}

function resetForm() {
  form.value = {
    vendor: '',
    invoice_number: '',
    payment_status: 'UNPAID',
    purchase_date: new Date().toISOString().split('T')[0],
    items: [{ type: 'existing_material', product_id: '', item_name: '', quantity: 1, unit_cost: 0 }],
    notes: ''
  }
}

function addItem() {
  form.value.items.push({ type: 'existing_material', product_id: '', item_name: '', quantity: 1, unit_cost: 0 })
}

function removeItem(index: number) {
  if (form.value.items.length > 1) {
    form.value.items.splice(index, 1)
  }
}

const formTotal = computed(() => {
  return form.value.items.reduce((total, item) => {
    return total + (Number(item.quantity || 0) * Number(item.unit_cost || 0))
  }, 0)
})

async function savePurchase() {
  try {
    // Calculate total amount from items
    const totalAmount = formTotal.value
    
    // Prepare items for backend - create new products if needed
    const items = []
    
    for (const item of form.value.items) {
      let productId = null
      
      if (item.type === 'existing_product' || item.type === 'existing_material') {
        productId = item.product_id
        
        if (!productId) {
          alert('Please select a product or raw material from the dropdown')
          return
        }
      } else if (item.type === 'new_item') {
        // Create a new product on-the-fly
        if (!item.item_name || item.item_name.trim() === '') {
          alert('Please enter a name for the new item')
          return
        }
        
        try {
          // Create as a purchased product
          const newProduct = await productsStore.createProduct({
            name: item.item_name.trim(),
            unit: 'PCS',
            cop: item.unit_cost,
            quantity: 0,
            product_type: 'PURCHASED'
          })
          productId = newProduct.id
        } catch (error) {
          alert(`Failed to create new product: ${item.item_name}`)
          return
        }
      }
      
      if (productId) {
        items.push({
          product: productId,
          quantity: item.quantity,
          unit_cost: item.unit_cost,
          subtotal: item.quantity * item.unit_cost
        })
      }
    }
    
    if (items.length === 0) {
      alert('Please add at least one item to the purchase')
      return
    }
    
    // Create purchase with items
    await purchasesStore.createPurchase({
      vendor: form.value.vendor,
      total_amount: totalAmount,
      date: form.value.purchase_date,
      invoice_number: form.value.invoice_number,
      payment_status: form.value.payment_status,
      items: items
    })
    
    alert('Purchase created successfully!')
    closeForm()
    purchasesStore.fetchPurchases()
    productsStore.fetchProducts() // Refresh products list
  } catch (error: any) {
    const errorMsg = error.response?.data ? JSON.stringify(error.response.data) : error.message
    alert(`Error creating purchase: ${errorMsg}`)
  }
}

function viewPurchase(purchase: any) {
  // Implement view functionality
}

function deletePurchase(id: number) {
  if (confirm('Are you sure you want to delete this purchase?')) {
    // Implement delete functionality
  }
}

function getRawMaterialName(rawMaterialId: number) {
  const material = rawMaterials.value.find(m => m.id === rawMaterialId)
  return material?.name || 'Unknown'
}

function getRawMaterialUnit(rawMaterialId: number) {
  const material = rawMaterials.value.find(m => m.id === rawMaterialId)
  return material?.unit || ''
}

function getStatusBadge(status: string) {
  const statusMap: Record<string, string> = {
    'PAID': 'status-paid',
    'UNPAID': 'status-unpaid',
    'PARTIAL': 'status-partial'
  }
  return statusMap[status] || 'status-unpaid'
}

function loadPurchases() {
  rawMaterialsStore.fetchMaterials()
  productsStore.fetchProducts()
  vendorsStore.fetchVendors()
  purchasesStore.fetchPurchases()
}

onMounted(() => {
  loadPurchases()
})
</script>

<style scoped>
.purchases-page {
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #111827;
}

.btn-primary {
  background: #2563eb;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-primary:hover {
  background: #1d4ed8;
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

.purchases-table {
  width: 100%;
  border-collapse: collapse;
}

.purchases-table th,
.purchases-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.purchases-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.table-row:hover {
  background: #f9fafb;
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

.items-list {
  font-size: 0.875rem;
}

.item-entry {
  padding: 0.125rem 0;
  color: #374151;
}

.status-paid {
  background: #dcfce7;
  color: #16a34a;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-unpaid {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-partial {
  background: #fef3c7;
  color: #d97706;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
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
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  margin: 1rem;
}

.modal.large {
  max-width: 1000px;
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

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.items-section {
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 1rem;
  background: #f9fafb;
}

.item-row {
  display: grid;
  grid-template-columns: 140px 2fr 100px 120px 100px auto;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  align-items: center;
  background: white;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
}

.item-type {
  font-size: 0.8125rem;
}

.item-select {
  min-width: 180px;
}

.item-qty {
  width: 100px;
}

.item-price {
  width: 120px;
}

.item-subtotal {
  font-weight: 600;
  color: #059669;
  font-size: 0.9375rem;
  text-align: right;
  min-width: 100px;
}

.btn-remove-item {
  background: #fee2e2;
  color: #dc2626;
  border: none;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-remove-item:hover {
  background: #fecaca;
}

.btn-add-item {
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

.btn-add-item:hover {
  background: #059669;
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