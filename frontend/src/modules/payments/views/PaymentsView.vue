<template>
  <div class="payments-view">
    <header class="page-head">
      <h1>Payments</h1>
      <button type="button" class="primary-btn" @click="showForm = true">Record payment</button>
    </header>

    <section class="filters">
      <select v-model="filters.payment_type" class="form-input" aria-label="Direction">
        <option value="">All directions</option>
        <option value="INCOMING">Money in</option>
        <option value="OUTGOING">Money out</option>
      </select>
      <input v-model="filters.date_from" type="date" class="form-input" aria-label="From date" />
      <input v-model="filters.date_to" type="date" class="form-input" aria-label="To date" />
      <input v-model="filters.search" type="search" class="form-input" placeholder="Search party, bill, reference" aria-label="Search payments" />
    </section>

    <p v-if="error" class="form-error">{{ error }}</p>
    <p class="summary">
      In {{ formatMoney(totals.in) }} · Out {{ formatMoney(totals.out) }} · Net {{ formatMoney(totals.in - totals.out) }}
    </p>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Direction</th>
            <th>Party</th>
            <th>Sale</th>
            <th>Method</th>
            <th class="num">Amount</th>
            <th>Reference</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr v-if="!paymentsStore.payments.length && !paymentsStore.loading">
            <td colspan="8" class="empty">No payments match these filters.</td>
          </tr>
          <tr v-for="payment in pageItems" :key="payment.id">
            <td>{{ formatDate(payment.payment_date) }}</td>
            <td>
              <span class="badge" :class="payment.payment_type === 'INCOMING' ? 'in' : 'out'">
                {{ payment.payment_type === 'INCOMING' ? 'In' : 'Out' }}
              </span>
            </td>
            <td>{{ payment.customer?.name ?? payment.vendor?.name ?? '—' }}</td>
            <td>{{ payment.sale?.bill_no ?? '—' }}</td>
            <td>{{ methodLabel(payment.payment_method) }}<span v-if="payment.bank_account" class="muted"> · {{ payment.bank_account.name }}</span></td>
            <td class="num">{{ formatMoney(Number(payment.amount)) }}</td>
            <td>{{ payment.reference || '—' }}</td>
            <td>
              <button v-if="auth.isManager" type="button" class="link-btn danger" @click="removePayment(payment)">Delete</button>
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
      <div class="modal" role="dialog" aria-label="Record payment">
        <h2>Record payment</h2>
        <PaymentForm @saved="onSaved" @cancel="showForm = false" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import PaymentForm from '../components/PaymentForm.vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import { usePaymentsStore } from '../stores/payments'
import { useAuthStore } from '../../../shared/stores/auth'
import { useToastStore } from '../../../shared/stores/toast'
import { apiErrorMessage } from '../../../shared/utils/apiError'
import type { Payment, PaymentFilters, PaymentMethod } from '../types'

const paymentsStore = usePaymentsStore()
const auth = useAuthStore()
const toast = useToastStore()

const showForm = ref(false)
const error = ref('')

const filters = reactive<{ payment_type: '' | 'INCOMING' | 'OUTGOING'; date_from: string; date_to: string; search: string }>({
  payment_type: '', date_from: '', date_to: '', search: '',
})

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(computed(() => paymentsStore.payments))

const totals = computed(() => paymentsStore.payments.reduce(
  (acc, p) => {
    const amount = Number(p.amount)
    if (p.payment_type === 'INCOMING') acc.in += amount
    else if (p.payment_type === 'OUTGOING') acc.out += amount
    return acc
  },
  { in: 0, out: 0 },
))

const activeFilters = (): PaymentFilters => {
  const params: PaymentFilters = {}
  if (filters.payment_type) params.payment_type = filters.payment_type
  if (filters.date_from) params.date_from = filters.date_from
  if (filters.date_to) params.date_to = filters.date_to
  if (filters.search.trim()) params.search = filters.search.trim()
  return params
}

const reload = async () => {
  error.value = ''
  try {
    await paymentsStore.fetchPayments(activeFilters())
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
watch(() => [filters.payment_type, filters.date_from, filters.date_to], () => {
  reset()
  reload()
})

const onSaved = async () => {
  showForm.value = false
  await reload()
}

const removePayment = async (payment: Payment) => {
  const party = payment.customer?.name ?? payment.vendor?.name ?? 'this party'
  const effect = payment.payment_type === 'INCOMING'
    ? `${party}'s balance will go up again, and the linked sale's status will be recalculated.`
    : `${party}'s balance will be restored.`
  if (!window.confirm(`Delete this payment of ${formatMoney(Number(payment.amount))}? ${effect}`)) return
  try {
    const deleted = await acceptQueued(async () => {
      await paymentsStore.deletePayment(payment.id)
      return true
    })
    if (!deleted) return
    toast.success('Payment deleted')
    await reload()
  } catch (e) {
    toast.error('Could not delete payment', apiErrorMessage(e))
  }
}

const methodLabels: Record<PaymentMethod, string> = {
  CASH: 'Cash', BANK: 'Bank transfer', CHEQUE: 'Cheque', PARCHI: 'Parchi',
}
const methodLabel = (method: PaymentMethod) => methodLabels[method] ?? method

const formatDate = (value: string) => new Date(value).toLocaleDateString('en-PK')
const formatMoney = (value: number) => `₨${value.toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

onMounted(async () => {
  try {
    await paymentsStore.fetchFormOptions()
  } catch (e) {
    error.value = apiErrorMessage(e)
  }
  await reload()
})

onBeforeUnmount(() => clearTimeout(searchTimer))
</script>

<style scoped>
.payments-view { display: flex; flex-direction: column; gap: 1rem; padding: 1rem; }
.page-head { display: flex; justify-content: space-between; align-items: center; }
.page-head h1 { margin: 0; font-size: 1.5rem; }
.filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); gap: 0.5rem; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.data-table th, .data-table td { padding: 0.5rem; border-bottom: 1px solid #e5e7eb; text-align: left; white-space: nowrap; }
.data-table .num { text-align: right; font-variant-numeric: tabular-nums; }
.empty { text-align: center; opacity: 0.7; }
.muted { opacity: 0.6; }
.summary { margin: 0; font-size: 0.9rem; opacity: 0.8; }
.form-error { color: #b42318; margin: 0; }
.link-btn { background: none; border: none; color: #b42318; cursor: pointer; padding: 0; }
.badge { padding: 0.15rem 0.55rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; background: #eee; }
.badge.in { background: #d1fae5; color: #065f46; }
.badge.out { background: #fee2e2; color: #991b1b; }
.modal-backdrop { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: flex-start; justify-content: center; overflow-y: auto; padding: 2rem 1rem; z-index: 50; }
.modal { background: #fff; color: #111; border-radius: 10px; padding: 1.25rem; width: min(42rem, 100%); }
.modal h2 { margin-top: 0; }
@media (max-width: 640px) {
  .page-head { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
}
</style>
