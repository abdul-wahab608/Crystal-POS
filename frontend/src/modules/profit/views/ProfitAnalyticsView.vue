<template>
  <div class="profit-analytics-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Profit Analytics</h1>
        <p class="subtitle">Profit per piece and per dozen, filterable by article, month, season, year and location.</p>
      </div>
      <router-link to="/profit/costs" class="btn-secondary">Manage Costs</router-link>
    </div>

    <div class="filters-panel">
      <div class="filters-grid">
        <div class="filter-group">
          <label>Article</label>
          <select v-model="filters.product" class="filter-select">
            <option value="">All Articles</option>
            <option v-for="p in productsStore.products" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Location</label>
          <select v-model="filters.city" class="filter-select">
            <option value="">All Locations</option>
            <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Year</label>
          <select v-model="filters.year" class="filter-select">
            <option value="">All Years</option>
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Month</label>
          <select v-model="filters.month" class="filter-select">
            <option value="">All Months</option>
            <option v-for="(m, idx) in monthNames" :key="idx" :value="idx + 1">{{ m }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Season</label>
          <select v-model="filters.season" class="filter-select">
            <option value="">All Seasons</option>
            <option v-for="s in seasons" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Unit</label>
          <select v-model="unit" class="filter-select">
            <option value="dozen">Per Dozen</option>
            <option value="piece">Per Piece</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Trend / Breakdown By</label>
          <select v-model="trendX" class="filter-select">
            <option value="month">Month</option>
            <option value="season">Season</option>
            <option value="year">Year</option>
            <option value="location">Location</option>
            <option value="product">Article</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Split Chart Lines By</label>
          <select v-model="trendSeries" class="filter-select">
            <option value="">Single line</option>
            <option value="product">Article</option>
            <option value="location">Location</option>
          </select>
        </div>
        <div class="filter-group">
          <button class="reset-btn" @click="resetFilters">Reset Filters</button>
        </div>
      </div>
    </div>

    <div v-if="profitStore.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Crunching the numbers...</p>
    </div>

    <div v-else class="analytics-content">
      <div class="kpi-row" v-if="profitStore.summaryTotals">
        <div class="kpi-card revenue">
          <div class="kpi-label">Revenue</div>
          <div class="kpi-value">₨{{ formatMoney(profitStore.summaryTotals.revenue) }}</div>
        </div>
        <div class="kpi-card expense">
          <div class="kpi-label">Cost</div>
          <div class="kpi-value">₨{{ formatMoney(profitStore.summaryTotals.cost) }}</div>
        </div>
        <div class="kpi-card profit">
          <div class="kpi-label">Profit</div>
          <div class="kpi-value">₨{{ formatMoney(profitStore.summaryTotals.profit_amount) }}</div>
          <div class="kpi-detail" :class="Number(profitStore.summaryTotals.profit_ratio) >= 0 ? 'positive' : 'negative'">
            {{ (Number(profitStore.summaryTotals.profit_ratio) * 100).toFixed(1) }}% margin
          </div>
        </div>
        <div class="kpi-card info">
          <div class="kpi-label">Profit / {{ unit === 'piece' ? 'Piece' : 'Dozen' }}</div>
          <div class="kpi-value">₨{{ formatMoney(profitStore.summaryTotals.profit_per_unit) }}</div>
          <div class="kpi-detail">{{ formatMoney(profitStore.summaryTotals.quantity) }} {{ unit === 'piece' ? 'pcs' : 'dz' }} sold</div>
        </div>
      </div>

      <div class="chart-card">
        <h3>Profit Trend by {{ trendXLabel }}</h3>
        <apexchart v-if="profitStore.trend.categories.length" type="line" height="350" :options="chartOptions" :series="profitStore.trend.series" />
        <p v-else class="empty-row">No sales match these filters.</p>
      </div>

      <div class="table-card">
        <h3>Breakdown by {{ trendXLabel }}</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ trendXLabel }}</th>
              <th>Qty ({{ unit }})</th>
              <th>Revenue</th>
              <th>Cost</th>
              <th>Profit</th>
              <th>Margin</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in profitStore.summaryRows" :key="row.key">
              <td>{{ row.label }}</td>
              <td>{{ formatMoney(row.quantity) }}</td>
              <td>₨{{ formatMoney(row.revenue) }}</td>
              <td>₨{{ formatMoney(row.cost) }}</td>
              <td>₨{{ formatMoney(row.profit_amount) }}</td>
              <td>{{ (Number(row.profit_ratio) * 100).toFixed(1) }}%</td>
            </tr>
            <tr v-if="profitStore.summaryRows.length === 0">
              <td colspan="6" class="empty-row">No sales match these filters.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useProfitStore } from '../stores/profit'
import { useProductsStore } from '../../products/stores/products'
import { useCustomersStore } from '../../customers/stores/customers'
import type { ProfitGroupBy, ProfitUnit } from '../types'

const profitStore = useProfitStore()
const productsStore = useProductsStore()
const customersStore = useCustomersStore()

const filters = ref<{ product: number | ''; city: string; year: number | ''; month: number | ''; season: string }>({
  product: '',
  city: '',
  year: '',
  month: '',
  season: '',
})
const unit = ref<ProfitUnit>('dozen')
const trendX = ref<ProfitGroupBy>('month')
const trendSeries = ref<ProfitGroupBy | ''>('')

const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

const years = computed(() => {
  const current = new Date().getFullYear()
  return Array.from({ length: 6 }, (_, i) => current - i)
})

const cities = computed(() => {
  const set = new Set<string>()
  customersStore.customers.forEach((c) => {
    if (c.city) set.add(c.city)
  })
  return Array.from(set).sort()
})

const trendXLabel = computed(() => {
  const labels: Record<string, string> = { month: 'Month', season: 'Season', year: 'Year', location: 'Location', product: 'Article' }
  return labels[trendX.value] || trendX.value
})

function formatMoney(value: number | string) {
  return Number(value).toLocaleString('en-PK', { maximumFractionDigits: 2 })
}

function activeFilters() {
  const f: Record<string, any> = { unit: unit.value }
  if (filters.value.product) f.product = filters.value.product
  if (filters.value.city) f.city = filters.value.city
  if (filters.value.year) f.year = filters.value.year
  if (filters.value.month) f.month = filters.value.month
  if (filters.value.season) f.season = filters.value.season
  return f
}

async function refresh() {
  const f = activeFilters()
  await Promise.all([
    profitStore.fetchSummary(f),
    profitStore.fetchSummary(f, trendX.value),
    profitStore.fetchTrend(f, trendX.value, trendSeries.value || undefined, 'profit_amount'),
  ])
}

const chartOptions = computed(() => ({
  chart: { type: 'line', height: 350, toolbar: { show: true }, zoom: { enabled: true } },
  stroke: { curve: 'smooth', width: 3 },
  dataLabels: { enabled: false },
  xaxis: { categories: profitStore.trend.categories },
  yaxis: { title: { text: 'Profit (₨)' } },
  legend: { position: 'top' },
  colors: ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'],
  tooltip: { y: { formatter: (val: number) => `₨${val.toLocaleString('en-PK')}` } },
}))

function resetFilters() {
  filters.value = { product: '', city: '', year: '', month: '', season: '' }
  unit.value = 'dozen'
  trendX.value = 'month'
  trendSeries.value = ''
}

watch([filters, unit, trendX, trendSeries], refresh, { deep: true })

onMounted(async () => {
  await Promise.all([productsStore.fetchProducts(), customersStore.fetchCustomers()])
  await refresh()
})
</script>

<style scoped>
.profit-analytics-page {
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #111827;
  margin: 0;
}

.subtitle {
  color: #64748b;
  margin-top: 0.25rem;
}

.btn-secondary {
  background: #6b7280;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
}

.filters-panel {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3b82f6;
  margin-bottom: 1.5rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr));
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
}

.filter-select {
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  background: white;
}

.reset-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #64748b;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.analytics-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
  gap: 1rem;
}

.kpi-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.kpi-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.kpi-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0.25rem 0;
}

.kpi-detail {
  font-size: 0.75rem;
  color: #64748b;
}

.kpi-detail.positive {
  color: #16a34a;
  font-weight: 600;
}

.kpi-detail.negative {
  color: #dc2626;
  font-weight: 600;
}

.chart-card,
.table-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-card h3,
.table-card h3 {
  margin: 0 0 1rem 0;
  color: #0f172a;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
}

.empty-row {
  text-align: center;
  color: #94a3b8;
  padding: 2rem !important;
}

@media (max-width: 768px) {
  .profit-analytics-page {
    padding: 1rem;
  }
}
</style>
