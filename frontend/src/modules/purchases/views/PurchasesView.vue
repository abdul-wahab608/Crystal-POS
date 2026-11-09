<template>
  <div class="purchases-page">
    <div class="page-header">
      <h1 class="page-title">Purchases</h1>
      <button class="btn-primary" @click="formOpen = true">New purchase</button>
    </div>

    <div class="filters">
      <label class="filter-check">
        <input v-model="unpaidOnly" type="checkbox" /> Unpaid bills only
      </label>
    </div>

    <p v-if="loadError" class="form-error">{{ loadError }}</p>
    <p v-else-if="loading" class="muted">Loading purchases...</p>

    <div v-else class="table-container">
      <table v-if="purchasesStore.purchases.length" class="purchases-table">
        <thead>
          <tr>
            <th></th>
            <th>Date</th>
            <th>Vendor</th>
            <th>Invoice #</th>
            <th class="num">Lines</th>
            <th class="num">Total</th>
            <th class="num">Paid</th>
            <th class="num">Unpaid</th>
            <th>Payment</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="purchase in pageItems" :key="purchase.id">
            <tr>
              <td>
                <button class="link-btn" :aria-expanded="expandedId === purchase.id" @click="toggle(purchase.id)">
                  {{ expandedId === purchase.id ? 'Hide' : 'Show' }}
                </button>
              </td>
              <td>{{ formatDate(purchase.date) }}</td>
              <td>
                <router-link :to="{ path: '/vendors', query: { vendor: purchase.vendor } }" class="vendor-link">
                  {{ purchase.vendor_name }}
                </router-link>
              </td>
              <td>{{ purchase.invoice_number || '-' }}</td>
              <td class="num">{{ purchase.items.length }}</td>
              <td class="num">{{ Number(purchase.total_amount).toFixed(2) }}</td>
              <td class="num">{{ Number(purchase.paid_amount).toFixed(2) }}</td>
              <td class="num">{{ Number(purchase.unpaid_amount).toFixed(2) }}</td>
              <td>
                <span class="badge" :class="purchase.payment_status.toLowerCase()">{{ paymentStatusLabel(purchase.payment_status) }}</span>
              </td>
              <td>
                <button class="link-btn danger" @click="confirmDelete(purchase)">Delete</button>
              </td>
            </tr>
            <tr v-if="expandedId === purchase.id" class="detail-row">
              <td colspan="10">
                <table class="lines-table">
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Variant</th>
                      <th class="num">Quantity</th>
                      <th class="num">Unit cost</th>
                      <th class="num">Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in purchase.items" :key="item.id">
                      <td>{{ item.raw_material_name ?? item.product_name }}</td>
                      <td>{{ item.raw_material_name ? 'Raw material' : `${item.size_range_name} / ${item.color_name}` }}</td>
                      <td class="num">{{ Number(item.quantity).toFixed(2) }} {{ item.unit }}</td>
                      <td class="num">{{ Number(item.unit_cost).toFixed(2) }}</td>
                      <td class="num">{{ Number(item.subtotal).toFixed(2) }}</td>
                    </tr>
                  </tbody>
                </table>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <p v-else class="empty-state">No purchases yet.</p>
      <PaginationBar
        v-if="purchasesStore.purchases.length"
        :page="page"
        :totalPages="totalPages"
        :total="total"
        :pageSize="pageSize"
        @update:page="goTo"
        @update:pageSize="setPageSize"
      />
    </div>

    <div v-if="formOpen" class="modal-overlay" @click.self="formOpen = false">
      <PurchaseForm @saved="onSaved" @cancel="formOpen = false" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePurchasesStore } from '../stores/purchases'
import { useToastStore } from '../../../shared/stores/toast'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { paymentStatusLabel } from '../../../shared/utils/statusLabels'
import { errorMessageOf } from '../../raw_materials/utils/errorMessage'
import PurchaseForm from '../components/PurchaseForm.vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import type { Purchase } from '../types'

const purchasesStore = usePurchasesStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const loadError = ref('')
const formOpen = ref(false)
const expandedId = ref<number | null>(null)
const unpaidOnly = ref(route.query.unpaid === 'true')
const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(computed(() => purchasesStore.purchases))

function formatDate(value: string) {
  return new Date(value).toLocaleDateString()
}

function toggle(id: number) {
  expandedId.value = expandedId.value === id ? null : id
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    await purchasesStore.fetchPurchases({ unpaid: unpaidOnly.value })
  } catch (e) {
    loadError.value = errorMessageOf(e)
  } finally {
    loading.value = false
  }
}

async function confirmDelete(purchase: Purchase) {
  if (Number(purchase.paid_amount) > 0) {
    toast.error(
      'Cannot delete this bill',
      `Delete the vendor payments for Purchase #${purchase.id} first (${Number(purchase.paid_amount).toFixed(2)} is paid against it).`,
    )
    return
  }
  if (!window.confirm(`Delete purchase #${purchase.id} from ${purchase.vendor_name}? Its stock and vendor balance will be reversed.`)) return
  try {
    await acceptQueued(() => purchasesStore.deletePurchase(purchase.id))
  } catch (e) {
    toast.error('Could not delete purchase', errorMessageOf(e))
  }
}

async function onSaved() {
  formOpen.value = false
  await load()
}

watch(unpaidOnly, (value) => {
  reset()
  router.replace({ query: value ? { unpaid: 'true' } : {} })
  load()
})

watch(() => route.query.unpaid, (value) => {
  unpaidOnly.value = value === 'true'
})

onMounted(load)
</script>

<style scoped>
.purchases-page { padding: 1.5rem; }
.filters { margin-bottom: 0.75rem; }
.filter-check { display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.875rem; cursor: pointer; }
.badge { display: inline-block; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
.badge.paid { background: #d1fae5; color: #065f46; }
.badge.partial { background: #fef3c7; color: #92400e; }
.badge.unpaid { background: #fee2e2; color: #991b1b; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.page-title { font-size: 1.5rem; font-weight: 600; }
.muted { color: #6b7280; }
.form-error { color: #b91c1c; }
.table-container { background: white; border-radius: 0.5rem; border: 1px solid #e5e7eb; overflow-x: auto; }
.purchases-table, .lines-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.purchases-table th, .purchases-table td, .lines-table th, .lines-table td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: left; }
.purchases-table th { background: #f9fafb; font-weight: 600; }
.lines-table { background: #f9fafb; }
.detail-row td { padding: 0.5rem 1rem 1rem; }
.num { text-align: right; white-space: nowrap; }
.link-btn { background: none; border: none; color: #2563eb; cursor: pointer; font-size: 0.875rem; }
.link-btn.danger { color: #b91c1c; }
.vendor-link { color: #2563eb; text-decoration: underline; }
.empty-state { padding: 2rem; text-align: center; color: #6b7280; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 1rem; }
.btn-primary { cursor: pointer; border: none; }
</style>
