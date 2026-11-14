<template>
  <div class="customers-view">
    <header class="page-head">
      <h1>Customers</h1>
      <button v-if="auth.canImport" type="button" class="secondary-btn" @click="showImportWizard = true">Import</button>
      <button type="button" class="primary-btn" @click="openForm(null)">Add customer</button>
    </header>

    <ImportWizard v-if="showImportWizard" entityType="customer" @close="handleImportClose" />

    <section class="filters">
      <input v-model="search" type="search" class="form-input" placeholder="Search name or phone" aria-label="Search customers" />
      <select v-model="city" class="form-input" aria-label="City">
        <option value="">All cities</option>
        <option v-for="c in cities" :key="c" :value="c">{{ c }}</option>
      </select>
    </section>

    <p v-if="customersStore.error" class="form-error">{{ customersStore.error }}</p>

    <div class="layout">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>City</th>
              <th>Phone</th>
              <th>Type</th>
              <th class="num">Balance</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!filtered.length && !customersStore.loading">
              <td colspan="5" class="empty">No customers match these filters.</td>
            </tr>
            <tr
              v-for="customer in pageItems"
              :key="customer.id"
              :class="{ selected: customer.id === selectedId }"
              class="clickable"
              @click="select(customer.id)"
            >
              <td>{{ customer.name }}</td>
              <td>{{ customer.city || '—' }}</td>
              <td>{{ customer.phone || '—' }}</td>
              <td>{{ customer.customer_type === 'WALK_IN' ? 'Walk-in' : 'Regular' }}</td>
              <td class="num" :class="{ owed: Number(customer.balance) > 0 }">{{ customerBalanceLabel(customer.balance) }}</td>
            </tr>
          </tbody>
        </table>
        <PaginationBar
          :page="page"
          :totalPages="totalPages"
          :total="total"
          :pageSize="pageSize"
          @update:page="goTo"
          @update:pageSize="setPageSize"
        />
      </div>

      <aside v-if="selected" class="detail" aria-label="Customer detail">
        <header class="detail-head">
          <div>
            <h2>{{ selected.name }}</h2>
            <p class="muted">{{ [selected.city, selected.phone].filter(Boolean).join(' · ') || 'No city or phone' }}</p>
            <p class="balance">Balance <strong>{{ customerBalanceLabel(selected.balance) }}</strong></p>
          </div>
          <div class="detail-actions">
            <button type="button" class="primary-btn" @click="showPayment = true">Record payment</button>
            <button v-if="auth.isManager" type="button" class="secondary-btn" @click="openForm(selected)">Edit</button>
            <button v-if="auth.isManager" type="button" class="danger-btn" @click="removeCustomer">Delete</button>
          </div>
        </header>

        <p v-if="detailError" class="form-error">{{ detailError }}</p>

        <h3>Sales</h3>
        <table class="data-table compact">
          <thead>
            <tr><th>Bill</th><th>Date</th><th class="num">Total</th><th class="num">Balance</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr v-if="!sales.length"><td colspan="5" class="empty">No sales yet.</td></tr>
            <tr v-for="sale in sales" :key="sale.id">
              <td>{{ sale.bill_no }}</td>
              <td>{{ formatDate(sale.date) }}</td>
              <td class="num">{{ formatMoney(Number(sale.total_amount)) }}</td>
              <td class="num">{{ formatMoney(Number(sale.balance)) }}</td>
              <td><span class="badge" :class="sale.payment_status.toLowerCase()">{{ paymentStatusLabel(sale.payment_status) }}</span></td>
            </tr>
          </tbody>
        </table>

        <h3>Ledger</h3>
        <table class="data-table compact">
          <thead>
            <tr><th>Date</th><th>Entry</th><th class="num">Debit</th><th class="num">Credit</th><th class="num">Balance</th></tr>
          </thead>
          <tbody>
            <tr v-if="!ledger.length"><td colspan="5" class="empty">No entries yet.</td></tr>
            <tr v-for="row in ledger" :key="row.id">
              <td>{{ formatDate(row.date) }}</td>
              <td>{{ ledgerTypeLabel(row.type) }} <span class="muted">{{ row.reference }}</span></td>
              <td class="num">{{ row.debit ? formatMoney(Number(row.debit)) : '' }}</td>
              <td class="num">{{ row.credit ? formatMoney(Number(row.credit)) : '' }}</td>
              <td class="num">{{ formatMoney(Number(row.balance)) }}</td>
            </tr>
          </tbody>
        </table>
      </aside>
    </div>

    <div v-if="showForm" class="modal-backdrop" @click.self="closeForm">
      <div class="modal" role="dialog" :aria-label="editing ? 'Edit customer' : 'Add customer'">
        <h2>{{ editing ? 'Edit customer' : 'Add customer' }}</h2>
        <CustomerForm :customer="editing" @saved="onSaved" @cancel="closeForm" />
      </div>
    </div>

    <div v-if="showPayment && selected" class="modal-backdrop" @click.self="showPayment = false">
      <div class="modal" role="dialog" aria-label="Record payment">
        <h2>Record payment for {{ selected.name }}</h2>
        <PaymentForm :preset-customer-id="selected.id" @saved="onPaymentSaved" @cancel="showPayment = false" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { ref, computed, watch, onMounted } from 'vue'
import CustomerForm from '../components/CustomerForm.vue'
import PaymentForm from '../../payments/components/PaymentForm.vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import { useCustomersStore } from '../stores/customers'
import { useSalesStore } from '../../sales/stores/sales'
import { useAuthStore } from '../../../shared/stores/auth'
import { useToastStore } from '../../../shared/stores/toast'
import { apiErrorMessage } from '../../../shared/utils/apiError'
import { customerBalanceLabel, paymentStatusLabel } from '../../../shared/utils/statusLabels'
import type { Customer, LedgerRow } from '../types'
import type { Sale } from '../../sales/types'
import ImportWizard from '../../../shared/components/ImportWizard/ImportWizard.vue'

const customersStore = useCustomersStore()
const salesStore = useSalesStore()
const auth = useAuthStore()
const toast = useToastStore()
const showImportWizard = ref(false)

function handleImportClose() {
  showImportWizard.value = false
  customersStore.fetchCustomers()
}

const search = ref('')
const city = ref('')
const selectedId = ref<number | null>(null)
const sales = ref<Sale[]>([])
const ledger = ref<LedgerRow[]>([])
const detailError = ref('')
const showForm = ref(false)
const editing = ref<Customer | null>(null)
const showPayment = ref(false)

const selected = computed(() => customersStore.customers.find(c => c.id === selectedId.value) ?? null)

const cities = computed(() => [...new Set(customersStore.customers.map(c => c.city).filter((c): c is string => !!c))].sort())

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  return customersStore.customers
    .filter(c => !city.value || c.city === city.value)
    .filter(c => !q || c.name.toLowerCase().includes(q) || (c.phone ?? '').toLowerCase().includes(q))
})

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(filtered)
watch([search, city], reset)

const loadDetail = async () => {
  if (selectedId.value === null) return
  detailError.value = ''
  try {
    const [ledgerData, customerSales] = await Promise.all([
      customersStore.fetchLedger(selectedId.value),
      salesStore.fetchCustomerSales(selectedId.value),
    ])
    ledger.value = ledgerData.rows
    sales.value = customerSales
  } catch (e) {
    detailError.value = apiErrorMessage(e)
  }
}

const select = (id: number) => {
  selectedId.value = id
  loadDetail()
}

watch(selectedId, () => {
  sales.value = []
  ledger.value = []
})

const openForm = (customer: Customer | null) => {
  editing.value = customer
  showForm.value = true
}

const closeForm = () => {
  showForm.value = false
  editing.value = null
}

const onSaved = (customer: Customer | undefined) => {
  closeForm()
  if (customer && !editing.value) select(customer.id)
  else loadDetail()
}

const onPaymentSaved = async () => {
  showPayment.value = false
  await customersStore.fetchCustomers()
  await loadDetail()
}

const removeCustomer = async () => {
  if (!selected.value) return
  if (!window.confirm(`Delete ${selected.value.name}? This cannot be undone.`)) return
  try {
    const id = selected.value.id
    const deleted = await acceptQueued(async () => {
      await customersStore.deleteCustomer(id)
      return true
    })
    if (!deleted) return
    selectedId.value = null
    toast.success('Customer deleted')
  } catch (e) {
    detailError.value = apiErrorMessage(e)
  }
}

const formatDate = (value: string) => new Date(value).toLocaleDateString('en-PK')
const ledgerTypeLabel = (type: LedgerRow['type']) => ({ SALE: 'Sale', PAYMENT: 'Payment', REVERSAL: 'Reversal' })[type]
const formatMoney = (value: number) => `₨${value.toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

onMounted(() => customersStore.fetchCustomers())
</script>

<style scoped>
.customers-view { display: flex; flex-direction: column; gap: 1rem; padding: 1rem; }
.page-head { display: flex; justify-content: space-between; align-items: center; }
.page-head h1 { margin: 0; font-size: 1.5rem; }
.filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); gap: 0.5rem; }
.layout { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr); gap: 1rem; align-items: start; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.data-table th, .data-table td { padding: 0.5rem; border-bottom: 1px solid #e5e7eb; text-align: left; white-space: nowrap; }
.data-table.compact th, .data-table.compact td { padding: 0.35rem 0.4rem; }
.data-table .num { text-align: right; font-variant-numeric: tabular-nums; }
.clickable { cursor: pointer; }
.selected { background: rgba(37, 99, 235, 0.08); }
.owed { color: #b42318; font-weight: 600; }
.empty { text-align: center; opacity: 0.7; }
.muted { opacity: 0.6; }
.balance { margin: 0.25rem 0 0; }
.form-error { color: #b42318; margin: 0; }
.detail { border: 1px solid #e5e7eb; border-radius: 10px; padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem; min-width: 0; }
.detail-head { display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.detail-head h2 { margin: 0; }
.detail-head p { margin: 0.2rem 0 0; }
.detail-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: flex-start; }
.detail h3 { margin: 0.75rem 0 0.25rem; font-size: 1rem; }
.danger-btn { background: #b42318; color: #fff; border: none; border-radius: 6px; padding: 0.5rem 0.9rem; cursor: pointer; }
.badge { padding: 0.15rem 0.55rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; background: #eee; }
.badge.paid { background: #d1fae5; color: #065f46; }
.badge.partial { background: #fef3c7; color: #92400e; }
.badge.unpaid { background: #fee2e2; color: #991b1b; }
.modal-backdrop { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: flex-start; justify-content: center; overflow-y: auto; padding: 2rem 1rem; z-index: 50; }
.modal { background: #fff; color: #111; border-radius: 10px; padding: 1.25rem; width: min(40rem, 100%); }
.modal h2 { margin-top: 0; }
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
}
</style>
