<template>
  <div class="sales-view">
    <header class="page-head">
      <h1>Sales</h1>
      <button type="button" class="primary-btn" @click="showForm = true">New sale</button>
    </header>

    <section class="filters">
      <input
        v-model="filters.search"
        type="search"
        class="form-input"
        placeholder="Search bill number or customer"
        aria-label="Search sales"
      />
      <div class="filter-customer">
        <SearchableSelect
          v-model="filters.customer"
          :options="customerOptions"
          placeholder="All customers"
        />
      </div>
      <select v-model="filters.payment_status" class="form-input" aria-label="Payment status">
        <option value="">All statuses</option>
        <option value="PAID">Paid</option>
        <option value="PARTIAL">Part paid</option>
        <option value="UNPAID">Unpaid</option>
      </select>
      <input v-model="filters.date_from" type="date" class="form-input" aria-label="From date" />
      <input v-model="filters.date_to" type="date" class="form-input" aria-label="To date" />
    </section>

    <p v-if="error" class="form-error">{{ error }}</p>
    <p class="summary">
      {{ salesStore.sales.length }} bills · Total {{ formatMoney(totals.total) }} · Received {{ formatMoney(totals.received) }} · Balance {{ formatMoney(totals.balance) }}
    </p>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Bill</th>
            <th>Customer</th>
            <th>Date</th>
            <th class="num">Lines</th>
            <th class="num">Total</th>
            <th class="num">Received</th>
            <th class="num">Balance</th>
            <th>Status</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr v-if="!salesStore.sales.length && !salesStore.loading">
            <td colspan="9" class="empty">No sales match these filters.</td>
          </tr>
          <tr v-for="sale in pageItems" :key="sale.id">
            <td>{{ sale.bill_no }}</td>
            <td>{{ sale.customer_name }}<span v-if="sale.customer_city" class="muted"> · {{ sale.customer_city }}</span></td>
            <td>{{ formatDate(sale.date) }}</td>
            <td class="num">{{ sale.items_count }}</td>
            <td class="num">{{ formatMoney(Number(sale.total_amount)) }}</td>
            <td class="num">{{ formatMoney(Number(sale.amount_paid)) }}</td>
            <td class="num">{{ formatMoney(Number(sale.balance)) }}</td>
            <td><span class="badge" :class="sale.payment_status.toLowerCase()">{{ paymentStatusLabel(sale.payment_status) }}</span></td>
            <td class="actions">
              <button type="button" class="link-btn" @click="billSale = sale">View bill</button>
              <button v-if="auth.isManager" type="button" class="link-btn danger" @click="removeSale(sale)">Delete</button>
            </td>
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

    <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
      <div class="modal" role="dialog" aria-label="New sale">
        <h2>New sale</h2>
        <SalesForm @saved="onSaved" @cancel="showForm = false" />
      </div>
    </div>

    <div v-if="billSale" class="modal-backdrop" @click.self="billSale = null">
      <div class="modal modal-wide" role="dialog" aria-label="Bill">
        <SaleBill :sale="billSale" :unit-by-product-id="unitByProductId" @close="billSale = null" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import SalesForm from '../components/SalesForm.vue'
import SaleBill from '../components/SaleBill.vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import { useSalesStore } from '../stores/sales'
import { useCustomersStore } from '../../customers/stores/customers'
import { useAuthStore } from '../../../shared/stores/auth'
import { useToastStore } from '../../../shared/stores/toast'
import { apiErrorMessage } from '../../../shared/utils/apiError'
import { paymentStatusLabel } from '../../../shared/utils/statusLabels'
import type { Sale, SaleFilters } from '../types'

const salesStore = useSalesStore()
const customersStore = useCustomersStore()
const auth = useAuthStore()
const toast = useToastStore()

const showForm = ref(false)
const billSale = ref<Sale | null>(null)
const error = ref('')

const filters = reactive<{
  search: string
  customer: number | null
  payment_status: '' | 'PAID' | 'PARTIAL' | 'UNPAID'
  date_from: string
  date_to: string
}>({ search: '', customer: null, payment_status: '', date_from: '', date_to: '' })

const customerOptions = computed(() => customersStore.customers.map(c => ({ value: c.id, label: c.name })))

const unitByProductId = computed(() => Object.fromEntries(salesStore.products.map(p => [p.id, p.unit])))

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(computed(() => salesStore.sales))

const totals = computed(() => salesStore.sales.reduce(
  (acc, sale) => ({
    total: acc.total + Number(sale.total_amount),
    received: acc.received + Number(sale.amount_paid),
    balance: acc.balance + Number(sale.balance),
  }),
  { total: 0, received: 0, balance: 0 },
))

const activeFilters = (): SaleFilters => {
  const params: SaleFilters = {}
  if (filters.search.trim()) params.search = filters.search.trim()
  if (filters.customer) params.customer = filters.customer
  if (filters.payment_status) params.payment_status = filters.payment_status
  if (filters.date_from) params.date_from = filters.date_from
  if (filters.date_to) params.date_to = filters.date_to
  return params
}

const reload = async () => {
  error.value = ''
  try {
    await salesStore.fetchSales(activeFilters())
  } catch (e) {
    error.value = apiErrorMessage(e)
  }
}

let searchTimer: ReturnType<typeof setTimeout> | undefined
watch(() => filters.search, () => {
  reset()
  clearTimeout(searchTimer)
  searchTimer = setTimeout(reload, 300)
})
watch(() => [filters.customer, filters.payment_status, filters.date_from, filters.date_to], () => {
  reset()
  reload()
})

const onSaved = async () => {
  showForm.value = false
  await reload()
}

const removeSale = async (sale: Sale) => {
  if (!window.confirm('This deletes the bill, its payments, and returns the stock. The customer balance is corrected.')) return
  try {
    const deleted = await acceptQueued(async () => {
      await salesStore.deleteSale(sale.id)
      return true
    })
    if (!deleted) return
    toast.success('Sale deleted', sale.bill_no)
    await customersStore.fetchCustomers()
  } catch (e) {
    toast.error('Could not delete sale', apiErrorMessage(e))
  }
}

const formatDate = (value: string) => new Date(value).toLocaleDateString('en-PK')
const formatMoney = (value: number) => `₨${value.toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

onMounted(async () => {
  try {
    await Promise.all([salesStore.fetchCatalog(), customersStore.fetchCustomers()])
  } catch (e) {
    error.value = apiErrorMessage(e)
  }
  await reload()
})

onBeforeUnmount(() => clearTimeout(searchTimer))
</script>

<style scoped>
.sales-view { display: flex; flex-direction: column; gap: 1rem; padding: 1rem; }
.page-head { display: flex; justify-content: space-between; align-items: center; }
.page-head h1 { margin: 0; font-size: 1.5rem; }
.filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); gap: 0.5rem; align-items: start; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.data-table th, .data-table td { padding: 0.5rem; border-bottom: 1px solid #e5e7eb; text-align: left; white-space: nowrap; }
.data-table .num { text-align: right; font-variant-numeric: tabular-nums; }
.empty { text-align: center; opacity: 0.7; }
.muted { opacity: 0.6; }
.summary { margin: 0; font-size: 0.9rem; opacity: 0.8; }
.form-error { color: #b42318; margin: 0; }
.actions { display: flex; gap: 0.75rem; }
.link-btn { background: none; border: none; color: #2563eb; cursor: pointer; padding: 0; }
.link-btn.danger { color: #b42318; }
.badge { padding: 0.15rem 0.55rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; background: #eee; }
.badge.paid { background: #d1fae5; color: #065f46; }
.badge.partial { background: #fef3c7; color: #92400e; }
.badge.unpaid { background: #fee2e2; color: #991b1b; }
.modal-backdrop { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: flex-start; justify-content: center; overflow-y: auto; padding: 2rem 1rem; z-index: 50; }
.modal { background: #fff; color: #111; border-radius: 10px; padding: 1.25rem; width: min(70rem, 100%); }
.modal-wide { width: min(50rem, 100%); }
.modal h2 { margin-top: 0; }
@media (max-width: 640px) {
  .page-head { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
}
</style>
