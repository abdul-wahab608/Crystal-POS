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
              <th>Bill No</th>
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
              <td>{{ sale.bill_no }}</td>
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
    <SalesForm
      v-if="showAddForm"
      :customers="customers"
      @save="handleSaveSale"
      @close="closeForm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSalesStore } from '../stores/sales'
import { useCustomersStore } from '../../customers/stores/customers'
import SalesForm from '../components/SalesForm.vue'
import type { Sale, CreateSaleRequest } from '../types'

const store = useSalesStore()
const customersStore = useCustomersStore()

const searchTerm = ref('')
const showAddForm = ref(false)

onMounted(() => {
  store.fetchSales()
  customersStore.fetchCustomers()
})

const sales = computed(() => store.sales || [])
const customers = computed(() => customersStore.customers || [])

const filteredSales = computed(() => {
  if (!searchTerm.value) return sales.value
  return sales.value.filter(sale =>
    sale.customer_name?.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    sale.bill_no?.toLowerCase().includes(searchTerm.value.toLowerCase())
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

function viewSale(sale: Sale) {
  // Create a detailed sale view
  let details = `Bill No: ${sale.bill_no}\n`
  details += `Customer: ${sale.customer_name}\n`
  details += `Date: ${sale.date ? formatDate(sale.date) : 'N/A'}\n`
  details += `Total: ₨${Number(sale.total_amount || 0).toFixed(2)}\n`
  details += `Status: ${sale.payment_status || 'UNKNOWN'}\n\n`

  if (sale.sale_items && sale.sale_items.length > 0) {
    details += 'Items:\n'
    sale.sale_items.forEach(item => {
      details += `• ${item.product_name} (${item.size_range_name}, ${item.color_name}) x ${item.quantity_dozens} dz @ ₨${item.unit_price} = ₨${item.subtotal}\n`
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

async function handleSaveSale(payload: CreateSaleRequest) {
  try {
    await store.createSale(payload)
    closeForm()
    alert('✅ Sale created successfully! Stock has been updated.')
  } catch (error: any) {
    if (error && error.response && error.response.data) {
      const data = error.response.data
      const message = typeof data === 'string' ? data : data.message || data.error || JSON.stringify(data)
      alert(`❌ Sale creation failed: ${message}`)
    } else {
      alert('❌ Sale creation failed. Please try again.')
    }
  }
}

function closeForm() {
  showAddForm.value = false
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