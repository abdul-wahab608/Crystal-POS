<template>
  <div class="payments-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Payments Management</h1>
      <button @click="showAddForm = true" class="btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        New Payment
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading payments...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="error-state">
      <p class="error-message">{{ store.error }}</p>
      <button @click="store.fetchPayments()" class="btn-secondary">Try Again</button>
    </div>

    <!-- Content -->
    <div v-else class="content">
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ payments.length }}</div>
          <div class="stat-label">Total Payments</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">₨{{ typeof totalAmount === 'number' ? totalAmount.toFixed(2) : '0.00' }}</div>
          <div class="stat-label">Total Amount</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ thisMonthPayments }}</div>
          <div class="stat-label">This Month</div>
        </div>
      </div>

      <!-- Search -->
      <div class="filters-section">
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Search payments..." 
          class="search-input"
        />
      </div>

      <!-- Payments Table -->
      <div class="table-container">
        <table class="payments-table">
          <thead>
            <tr>
              <th>Payment ID</th>
              <th>Type</th>
              <th>From → To</th>
              <th>Amount</th>
              <th>Method</th>
              <th>Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in filteredPayments" :key="payment.id" class="table-row">
              <td>#{{ payment.id }}</td>
              <td>
                <span :class="getTypeClass(payment.payment_type)">
                  {{ getTypeLabel(payment.payment_type) }}
                </span>
              </td>
              <td>{{ getPaymentParties(payment) }}</td>
              <td>₨{{ (Number(payment.amount) || 0).toFixed(2) }}</td>
              <td>
                <span class="payment-method">{{ payment.payment_method }}</span>
              </td>
              <td>{{ formatDate(payment.date || payment.payment_date) }}</td>
              <td>
                <span :class="getStatusClass(payment.status)">
                  {{ payment.status }}
                </span>
              </td>
              <td>
                <div class="actions">
                  <button @click="editPayment(payment)" class="action-btn edit">Edit</button>
                  <button @click="deletePayment(payment)" class="action-btn delete">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredPayments.length === 0" class="empty-state">
          <p>No payments found.</p>
          <button @click="showAddForm = true" class="btn-primary">Create Your First Payment</button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Payment Modal -->
    <div v-if="showAddForm || showEditForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ showEditForm ? 'Edit Payment' : 'Add New Payment' }}</h2>
          <button @click="closeForm" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="savePayment" class="modal-form">
          <div class="form-group">
            <label for="payment_type">Payment Type</label>
            <select id="payment_type" v-model="form.payment_type" required class="form-input">
              <option value="INCOMING">Incoming (Customer pays me)</option>
              <option value="OUTGOING">Outgoing (I pay vendor)</option>
              <option value="DIRECT">Direct (Customer pays vendor directly)</option>
            </select>
          </div>
          
          <div class="form-group" v-if="form.payment_type === 'INCOMING' || form.payment_type === 'DIRECT'">
            <label for="customer">Customer *</label>
            <select id="customer" v-model="form.customer" required class="form-input">
              <option value="">Select Customer</option>
              <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                {{ customer.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group" v-if="form.payment_type === 'OUTGOING' || form.payment_type === 'DIRECT'">
            <label for="vendor">Vendor {{ form.payment_type === 'DIRECT' ? '(Receiving Payment) *' : '*' }}</label>
            <select id="vendor" v-model="form.vendor" required class="form-input">
              <option value="">Select Vendor</option>
              <option v-for="vendor in vendors" :key="vendor.id" :value="vendor.id">
                {{ vendor.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="amount">Amount</label>
            <input 
              id="amount"
              v-model.number="form.amount" 
              type="number" 
              step="0.01" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="payment_method">Payment Method</label>
            <select id="payment_method" v-model="form.payment_method" required class="form-input">
              <option value="">Select Method</option>
              <option value="CASH">Cash</option>
              <option value="BANK">Bank Transfer</option>
              <option value="CHEQUE">Cheque</option>
              <option value="PARCHI">Parchi (Promissory)</option>
            </select>
          </div>
          
          <div class="form-group" v-if="form.payment_method === 'BANK'">
            <label for="bank_name">Bank Name *</label>
            <div class="bank-select-wrapper">
              <input 
                id="bank_search"
                v-model="bankSearchQuery"
                type="text" 
                class="form-input"
                placeholder="Search for a bank..."
                @focus="showBankDropdown = true"
                @input="showBankDropdown = true"
                required
              />
              <div v-if="showBankDropdown" class="bank-dropdown">
                <div 
                  v-for="bank in filteredBanks" 
                  :key="bank"
                  class="bank-option"
                  @click="selectBank(bank)"
                >
                  {{ bank }}
                </div>
                <div v-if="filteredBanks.length === 0" class="bank-option disabled">
                  No banks found
                </div>
              </div>
            </div>
            <div v-if="form.bank_name === 'Other'" class="form-group" style="margin-top: 10px;">
              <label for="other_bank_name">Specify Bank Name *</label>
              <input 
                id="other_bank_name"
                v-model="form.other_bank_name" 
                type="text" 
                required 
                class="form-input"
                placeholder="Enter bank name"
              />
            </div>
            <p v-if="form.bank_name && form.bank_name !== 'Other'" class="selected-bank">
              Selected: <strong>{{ form.bank_name }}</strong>
            </p>
          </div>
          
          <div class="form-group" v-if="form.payment_method === 'BANK'">
            <label for="account_number">Account Number</label>
            <input 
              id="account_number"
              v-model="form.account_number" 
              type="text" 
              class="form-input"
              placeholder="Enter account number (optional)"
            />
          </div>
          
          <div class="form-group">
            <label for="payment_date">Transaction Date</label>
            <input 
              id="payment_date"
              v-model="form.payment_date" 
              type="date" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="reference">Reference Number</label>
            <input 
              id="reference"
              v-model="form.reference_number" 
              type="text" 
              class="form-input"
            />
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
          
          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">
              {{ showEditForm ? 'Update' : 'Create' }} Payment
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePaymentsStore } from '../stores/payments'
import { useCustomersStore } from '../../customers/stores/customers'
import { useVendorsStore } from '../../vendors/stores/vendors'
import type { Payment, CreatePaymentRequest } from '../types'

const store = usePaymentsStore()
const customersStore = useCustomersStore()
const vendorsStore = useVendorsStore()

const searchTerm = ref('')
const showAddForm = ref(false)
const showEditForm = ref(false)
const editingPayment = ref<Payment | null>(null)

// Bank dropdown states
const showBankDropdown = ref(false)
const bankSearchQuery = ref('')

// Pakistani Banks List
const pakistaniBanks = [
  'Allied Bank Limited (ABL)',
  'Askari Bank',
  'Bank Alfalah',
  'Bank AL Habib',
  'Bank of Punjab',
  'BankIslami',
  'Citibank Pakistan',
  'Faysal Bank',
  'First Women Bank',
  'Habib Bank Limited (HBL)',
  'Habib Metropolitan Bank Limited',
  'JS Bank',
  'MCB Bank Limited',
  'Meezan Bank',
  'National Bank of Pakistan (NBP)',
  'Standard Chartered Bank Pakistan',
  'Soneri Bank',
  'Summit Bank',
  'United Bank Limited (UBL)',
  'HBL Microfinance Bank',
  'Khushhali Microfinance Bank Limited',
  'U Microfinance Bank (UBank)',
  'Easypaisa',
  'JazzCash',
  'Other'
]

// Computed filtered banks based on search
const filteredBanks = computed(() => {
  if (!bankSearchQuery.value) {
    return pakistaniBanks
  }
  const query = bankSearchQuery.value.toLowerCase()
  return pakistaniBanks.filter(bank => 
    bank.toLowerCase().includes(query)
  )
})

const form = ref<CreatePaymentRequest & { bank_name?: string; other_bank_name?: string; account_number?: string }>({
  customer: undefined,
  vendor: undefined,
  amount: 0,
  payment_type: 'INCOMING',
  payment_method: 'CASH',
  related_entity: 'CUSTOMER',
  payment_date: new Date().toISOString().split('T')[0],
  date: new Date().toISOString().split('T')[0],
  status: 'COMPLETED',
  reference_number: '',
  notes: '',
  bank_name: '',
  other_bank_name: '',
  account_number: ''
})

function selectBank(bank: string) {
  form.value.bank_name = bank
  bankSearchQuery.value = bank
  showBankDropdown.value = false
  
  // Clear other bank name if not selecting 'Other'
  if (bank !== 'Other') {
    form.value.other_bank_name = ''
  }
}

// Close dropdown when clicking outside
onMounted(() => {
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement
    if (!target.closest('.bank-select-wrapper')) {
      showBankDropdown.value = false
    }
  })
  store.fetchPayments()
  customersStore.fetchCustomers()
  vendorsStore.fetchVendors()
})

const payments = computed(() => store.payments || [])
const customers = computed(() => customersStore.customers || [])
const vendors = computed(() => vendorsStore.vendors || [])

const filteredPayments = computed(() => {
  if (!searchTerm.value) return payments.value
  return payments.value.filter(payment => 
    payment.id.toString().includes(searchTerm.value) ||
    payment.reference_number?.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

const totalAmount = computed(() => {
  if (!Array.isArray(payments.value)) return 0
  return payments.value.reduce((sum, payment) => {
    const amount = Number(payment.amount) || 0
    return sum + amount
  }, 0)
})

const thisMonthPayments = computed(() => {
  const thisMonth = new Date().getMonth()
  const thisYear = new Date().getFullYear()
  return payments.value.filter(p => {
    const created = new Date(p.payment_date)
    return created.getMonth() === thisMonth && created.getFullYear() === thisYear
  }).length
})

function editPayment(payment: Payment) {
  editingPayment.value = payment
  form.value = { ...payment }
  showEditForm.value = true
}

async function deletePayment(payment: Payment) {
  if (confirm('Are you sure you want to delete this payment?')) {
    try {
      await store.deletePayment(payment.id)
    } catch (error) {
      // Handle error silently
    }
  }
}

async function savePayment() {
  try {
    const payload = { ...form.value }
    
    // Use other_bank_name if 'Other' is selected
    if (payload.bank_name === 'Other' && payload.other_bank_name) {
      payload.bank_name = payload.other_bank_name
    }
    delete payload.other_bank_name
    
    // Map vendor to direct_payment_to_vendor for DIRECT payments
    if (payload.payment_type === 'DIRECT' && payload.vendor) {
      payload.direct_payment_to_vendor = payload.vendor
      delete payload.vendor
    }
    
    if (showEditForm.value) {
      await store.updatePayment(editingPayment.value!.id, payload)
    } else {
      await store.createPayment(payload)
    }
    closeForm()
  } catch (error) {
    alert('Failed to save payment. Please check the form and try again.')
  }
}

function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  editingPayment.value = null
  form.value = {
    customer: undefined,
    vendor: undefined,
    amount: 0,
    payment_type: 'INCOMING',
    payment_method: 'CASH',
    related_entity: 'CUSTOMER',
    payment_date: new Date().toISOString().split('T')[0],
    date: new Date().toISOString().split('T')[0],
    status: 'COMPLETED',
    reference_number: '',
    notes: '',
    bank_name: '',
    other_bank_name: '',
    account_number: ''
  }
  bankSearchQuery.value = ''
}

function formatDate(dateString: string) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return 'Invalid Date'
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function getStatusClass(status: string) {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'status-completed'
    case 'pending':
      return 'status-pending'
    case 'failed':
      return 'status-failed'
    default:
      return 'status-default'
  }
}

function getTypeLabel(type: string) {
  const labels: Record<string, string> = {
    'INCOMING': 'Incoming',
    'OUTGOING': 'Outgoing',
    'DIRECT': 'Direct'
  }
  return labels[type] || type
}

function getTypeClass(type: string) {
  const classes: Record<string, string> = {
    'INCOMING': 'type-incoming',
    'OUTGOING': 'type-outgoing',
    'DIRECT': 'type-direct'
  }
  return classes[type] || ''
}

function getPaymentParties(payment: any) {
  if (payment.payment_type === 'INCOMING') {
    const customerId = typeof payment.customer === 'object' ? payment.customer?.id : payment.customer
    const customerName = typeof payment.customer === 'object' ? payment.customer?.name : 
                        customers.value.find(c => c.id === customerId)?.name
    return `${customerName || 'Customer'} → Me`
  } else if (payment.payment_type === 'OUTGOING') {
    const vendorId = typeof payment.vendor === 'object' ? payment.vendor?.id : payment.vendor
    const vendorName = typeof payment.vendor === 'object' ? payment.vendor?.name : 
                      vendors.value.find(v => v.id === vendorId)?.name
    return `Me → ${vendorName || 'Vendor'}`
  } else if (payment.payment_type === 'DIRECT') {
    const customerId = typeof payment.customer === 'object' ? payment.customer?.id : payment.customer
    const customerName = typeof payment.customer === 'object' ? payment.customer?.name : 
                        customers.value.find(c => c.id === customerId)?.name
    const vendorId = typeof payment.direct_payment_to_vendor === 'object' ? payment.direct_payment_to_vendor?.id : payment.direct_payment_to_vendor
    const vendorName = typeof payment.direct_payment_to_vendor === 'object' ? payment.direct_payment_to_vendor?.name : 
                      vendors.value.find(v => v.id === vendorId)?.name
    return `${customerName || 'Customer'} → ${vendorName || 'Vendor'}`
  }
  return 'N/A'
}
</script>

<style scoped>
.payments-page {
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

.payments-table {
  width: 100%;
  border-collapse: collapse;
}

.payments-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.payments-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.table-row:hover {
  background: #f9fafb;
}

.payment-method {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
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

.status-failed {
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

.type-incoming {
  background: #dcfce7;
  color: #16a34a;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-outgoing {
  background: #fef3c7;
  color: #d97706;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-direct {
  background: #dbeafe;
  color: #2563eb;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
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
  max-height: 90vh;
  overflow-y: auto;
  margin: 1rem;
  display: flex;
  flex-direction: column;
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

.helper-text {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.helper-text .link {
  color: #2563eb;
  text-decoration: underline;
}

.helper-text .link:hover {
  color: #1d4ed8;
}

.bank-select-wrapper {
  position: relative;
}

.bank-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  max-height: 300px;
  overflow-y: auto;
  z-index: 10;
  margin-top: 0.25rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.bank-option {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.15s;
}

.bank-option:hover:not(.disabled) {
  background: #f3f4f6;
}

.bank-option.disabled {
  color: #9ca3af;
  cursor: not-allowed;
}

.selected-bank {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #059669;
  padding: 0.5rem;
  background: #d1fae5;
  border-radius: 0.375rem;
}

.selected-bank strong {
  font-weight: 600;
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