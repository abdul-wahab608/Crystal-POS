<template>
  <div class="products-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Products Management</h1>
      <button @click="showAddForm = true" class="btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Add Product
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading products...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="error-state">
      <p class="error-message">{{ store.error }}</p>
      <button @click="store.fetchProducts()" class="btn-secondary">Try Again</button>
    </div>

    <!-- Content -->
    <div v-else class="content">
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ products.length }}</div>
          <div class="stat-label">Total Products</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ lowStockCount }}</div>
          <div class="stat-label">Low Stock Items</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">₨{{ totalValue.toFixed(2) }}</div>
          <div class="stat-label">Total Value</div>
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="filters-section">
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Search products..." 
          class="search-input"
        />
      </div>

      <!-- Products Table -->
      <div class="table-container">
        <table class="products-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Unit</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Value</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredProducts" :key="product.id" class="table-row">
              <td>{{ product.name }}</td>
              <td>
                <span class="unit-badge">{{ product.unit }}</span>
              </td>
              <td>₨{{ Number(product.cop).toFixed(2) }}</td>
              <td>
                <span :class="Number(product.quantity) < 10 ? 'low-stock' : ''">
                  {{ product.quantity }}
                </span>
              </td>
              <td>₨{{ (Number(product.quantity) * Number(product.cop)).toFixed(2) }}</td>
              <td>
                <div class="actions">
                  <button @click="editProduct(product)" class="action-btn edit">Edit</button>
                  <button @click="deleteProduct(product.id)" class="action-btn delete">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredProducts.length === 0" class="empty-state">
          <p>No products found.</p>
          <button @click="showAddForm = true" class="btn-primary">Add Your First Product</button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Product Modal -->
    <div v-if="showAddForm || showEditForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ showEditForm ? 'Edit Product' : 'Add New Product' }}</h2>
          <button @click="closeForm" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveProduct" class="modal-form">
          <div class="form-group">
            <label for="name">Product Name</label>
            <input 
              id="name"
              v-model="form.name" 
              type="text" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="unit">Unit</label>
            <select id="unit" v-model="form.unit" required class="form-input">
              <option value="">Select Unit</option>
              <option value="BAG">Bags</option>
              <option value="KILO">Kilos</option>
              <option value="PCS">Pieces</option>
              <option value="KG">Kilograms</option>
              <option value="L">Liters</option>
              <option value="M">Meters</option>
              <option value="BOX">Boxes</option>
              <option value="PACK">Packs</option>
              <option value="UNIT">Units</option>
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
          
          <div v-if="showEditForm" class="form-group">
            <label for="price">Unit Price</label>
            <input 
              id="price"
              v-model.number="form.cop"
              type="number" 
              step="0.01" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="quantity">Stock Quantity</label>
            <input 
              id="quantity"
              v-model.number="form.quantity" 
              type="number" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">
              {{ showEditForm ? 'Update' : 'Create' }} Product
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProductsStore } from '../stores/products'

const store = useProductsStore()
const searchTerm = ref('')
const showAddForm = ref(false)
const showEditForm = ref(false)
const editingProduct = ref<any>(null)

const form = ref({
  name: '',
  unit: 'PCS' as 'M' | 'BAG' | 'KILO' | 'PCS' | 'KG' | 'L' | 'BOX' | 'PACK' | 'UNIT' | 'GRAM' | 'TON' | 'GALLON' | 'FOOT' | 'YARD' | 'CM' | 'MM' | 'INCH' | 'POUND' | 'OUNCE' | 'CUP' | 'TABLESPOON' | 'TEASPOON',
  cop: 0,
  quantity: 0
})

onMounted(() => {
  store.fetchProducts()
})

const products = computed(() => {
  const productsArray = store.products || []
  // Filter to show only MANUFACTURED products in the Products tab
  return Array.isArray(productsArray) 
    ? productsArray.filter(p => !p.product_type || p.product_type === 'MANUFACTURED')
    : []
})

const filteredProducts = computed(() => {
  const productsArray = products.value
  if (!Array.isArray(productsArray)) return []
  if (!searchTerm.value) return productsArray
  return productsArray.filter(p =>
    p.name.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

const lowStockCount = computed(() => {
  const productsArray = products.value
  if (!Array.isArray(productsArray)) return 0
  return productsArray.filter(p => Number(p.quantity) < 10).length
})

const totalValue = computed(() => {
  const productsArray = products.value
  if (!Array.isArray(productsArray)) return 0
  return productsArray.reduce((sum, p) => sum + (Number(p.quantity) * Number(p.cop)), 0)
})

function editProduct(product: any) {
  editingProduct.value = product
  form.value = {
    name: product.name,
    unit: product.unit as typeof form.value.unit,
    cop: product.cop,
    quantity: product.quantity
  }
  showEditForm.value = true
}

function deleteProduct(id: number) {
  if (confirm('Are you sure you want to delete this product?')) {
    store.deleteProduct(id)
  }
}

async function saveProduct() {
  try {
    if (showEditForm.value && editingProduct.value) {
      await store.updateProduct(editingProduct.value.id, form.value)
    } else {
      // Check if product with same name and unit already exists
      const existingProduct = products.value.find(
        p => p.name.toLowerCase() === form.value.name.toLowerCase() && p.unit === form.value.unit
      )
      
      if (existingProduct) {
        // Add quantity to existing product
        const newQuantity = Number(existingProduct.quantity) + Number(form.value.quantity)
        await store.updateProduct(existingProduct.id, {
          ...existingProduct,
          quantity: newQuantity
        })
      } else {
        // Create new product with default price of 0
        await store.createProduct({
          ...form.value,
          cop: 0
        })
      }
    }
    showAddForm.value = false
    showEditForm.value = false
    editingProduct.value = null
    form.value = { name: '', unit: 'PCS' as 'M' | 'BAG' | 'KILO' | 'PCS' | 'KG' | 'L' | 'BOX' | 'PACK' | 'UNIT' | 'GRAM' | 'TON' | 'GALLON' | 'FOOT' | 'YARD' | 'CM' | 'MM' | 'INCH' | 'POUND' | 'OUNCE' | 'CUP' | 'TABLESPOON' | 'TEASPOON', cop: 0, quantity: 0 }
  } catch (error: any) {
    let errorMessage = 'An error occurred.'
    if (error && error.response && error.response.data) {
      if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      } else if (error.response.data.message) {
        errorMessage = error.response.data.message
      } else if (error.response.data.error) {
        errorMessage = error.response.data.error
      } else {
        errorMessage = JSON.stringify(error.response.data)
      }
    } else if (error && error.message) {
      errorMessage = error.message
    }
    alert(`❌ Product save failed: ${errorMessage}`)
  }
}

function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  editingProduct.value = null
  form.value = {
    name: '',
    unit: 'PCS' as 'M' | 'BAG' | 'KILO' | 'PCS' | 'KG' | 'L' | 'BOX' | 'PACK' | 'UNIT' | 'GRAM' | 'TON' | 'GALLON' | 'FOOT' | 'YARD' | 'CM' | 'MM' | 'INCH' | 'POUND' | 'OUNCE' | 'CUP' | 'TABLESPOON' | 'TEASPOON',
    cop: 0,
    quantity: 0
  }
}
</script>

<style scoped>
.products-page {
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

.products-table {
  width: 100%;
  border-collapse: collapse;
}

.products-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.products-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.table-row:hover {
  background: #f9fafb;
}

.unit-badge {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.low-stock {
  color: #dc2626;
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

.action-btn.edit {
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