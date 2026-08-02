<template>
  <div class="assets-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Assets Management</h1>
      <div class="header-actions">
        <ExportButton entityType="assets" />
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
          Add Asset
        </button>
      </div>
    </div>

    <!-- Batch Actions Toolbar -->
    <BatchActionsToolbar 
      entityType="assets"
      entityLabel="asset"
      :showActivate="false"
      :showDeactivate="false"
      @action-complete="handleBatchActionComplete"
    />

    <!-- Loading State -->
    <div v-if="store.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading assets...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="error-state">
      <p class="error-message">{{ store.error }}</p>
      <button @click="store.fetchAssets()" class="btn-secondary">Try Again</button>
    </div>

    <!-- Content -->
    <div v-else class="content">
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ assets.length }}</div>
          <div class="stat-label">Total Assets</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">₨{{ totalValue.toFixed(2) }}</div>
          <div class="stat-label">Total Value</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ activeAssets }}</div>
          <div class="stat-label">Active Assets</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ depreciatedAssets }}</div>
          <div class="stat-label">Depreciated</div>
        </div>
      </div>

      <!-- Search -->
      <div class="filters-section">
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Search assets..." 
          class="search-input"
        />
      </div>

      <!-- Assets Table -->
      <div class="table-container">
        <table class="assets-table">
          <thead>
            <tr>
              <th class="checkbox-col">
                <SelectAllCheckbox 
                  entityType="assets" 
                  :allIds="filteredAssets.map(a => a.id)" 
                />
              </th>
              <th>Asset Name</th>
              <th>Category</th>
              <th>Purchase Value</th>
              <th>Current Value</th>
              <th>Status</th>
              <th>Purchase Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="asset in filteredAssets" :key="asset.id" class="table-row">
              <td class="checkbox-col">
                <SelectableCheckbox entityType="assets" :id="asset.id" />
              </td>
              <td>
                <div class="asset-info">
                  <div class="asset-icon">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                    </svg>
                  </div>
                  <div>
                    <div class="asset-name">{{ asset.name }}</div>
                    <div class="asset-description">{{ asset.description }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span class="category-badge">{{ asset.category }}</span>
              </td>
              <td>₨{{ asset.purchase_value.toFixed(2) }}</td>
              <td>₨{{ asset.current_value.toFixed(2) }}</td>
              <td>
                <span :class="getStatusClass(asset.status)">
                  {{ asset.status }}
                </span>
              </td>
              <td>{{ formatDate(asset.purchase_date) }}</td>
              <td>
                <div class="actions">
                  <button @click="editAsset(asset)" class="action-btn edit">Edit</button>
                  <button @click="deleteAsset(asset)" class="action-btn delete">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredAssets.length === 0" class="empty-state">
          <p>No assets found.</p>
          <button @click="showAddForm = true" class="btn-primary">Add Your First Asset</button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Asset Modal -->
    <div v-if="showAddForm || showEditForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ showEditForm ? 'Edit Asset' : 'Add New Asset' }}</h2>
          <button @click="closeForm" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveAsset" class="modal-form">
          <div class="form-group">
            <label for="name">Asset Name</label>
            <input 
              id="name"
              v-model="form.name" 
              type="text" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="description">Description</label>
            <textarea 
              id="description"
              v-model="form.description" 
              class="form-input"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="category">Category</label>
              <select id="category" v-model="form.category" required class="form-input">
                <option value="">Select Category</option>
                <option value="Equipment">Equipment</option>
                <option value="Furniture">Furniture</option>
                <option value="Vehicles">Vehicles</option>
                <option value="Buildings">Buildings</option>
                <option value="Technology">Technology</option>
                <option value="Other">Other</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="status">Status</label>
              <select id="status" v-model="form.status" required class="form-input">
                <option value="">Select Status</option>
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
                <option value="Under Maintenance">Under Maintenance</option>
                <option value="Disposed">Disposed</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="purchase_value">Purchase Value</label>
              <input 
                id="purchase_value"
                v-model.number="form.purchase_value" 
                type="number" 
                step="0.01" 
                required 
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label for="current_value">Current Value</label>
              <input 
                id="current_value"
                v-model.number="form.current_value" 
                type="number" 
                step="0.01" 
                required 
                class="form-input"
              />
            </div>
          </div>
          
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
            <label for="location">Location</label>
            <input 
              id="location"
              v-model="form.location" 
              type="text" 
              class="form-input"
            />
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">
              {{ showEditForm ? 'Update' : 'Create' }} Asset
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Import Wizard -->
    <ImportWizard 
      v-if="showImportWizard"
      entityType="assets"
      @close="handleImportClose"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAssetsStore } from '../stores/assets'
import { useAuthStore } from '../../../shared/stores/auth'
import { useBatchActionsStore } from '../../../shared/stores/batchActions'
import ImportWizard from '../../../shared/components/ImportWizard/ImportWizard.vue'
import ExportButton from '../../../shared/components/ExportButton.vue'
import BatchActionsToolbar from '../../../shared/components/BatchActionsToolbar.vue'
import SelectAllCheckbox from '../../../shared/components/SelectAllCheckbox.vue'
import SelectableCheckbox from '../../../shared/components/SelectableCheckbox.vue'
import type { Asset, CreateAssetRequest } from '../types'

const store = useAssetsStore()
const authStore = useAuthStore()
const batchStore = useBatchActionsStore()
const searchTerm = ref('')
const showAddForm = ref(false)
const showEditForm = ref(false)
const showImportWizard = ref(false)
const editingAsset = ref<Asset | null>(null)

const form = ref<CreateAssetRequest>({
  name: '',
  description: '',
  category: '',
  type: 'EQUIPMENT',
  value: 0,
  current_value: 0,
  purchase_value: 0,
  purchase_date: new Date().toISOString().split('T')[0],
  location: '',
  status: 'ACTIVE'
})

onMounted(() => {
  store.fetchAssets()
})

const assets = computed(() => store.assets || [])

const filteredAssets = computed(() => {
  if (!searchTerm.value) return assets.value
  return assets.value.filter(asset => 
    asset.name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    asset.description.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    asset.category.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

const totalValue = computed(() => 
  assets.value.reduce((sum, asset) => sum + asset.current_value, 0)
)

const activeAssets = computed(() => 
  assets.value.filter(a => a.status === 'Active').length
)

const depreciatedAssets = computed(() => 
  assets.value.filter(a => a.current_value < a.purchase_value * 0.5).length
)

function editAsset(asset: Asset) {
  editingAsset.value = asset
  form.value = { ...asset }
  showEditForm.value = true
}

async function deleteAsset(asset: Asset) {
  if (confirm('Are you sure you want to delete this asset?')) {
    try {
      await store.deleteAsset(asset.id)
    } catch (error) {
      // Handle error silently
    }
  }
}

async function saveAsset() {
  try {
    if (showEditForm.value) {
      await store.updateAsset(editingAsset.value!.id, form.value)
    } else {
      await store.createAsset(form.value)
    }
    closeForm()
  } catch (error) {
    // Handle error silently
  }
}

function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  editingAsset.value = null
  form.value = {
    name: '',
    description: '',
    category: '',
    type: 'EQUIPMENT',
    value: 0,
    current_value: 0,
    purchase_value: 0,
    purchase_date: new Date().toISOString().split('T')[0],
    location: '',
    status: 'ACTIVE'
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString()
}

function getStatusClass(status: string) {
  switch (status.toLowerCase()) {
    case 'active':
      return 'status-active'
    case 'inactive':
      return 'status-inactive'
    case 'under maintenance':
      return 'status-maintenance'
    case 'disposed':
      return 'status-disposed'
    default:
      return 'status-default'
  }
}

function handleImportClose() {
  showImportWizard.value = false
  store.fetchAssets()
}

function handleBatchActionComplete(action: string, result: any) {
  store.fetchAssets()
  console.log(`Batch ${action} completed:`, result.message)
}
</script>

<style scoped>
.assets-page {
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

.assets-table {
  width: 100%;
  border-collapse: collapse;
}

.assets-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.assets-table td {
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

.asset-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.asset-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.asset-name {
  font-weight: 500;
  color: #111827;
}

.asset-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.category-badge {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-inactive {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-maintenance {
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-disposed {
  background: #f3f4f6;
  color: #6b7280;
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