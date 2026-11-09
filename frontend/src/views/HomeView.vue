<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="subtitle">Today and this month at a glance. Click a card to open its page.</p>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-if="loading && !summary" class="loading">Loading...</div>

    <template v-if="summary">
      <section class="kpi-section">
        <h2>Today ({{ summary.today.date }})</h2>
        <div class="kpi-grid">
          <router-link to="/sales" class="kpi-card">
            <span class="kpi-label">Sales total</span>
            <span class="kpi-value">₨{{ money(summary.today.sales_total) }}</span>
            <span class="kpi-detail">{{ summary.today.sales_count }} bills</span>
          </router-link>
          <router-link to="/payments" class="kpi-card">
            <span class="kpi-label">Money received</span>
            <span class="kpi-value">₨{{ money(summary.today.received_total) }}</span>
          </router-link>
        </div>
      </section>

      <section class="kpi-section">
        <h2>This month ({{ summary.month.start }} to {{ summary.month.end }})</h2>
        <div class="kpi-grid">
          <router-link to="/sales" class="kpi-card">
            <span class="kpi-label">Sales total</span>
            <span class="kpi-value">₨{{ money(summary.month.sales_total) }}</span>
            <span class="kpi-detail">{{ summary.month.sales_count }} bills</span>
          </router-link>
          <router-link to="/payments" class="kpi-card">
            <span class="kpi-label">Money received</span>
            <span class="kpi-value">₨{{ money(summary.month.received_total) }}</span>
          </router-link>
          <router-link v-if="auth.isManager" to="/profit" class="kpi-card">
            <span class="kpi-label">Gross profit this month</span>
            <span class="kpi-value">₨{{ grossProfit === null ? '-' : money(grossProfit) }}</span>
          </router-link>
        </div>
      </section>

      <section class="kpi-section">
        <h2>Balances and stock</h2>
        <div class="kpi-grid">
          <router-link to="/customers" class="kpi-card">
            <span class="kpi-label">Customers owe us</span>
            <span class="kpi-value">₨{{ money(summary.outstanding_customer_balance) }}</span>
          </router-link>
          <router-link to="/vendors" class="kpi-card">
            <span class="kpi-label">We owe vendors</span>
            <span class="kpi-value">₨{{ money(summary.vendor_payables) }}</span>
          </router-link>
          <router-link to="/purchases?unpaid=true" class="kpi-card">
            <span class="kpi-label">Vendor bills unpaid</span>
            <span class="kpi-value">₨{{ money(summary.vendor_bills_unpaid) }}</span>
          </router-link>
          <router-link to="/raw-materials" class="kpi-card" :class="{ warn: summary.low_stock_raw_materials > 0 }">
            <span class="kpi-label">Raw materials low on stock</span>
            <span class="kpi-value">{{ summary.low_stock_raw_materials }}</span>
          </router-link>
          <router-link to="/products" class="kpi-card" :class="{ warn: summary.out_of_stock_products > 0 }">
            <span class="kpi-label">Products out of stock</span>
            <span class="kpi-value">{{ summary.out_of_stock_products }}</span>
          </router-link>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../shared/api/axios'
import { useAuthStore } from '../shared/stores/auth'

const auth = useAuthStore()

interface PeriodSummary {
  sales_total: number | string
  sales_count: number
  received_total: number | string
}

interface DashboardSummary {
  today: PeriodSummary & { date: string }
  month: PeriodSummary & { start: string; end: string }
  outstanding_customer_balance: number | string
  vendor_payables: number | string
  vendor_bills_unpaid: number | string
  low_stock_raw_materials: number
  out_of_stock_products: number
}

const summary = ref<DashboardSummary | null>(null)
const grossProfit = ref<string | null>(null)
const loading = ref(false)
const error = ref('')

function money(value: number | string): string {
  return Number(value || 0).toLocaleString('en-PK', { maximumFractionDigits: 2 })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get<DashboardSummary>('/reports/dashboard/')
    summary.value = res.data
    if (auth.isManager) {
      const profit = await api.get<{ profit_amount: string }>('/profit/summary/', {
        params: { date_from: res.data.month.start, date_to: res.data.month.end },
      })
      grossProfit.value = profit.data.profit_amount
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Could not load the dashboard.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.dashboard { padding: 0.5rem 0; }
.page-header { margin-bottom: 1.5rem; }
.page-title { font-size: 2rem; font-weight: 700; color: #111827; margin: 0; }
.subtitle { color: #64748b; margin-top: 0.25rem; }
.error-banner {
  background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5;
  border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1rem;
}
.loading { color: #64748b; padding: 2rem 0; }
.kpi-section { margin-bottom: 1.75rem; }
.kpi-section h2 { font-size: 1rem; font-weight: 600; color: #334155; margin: 0 0 0.75rem; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); gap: 1rem; }
.kpi-card {
  display: flex; flex-direction: column; gap: 0.25rem;
  background: white; border-radius: 12px; padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); border-left: 4px solid #3b82f6;
  text-decoration: none; color: inherit; transition: transform 0.15s, box-shadow 0.15s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12); }
.kpi-card.warn { border-left-color: #f59e0b; }
.kpi-label { font-size: 0.875rem; color: #64748b; font-weight: 500; }
.kpi-value { font-size: 1.6rem; font-weight: 700; color: #0f172a; }
.kpi-detail { font-size: 0.75rem; color: #64748b; }
</style>
