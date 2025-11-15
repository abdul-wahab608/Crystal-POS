<template>
  <div class="vendors-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Vendors Management</h1>
      <button @click="showAddForm = true" class="btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Add Vendor
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading vendors...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="error-state">
      <p class="error-message">{{ store.error }}</p>
      <button @click="store.fetchVendors()" class="btn-secondary">Try Again</button>
    </div>

    <!-- Content -->
    <div v-else class="content">
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ vendors.length }}</div>
          <div class="stat-label">Total Vendors</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ activeVendors }}</div>
          <div class="stat-label">Active Vendors</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ newThisMonth }}</div>
          <div class="stat-label">New This Month</div>
        </div>
      </div>

      <!-- Search -->
      <div class="filters-section">
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Search vendors..." 
          class="search-input"
        />
      </div>

      <!-- Vendors Table -->
      <div class="table-container">
        <table class="vendors-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Contact Person</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Address</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vendor in filteredVendors" :key="vendor.id" class="table-row">
              <td>{{ vendor.name }}</td>
              <td>{{ vendor.contact_person }}</td>
              <td>{{ vendor.email }}</td>
              <td>{{ vendor.phone }}</td>
              <td>{{ vendor.address }}</td>
              <td>
                <span :class="vendor.is_active ? 'status-active' : 'status-inactive'">
                  {{ vendor.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <div class="actions">
                  <button @click="editVendor(vendor)" class="action-btn edit">Edit</button>
                  <button @click="deleteVendor(vendor.id)" class="action-btn delete">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredVendors.length === 0" class="empty-state">
          <p>No vendors found.</p>
          <button @click="showAddForm = true" class="btn-primary">Add Your First Vendor</button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Vendor Modal -->
    <VendorForm
      v-if="showAddForm || showEditForm"
      :vendor="editingVendor"
      @save="handleSave"
      @close="closeForm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useVendorsStore } from '../stores/vendors'
import type { Vendor } from '../types'
import VendorForm from '../components/VendorForm.vue'

const store = useVendorsStore()
const searchTerm = ref('')
const showAddForm = ref(false)
const showEditForm = ref(false)
const editingVendor = ref<Vendor | null>(null)
const errorMessage = ref('')

onMounted(() => {
  store.fetchVendors()
})

const vendors = computed(() => store.vendors || [])

const filteredVendors = computed(() => {
  if (!searchTerm.value) return vendors.value
  return vendors.value.filter(vendor => 
    vendor.name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    vendor.contact_person.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    vendor.email.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

const activeVendors = computed(() => 
  vendors.value.filter(v => v.is_active).length
)

const newThisMonth = computed(() => {
  const thisMonth = new Date().getMonth()
  const thisYear = new Date().getFullYear()
  return vendors.value.filter(v => {
    const created = new Date(v.created_at)
    return created.getMonth() === thisMonth && created.getFullYear() === thisYear
  }).length
})

function editVendor(vendor: Vendor) {
  editingVendor.value = vendor
  showEditForm.value = true
  showAddForm.value = false
}

function deleteVendor(id: number) {
  if (confirm('Are you sure you want to delete this vendor?')) {
    store.deleteVendor(id)
  }
}

async function handleSave(vendorData: any) {
  try {
    errorMessage.value = ''
    if (showEditForm.value && editingVendor.value) {
      await store.updateVendor(editingVendor.value.id, vendorData)
    } else {
      await store.createVendor(vendorData)
    }
    closeForm()
  } catch (error: any) {
    // Extract error message from response
    const message = error.response?.data?.error || error.message || 'Failed to save vendor'
    errorMessage.value = message
    alert(message)
  }
}

function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  editingVendor.value = null
  errorMessage.value = ''
}
</script>

<style scoped>
.vendors-page {
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

.vendors-table {
  width: 100%;
  border-collapse: collapse;
}

.vendors-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.vendors-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.table-row:hover {
  background: #f9fafb;
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