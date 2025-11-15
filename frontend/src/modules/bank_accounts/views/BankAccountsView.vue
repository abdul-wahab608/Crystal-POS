<template>
  <div class="bank-accounts-page">
    <div class="page-header">
      <h1 class="page-title">Bank Accounts</h1>
      <button class="btn-primary" @click="showAddForm = true">Add Bank Account</button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Total Accounts</h3>
        <p class="stat-number">{{ store.bankAccounts.length }}</p>
      </div>
      <div class="stat-card">
        <h3>Active Accounts</h3>
        <p class="stat-number">{{ store.activeAccounts.length }}</p>
      </div>
      <div class="stat-card">
        <h3>Inactive Accounts</h3>
        <p class="stat-number">{{ store.inactiveAccounts.length }}</p>
      </div>
    </div>

    <!-- Bank Accounts Table -->
    <div class="table-container">
      <div v-if="store.loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading bank accounts...</p>
      </div>

      <table v-else class="bank-accounts-table">
        <thead>
          <tr>
            <th>Account Name</th>
            <th>Account Number</th>
            <th>Bank Name</th>
            <th>Branch</th>
            <th>IFSC Code</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in store.bankAccounts" :key="account.id" class="table-row">
            <td>{{ account.name }}</td>
            <td>{{ account.account_number }}</td>
            <td>{{ account.bank_name }}</td>
            <td>{{ account.branch || '-' }}</td>
            <td>{{ account.ifsc_code || '-' }}</td>
            <td>
              <span :class="getStatusClass(account.is_active)">
                {{ account.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <div class="actions">
                <button class="action-btn edit" @click="editAccount(account)" title="Edit">
                  ✏️
                </button>
                <button 
                  class="action-btn toggle" 
                  @click="toggleStatus(account.id)" 
                  :title="account.is_active ? 'Deactivate' : 'Activate'"
                >
                  {{ account.is_active ? '🔴' : '🟢' }}
                </button>
                <button class="action-btn delete" @click="deleteAccount(account.id)" title="Delete">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="store.bankAccounts.length === 0 && !store.loading" class="empty-state">
        <p>No bank accounts found.</p>
        <button class="btn-primary" @click="showAddForm = true">Add First Account</button>
      </div>
    </div>

    <!-- Add/Edit Form Modal -->
    <div v-if="showAddForm || editingAccount" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ editingAccount ? 'Edit Bank Account' : 'Add Bank Account' }}</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="form">
          <div class="form-group">
            <label for="name">Account Name *</label>
            <input 
              id="name"
              v-model="form.name" 
              type="text" 
              required 
              class="form-input"
              placeholder="Enter account name"
            />
          </div>
          
          <div class="form-group">
            <label for="account_number">Account Number *</label>
            <input 
              id="account_number"
              v-model="form.account_number" 
              type="text" 
              required 
              class="form-input"
              placeholder="Enter account number"
            />
          </div>
          
          <div class="form-group">
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
          
          <div class="form-row">
            <div class="form-group">
              <label for="branch">Branch</label>
              <input 
                id="branch"
                v-model="form.branch" 
                type="text" 
                class="form-input"
                placeholder="Enter branch name"
              />
            </div>
            
            <div class="form-group">
              <label for="ifsc_code">IFSC Code</label>
              <input 
                id="ifsc_code"
                v-model="form.ifsc_code" 
                type="text" 
                class="form-input"
                placeholder="Enter IFSC code"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="form.is_active"
              />
              Active Account
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="store.loading">
              {{ store.loading ? 'Saving...' : (editingAccount ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useBankAccountsStore } from '../stores/bank_accounts'
import type { BankAccount, CreateBankAccount } from '../types'

const store = useBankAccountsStore()

// Modal states
const showAddForm = ref(false)
const editingAccount = ref<BankAccount | null>(null)

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

// Form data
const form = ref<CreateBankAccount & { other_bank_name?: string }>({
  name: '',
  account_number: '',
  bank_name: '',
  branch: '',
  ifsc_code: '',
  is_active: true,
  other_bank_name: ''
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
  store.fetchBankAccounts()
})

function editAccount(account: BankAccount) {
  editingAccount.value = account
  form.value = {
    name: account.name,
    account_number: account.account_number,
    bank_name: account.bank_name,
    branch: account.branch || '',
    ifsc_code: account.ifsc_code || '',
    is_active: account.is_active
  }
  bankSearchQuery.value = account.bank_name
}

async function handleSubmit() {
  try {
    // Use other_bank_name if 'Other' is selected
    const submitData = { ...form.value }
    if (form.value.bank_name === 'Other' && form.value.other_bank_name) {
      submitData.bank_name = form.value.other_bank_name
    }
    delete submitData.other_bank_name
    
    if (editingAccount.value) {
      await store.updateBankAccount(editingAccount.value.id, submitData)
    } else {
      await store.createBankAccount(submitData)
    }
    closeModal()
    resetForm()
  } catch (error) {
    console.error('Error saving bank account:', error)
  }
}

function deleteAccount(id: number) {
  if (confirm('Are you sure you want to delete this bank account?')) {
    store.deleteBankAccount(id).catch(error => {
      console.error('Error deleting bank account:', error)
    })
  }
}

async function toggleStatus(id: number) {
  await store.toggleAccountStatus(id)
}

function closeModal() {
  showAddForm.value = false
  editingAccount.value = null
  resetForm()
}

function resetForm() {
  form.value = {
    name: '',
    account_number: '',
    bank_name: '',
    branch: '',
    ifsc_code: '',
    is_active: true,
    other_bank_name: ''
  }
  bankSearchQuery.value = ''
}

function getStatusClass(isActive: boolean) {
  return isActive ? 'status-active' : 'status-inactive'
}

onMounted(() => {
  store.fetchBankAccounts()
})
</script>

<style scoped>
.bank-accounts-page {
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

.stat-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-number {
  margin: 0;
  font-size: 2rem;
  font-weight: bold;
  color: #2563eb;
}

.table-container {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading-state {
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

.bank-accounts-table {
  width: 100%;
  border-collapse: collapse;
}

.bank-accounts-table th,
.bank-accounts-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.bank-accounts-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
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
  gap: 0.25rem;
}

.action-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
}

.action-btn.edit:hover {
  background: #dbeafe;
}

.action-btn.toggle:hover {
  background: #fef3c7;
}

.action-btn.delete:hover {
  background: #fee2e2;
}

.empty-state {
  text-align: center;
  color: #6b7280;
  padding: 3rem;
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

.modal-content {
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

.form {
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
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
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
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