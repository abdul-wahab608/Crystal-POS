<template>
  <div class="ledger">
    <div class="ledger-header">
      <div>
        <span class="muted">Opening balance</span>
        <strong>{{ opening.toFixed(2) }}</strong>
        <span class="muted"> · Current balance</span>
        <strong>{{ Number(vendor.balance).toFixed(2) }}</strong>
      </div>
      <button v-if="!paying" class="btn-primary small" @click="paying = true">Record payment</button>
    </div>

    <VendorPaymentForm v-if="paying" :vendor="vendor" @success="onPaid" @cancel="paying = false" />

    <p v-if="loading" class="muted">Loading ledger...</p>
    <p v-else-if="error" class="form-error">{{ error }}</p>
    <div v-else-if="rows.length">
    <table class="ledger-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Type</th>
          <th>Reference</th>
          <th>Pays bill</th>
          <th class="num">Purchase (debit)</th>
          <th class="num">Payment (credit)</th>
          <th class="num">Running balance</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in pageItems" :key="row.id">
          <td>{{ new Date(row.date).toLocaleDateString() }}</td>
          <td>{{ row.type === 'PURCHASE' ? 'Purchase' : 'Payment' }}</td>
          <td>{{ row.reference || '-' }}</td>
          <td>{{ billFor(row) }}</td>
          <td class="num">{{ row.debit ? row.debit.toFixed(2) : '' }}</td>
          <td class="num">{{ row.credit ? row.credit.toFixed(2) : '' }}</td>
          <td class="num">{{ row.balance.toFixed(2) }}</td>
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
    <p v-else class="muted">No purchases or payments for this vendor yet.</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import VendorPaymentForm from './VendorPaymentForm.vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import { useVendorsStore } from '../stores/vendors'
import { buildLedger, openingBalance } from '../utils/ledger'
import { errorMessageOf } from '../../raw_materials/utils/errorMessage'
import type { LedgerRow, Vendor, VendorTransaction } from '../types'

const props = defineProps<{ vendor: Vendor }>()

const vendorsStore = useVendorsStore()
const transactions = ref<VendorTransaction[]>([])
const loading = ref(true)
const error = ref('')
const paying = ref(false)

const billByReference = ref(new Map<string, number>())
const rows = computed<LedgerRow[]>(() => buildLedger(props.vendor, transactions.value))
const opening = computed(() => openingBalance(props.vendor, transactions.value))
const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize } = usePagination(rows)

function billFor(row: LedgerRow): string {
  if (row.type !== 'PAYMENT') return ''
  const billId = billByReference.value.get(row.reference)
  return billId ? `Purchase #${billId}` : '-'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [ledger, payments] = await Promise.all([
      vendorsStore.fetchLedger(props.vendor.id),
      vendorsStore.fetchVendorPayments(props.vendor.id),
    ])
    transactions.value = ledger
    billByReference.value = new Map(
      payments.flatMap(payment => (payment.purchase ? [[`Payment #${payment.id}`, payment.purchase.id] as [string, number]] : [])),
    )
  } catch (e) {
    error.value = errorMessageOf(e)
  } finally {
    loading.value = false
  }
}

async function onPaid() {
  paying.value = false
  await load()
}

onMounted(load)
</script>

<style scoped>
.ledger { padding: 0.75rem 1rem 1rem; background: #f9fafb; }
.ledger-header { display: flex; justify-content: space-between; align-items: center; gap: 1rem; font-size: 0.875rem; }
.ledger-header strong { margin: 0 0.5rem 0 0.25rem; }
.muted { color: #6b7280; }
.form-error { color: #b91c1c; font-size: 0.875rem; }
.ledger-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; margin-top: 0.75rem; background: white; }
.ledger-table th, .ledger-table td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: left; }
.ledger-table th { font-weight: 600; background: #f3f4f6; }
.num { text-align: right; white-space: nowrap; }
.btn-primary.small { padding: 0.25rem 0.75rem; font-size: 0.875rem; }
</style>
