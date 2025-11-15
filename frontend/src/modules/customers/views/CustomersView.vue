<template>
  <div class="customers-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Customers Management</h1>
      <button @click="showAddForm = true" class="btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Add Customer
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading customers...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="error-state">
      <p class="error-message">{{ store.error }}</p>
      <button @click="store.fetchCustomers()" class="btn-secondary">Try Again</button>
    </div>

    <!-- Content -->
    <div v-else class="content">
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ customers.length }}</div>
          <div class="stat-label">Total Customers</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ activeCustomers }}</div>
          <div class="stat-label">Active Customers</div>
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
          placeholder="Search customers..." 
          class="search-input"
        />
      </div>

      <!-- Customers Table -->
      <div class="table-container">
        <table class="customers-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Address</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="customer in filteredCustomers" :key="customer.id" class="table-row">
              <td>{{ customer.name }}</td>
              <td>{{ customer.email }}</td>
              <td>{{ customer.phone }}</td>
              <td>{{ customer.address }}</td>
              <td>
                <span :class="customer.is_active ? 'status-active' : 'status-inactive'">
                  {{ customer.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <div class="actions">
                  <button @click="editCustomer(customer)" class="action-btn edit">Edit</button>
                  <button @click="deleteCustomer(customer)" class="action-btn delete">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredCustomers.length === 0" class="empty-state">
          <p>No customers found.</p>
          <button @click="showAddForm = true" class="btn-primary">Add Your First Customer</button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Customer Modal -->
    <div v-if="showAddForm || showEditForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ showEditForm ? 'Edit Customer' : 'Add New Customer' }}</h2>
          <button @click="closeForm" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveCustomer" class="modal-form">
          <div class="form-group">
            <label for="name">Customer Name</label>
            <input 
              id="name"
              v-model="form.name" 
              type="text" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="email">Email</label>
            <input 
              id="email"
              v-model="form.email" 
              type="email" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="phone">Phone</label>
            <input 
              id="phone"
              v-model="form.phone" 
              type="tel" 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="address">Address</label>
            <textarea 
              id="address"
              v-model="form.address" 
              class="form-input"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="form.is_active" 
                type="checkbox" 
                class="checkbox"
              />
              Active Customer
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">
              {{ showEditForm ? 'Update' : 'Create' }} Customer
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCustomersStore } from '../stores/customers'
import type { Customer, CreateCustomerRequest } from '../types'

const store = useCustomersStore()
const searchTerm = ref('')
const showAddForm = ref(false)
const showEditForm = ref(false)
const editingCustomer = ref<Customer | null>(null)

const form = ref<CreateCustomerRequest>({
  name: '',
  email: '',
  phone: '',
  address: '',
  is_active: true
})

onMounted(() => {
  store.fetchCustomers()
})

const customers = computed(() => store.customers || [])

const filteredCustomers = computed(() => {
  if (!searchTerm.value) return customers.value
  return customers.value.filter(customer => 
    customer.name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

const activeCustomers = computed(() => 
  customers.value.filter(c => c.is_active).length
)

const newThisMonth = computed(() => {
  const thisMonth = new Date().getMonth()
  const thisYear = new Date().getFullYear()
  return customers.value.filter(c => {
    const created = new Date(c.created_at)
    return created.getMonth() === thisMonth && created.getFullYear() === thisYear
  }).length
})

function editCustomer(customer: Customer) {
  editingCustomer.value = customer
  form.value = { ...customer }
  showEditForm.value = true
}

async function deleteCustomer(customer: Customer) {
  if (confirm('Are you sure you want to delete this customer?')) {
    try {
      await store.deleteCustomer(customer.id)
    } catch (error) {
    }
  }
}

async function saveCustomer() {
  try {
    if (showEditForm.value) {
      await store.updateCustomer(editingCustomer.value!.id, form.value)
    } else {
      await store.createCustomer(form.value)
    }
    closeForm()
  } catch (error) {
  }
}

function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  editingCustomer.value = null
  form.value = {
    name: '',
    email: '',
    phone: '',
    address: '',
    is_active: true
  }
}
</script>

<style scoped>
.customers-page {
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

.customers-table {
  width: 100%;
  border-collapse: collapse;
}

.customers-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.customers-table td {
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox {
  width: 1rem;
  height: 1rem;
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