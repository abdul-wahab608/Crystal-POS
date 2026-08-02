<template>
  <div class="products-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Products Management</h1>
      <div class="header-actions">
        <ExportButton entityType="products" />
        <button v-if="authStore.canImport" @click="showImportWizard = true" class="btn-secondary">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
          </svg>
          Import
        </button>
        <button @click="showAddForm = true" class="btn-primary">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Product
        </button>
      </div>
    </div>

    <!-- Batch Actions Toolbar -->
    <BatchActionsToolbar 
      entityType="products"
      entityLabel="product"
      :showActivate="false"
      :showDeactivate="false"
      @action-complete="handleBatchActionComplete"
    />

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
        <select v-model="sizeRangeFilter" class="form-input filter-select">
          <option value="">All Size Ranges</option>
          <option v-for="sr in sizeRanges" :key="sr.id" :value="sr.id">{{ sr.name }}</option>
        </select>
        <select v-model="colorFilter" class="form-input filter-select">
          <option value="">All Colors</option>
          <option v-for="c in colors" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <!-- Products Table -->
      <div class="table-container">
        <table class="products-table">
          <thead>
            <tr>
              <th class="checkbox-col">
                <SelectAllCheckbox 
                  entityType="products" 
                  :allIds="filteredProducts.map(p => p.id)" 
                />
              </th>
              <th>Name</th>
              <th>Unit</th>
              <th>Price</th>
              <th>Stock (dozens)</th>
              <th>Stock (pcs)</th>
              <th>Variants</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredProducts" :key="product.id" class="table-row">
              <td class="checkbox-col">
                <SelectableCheckbox entityType="products" :id="product.id" />
              </td>
              <td>{{ product.name }}</td>
              <td>
                <span class="unit-badge">{{ product.unit }}</span>
              </td>
              <td>₨{{ Number(product.cop).toFixed(2) }}</td>
              <td>
                <span :class="totalVariantDozens(product) < 5 ? 'low-stock' : ''">
                  {{ totalVariantDozens(product) }} dz
                </span>
              </td>
              <td>
                <span :class="Number(product.quantity) < 60 ? 'low-stock' : ''">
                  {{ product.quantity }}
                </span>
              </td>
              <td>
                <ul>
                  <li v-for="variant in product.variants" :key="variant.id">
                    Size: {{ getSizeRangeName(variant.size_range) }},
                    Color: {{ getColorName(variant.color) }},
                    Qty: {{ variant.quantity_dozens }} dozens
                  </li>
                </ul>
              </td>
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

    <!-- Size Range and Color Management -->
    <div class="flex gap-8 mb-6">
      <SizeRangeManager />
      <ColorManager />
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
          
          <div class="form-group">
            <label for="sizeRange">Size Range</label>
            <select id="sizeRange" v-model="form.size_range" required class="form-input">
              <option value="">Select Size Range</option>
              <option v-for="sr in sizeRanges" :key="sr.id" :value="sr.id">{{ sr.name }}</option>
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

          <div class="form-group">
            <label>Product Variants (Size, Color, Quantity in Dozens)</label>
            <div class="variant-list mb-2">
              <div v-for="(variant, idx) in form.variants" :key="idx" class="flex gap-2 items-center mb-1">
                <select v-model="variant.size_range" required class="form-input w-32">
                  <option value="">Size Range</option>
                  <option v-for="sr in sizeRanges" :key="sr.id" :value="sr.id">{{ sr.name }}</option>
                </select>
                <select v-model="variant.color" required class="form-input w-32">
                  <option value="">Color</option>
                  <option v-for="c in colors" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
                <input v-model.number="variant.quantity_dozens" type="number" min="0" placeholder="Qty (dozens)" class="form-input w-24" required />
                <button type="button" @click="removeVariant(idx)" class="btn btn-danger">Delete</button>
              </div>
            </div>
            <button type="button" @click="addVariant" class="btn btn-secondary">Add Variant</button>
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

    <!-- Import Wizard -->
    <ImportWizard 
      v-if="showImportWizard"
      entityType="products"
      @close="handleImportClose"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductsStore } from '../stores/products'
import ImportWizard from '../../../shared/components/ImportWizard/ImportWizard.vue'
import ExportButton from '../../../shared/components/ExportButton.vue'
import BatchActionsToolbar from '../../../shared/components/BatchActionsToolbar.vue'
import SelectAllCheckbox from '../../../shared/components/SelectAllCheckbox.vue'
import SelectableCheckbox from '../../../shared/components/SelectableCheckbox.vue'
import { useAuthStore } from '../../../shared/stores/auth'
import { useBatchActionsStore } from '../../../shared/stores/batchActions'
import SizeRangeManager from '../components/SizeRangeManager.vue'
import ColorManager from '../components/ColorManager.vue'
import { useSizeRangeStore } from '../stores/sizeRange'
import { useColorStore } from '../stores/color'
import { useProductVariantStore } from '../stores/productVariant'

const store = useProductsStore()
const authStore = useAuthStore()
const batchStore = useBatchActionsStore()
const sizeRangeStore = useSizeRangeStore()
const colorStore = useColorStore()
const productVariantStore = useProductVariantStore()
const { sizeRanges } = storeToRefs(sizeRangeStore)
const { colors } = storeToRefs(colorStore)
const searchTerm = ref('')
const sizeRangeFilter = ref('')
const colorFilter = ref('')
const showAddForm = ref(false)
const showEditForm = ref(false)
const showImportWizard = ref(false)
const editingProduct = ref<any>(null)

const form = ref({
  name: '',
  unit: 'PCS' as 'M' | 'BAG' | 'KILO' | 'PCS' | 'KG' | 'L' | 'BOX' | 'PACK' | 'UNIT' | 'GRAM' | 'TON' | 'GALLON' | 'FOOT' | 'YARD' | 'CM' | 'MM' | 'INCH' | 'POUND' | 'OUNCE' | 'CUP' | 'TABLESPOON' | 'TEASPOON',
  cop: 0,
  quantity: 0,
  size_range: '',
  variants: [{ size_range: '', color: '', quantity_dozens: 0 }]
})

onMounted(() => {
  store.fetchProducts()
  sizeRangeStore.fetchSizeRanges()
  colorStore.fetchColors()
})

const products = computed(() => {
  const productsArray = store.products || []
  // Filter to show only MANUFACTURED products in the Products tab
  return Array.isArray(productsArray) 
    ? productsArray.filter((p: any) => !p.product_type && !p.type || (p.product_type || p.type) === 'MANUFACTURED')
    : []
})

const filteredProducts = computed(() => {
  let productsArray = products.value
  if (!Array.isArray(productsArray)) return []
  if (searchTerm.value) {
    productsArray = productsArray.filter(p =>
      p.name.toLowerCase().includes(searchTerm.value.toLowerCase())
    )
  }
  if (sizeRangeFilter.value) {
    productsArray = productsArray.filter((p: any) =>
      (p.variants || []).some((v: any) => v.size_range === Number(sizeRangeFilter.value))
    )
  }
  if (colorFilter.value) {
    productsArray = productsArray.filter((p: any) =>
      (p.variants || []).some((v: any) => v.color === Number(colorFilter.value))
    )
  }
  return productsArray
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
    quantity: product.quantity,
    size_range: product.size_range,
    variants: product.variants || [{ size_range: '', color: '', quantity_dozens: 0 }]
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
    let productId: number | null = null
    if (showEditForm.value && editingProduct.value) {
      await store.updateProduct(editingProduct.value.id, form.value)
      productId = editingProduct.value.id
    } else {
      const existingProduct = products.value.find(
        p => p.name.toLowerCase() === form.value.name.toLowerCase() && p.unit === form.value.unit
      )
      if (existingProduct) {
        const newQuantity = Number(existingProduct.quantity) + Number(form.value.quantity)
        await store.updateProduct(existingProduct.id, {
          ...existingProduct,
          quantity: newQuantity
        })
        productId = existingProduct.id
      } else {
        const created = await store.createProduct({ ...form.value, cop: 0 })
        productId = created.id
      }
    }
    // Save variants (skip rows already persisted and incomplete rows)
    if (productId) {
      for (const variant of form.value.variants) {
        if ((variant as any).id) continue
        if (!variant.size_range || !variant.color || !variant.quantity_dozens) continue
        await productVariantStore.addVariant({
          product: productId,
          size_range: Number(variant.size_range),
          color: Number(variant.color),
          quantity_dozens: variant.quantity_dozens
        })
      }
    }
    await store.fetchProducts()
    showAddForm.value = false
    showEditForm.value = false
    editingProduct.value = null
    form.value = { name: '', unit: 'PCS' as 'M' | 'BAG' | 'KILO' | 'PCS' | 'KG' | 'L' | 'BOX' | 'PACK' | 'UNIT' | 'GRAM' | 'TON' | 'GALLON' | 'FOOT' | 'YARD' | 'CM' | 'MM' | 'INCH' | 'POUND' | 'OUNCE' | 'CUP' | 'TABLESPOON' | 'TEASPOON', cop: 0, quantity: 0, size_range: '', variants: [{ size_range: '', color: '', quantity_dozens: 0 }] }
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
    quantity: 0,
    size_range: '',
    variants: [{ size_range: '', color: '', quantity_dozens: 0 }]
  }
}

function handleImportClose() {
  showImportWizard.value = false
  store.fetchProducts()
}

function handleBatchActionComplete(action: string, result: any) {
  store.fetchProducts()
  console.log(`Batch ${action} completed:`, result.message)
}

function getSizeRangeName(id: number) {
  const sr = sizeRanges.value.find((s: any) => s.id === id)
  return sr ? sr.name : id
}
function getColorName(id: number) {
  const c = colors.value.find((c: any) => c.id === id)
  return c ? c.name : id
}
function totalVariantDozens(product: any): number {
  return (product.variants || []).reduce((sum: number, v: any) => sum + (v.quantity_dozens || 0), 0)
}

function addVariant() {
  form.value.variants.push({ size_range: '', color: '', quantity_dozens: 0 })
}
function removeVariant(idx: number) {
  form.value.variants.splice(idx, 1)
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

.header-actions {
  display: flex;
  gap: 0.75rem;
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
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filter-select {
  width: auto;
  min-width: 160px;
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

.checkbox-col {
  width: 40px;
  text-align: center;
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

.variant-list { margin-bottom: 1rem; }
.btn-secondary { background: #e0e7ef; color: #222; }
.btn-danger { background: #dc2626; color: #fff; }
</style>