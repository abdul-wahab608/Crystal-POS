<template>
  <div class="profit-analytics-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Profit</h1>
        <p class="subtitle">Revenue, cost and profit from sales. Quantities are shown in each article's own unit.</p>
      </div>
      <router-link to="/profit/costs" class="btn-secondary">Manage Costs</router-link>
    </div>

    <div class="filters-panel">
      <div class="filters-grid">
        <div class="filter-group">
          <label for="profit-article">Article</label>
          <SearchableSelect id="profit-article" v-model="filters.product" :options="productOptions" />
        </div>
        <div class="filter-group">
          <label for="profit-size">Size range</label>
          <SearchableSelect id="profit-size" v-model="filters.size_range" :options="sizeOptions" />
        </div>
        <div class="filter-group">
          <label for="profit-color">Color</label>
          <SearchableSelect id="profit-color" v-model="filters.color" :options="colorOptions" />
        </div>
        <div class="filter-group">
          <label for="profit-city">City</label>
          <SearchableSelect id="profit-city" v-model="filters.city" :options="cityOptions" />
        </div>
        <div class="filter-group">
          <label for="profit-from">From</label>
          <input id="profit-from" v-model="filters.date_from" type="date" class="filter-input" />
        </div>
        <div class="filter-group">
          <label for="profit-to">To</label>
          <input id="profit-to" v-model="filters.date_to" type="date" class="filter-input" />
        </div>
        <div class="filter-group">
          <label for="profit-year">Year</label>
          <select id="profit-year" v-model="filters.year" class="filter-select">
            <option value="">All years</option>
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="profit-month">Month</label>
          <select id="profit-month" v-model="filters.month" class="filter-select">
            <option value="">All months</option>
            <option v-for="(m, idx) in monthNames" :key="m" :value="idx + 1">{{ m }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="profit-season">Season</label>
          <select id="profit-season" v-model="filters.season" class="filter-select">
            <option value="">All seasons</option>
            <option v-for="s in seasons" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="profit-breakdown">Breakdown by</label>
          <select id="profit-breakdown" v-model="breakdownBy" class="filter-select">
            <option v-for="opt in groupOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="profit-metric">Chart shows</label>
          <select id="profit-metric" v-model="chartMetric" class="filter-select">
            <option value="profit_amount">Profit</option>
            <option value="revenue">Revenue</option>
            <option value="quantity">Quantity (per unit)</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="profit-series">Chart lines</label>
          <select id="profit-series" v-model="chartSeries" class="filter-select">
            <option value="">One line</option>
            <option value="product">Per article</option>
            <option value="location">Per city</option>
            <option value="unit">Per unit</option>
          </select>
        </div>
        <div class="filter-group">
          <button class="reset-btn" @click="resetFilters">Reset filters</button>
        </div>
      </div>
    </div>

    <p v-if="!auth.isManager" class="form-error">Profit is available to managers only.</p>

    <div v-if="auth.isManager && profitStore.loading && !profitStore.summaryTotals" class="loading-state">
      <div class="spinner"></div>
      <p>Loading profit...</p>
    </div>

    <div v-else-if="auth.isManager && profitStore.summaryTotals" class="analytics-content">
      <div class="kpi-row">
        <div class="kpi-card revenue">
          <div class="kpi-label">Revenue</div>
          <div class="kpi-value">₨{{ formatMoney(profitStore.summaryTotals.revenue) }}</div>
        </div>
        <div class="kpi-card expense">
          <div class="kpi-label">Cost</div>
          <div v-if="profitStore.summaryTotals.cost_missing" class="kpi-detail negative">{{ COST_MISSING_MESSAGE }}</div>
          <div v-else class="kpi-value">₨{{ formatMoney(profitStore.summaryTotals.cost) }}</div>
          <div class="kpi-detail">{{ costSourceLabel(profitStore.summaryTotals.cost_source) }}</div>
        </div>
        <div class="kpi-card profit">
          <div class="kpi-label">Profit</div>
          <template v-if="!profitStore.summaryTotals.cost_missing">
            <div class="kpi-value">₨{{ formatMoney(profitStore.summaryTotals.profit_amount) }}</div>
            <div class="kpi-detail" :class="Number(profitStore.summaryTotals.profit_ratio) >= 0 ? 'positive' : 'negative'">
              {{ (Number(profitStore.summaryTotals.profit_ratio) * 100).toFixed(1) }}% margin
            </div>
          </template>
          <div v-else class="kpi-detail">Not shown until cost is known</div>
        </div>
        <div class="kpi-card info">
          <div class="kpi-label">Quantity sold</div>
          <div v-if="profitStore.summaryTotals.quantities.length" class="qty-lines">
            <div v-for="line in quantityLines(profitStore.summaryTotals.quantities)" :key="line">{{ line }}</div>
          </div>
          <div v-else class="kpi-detail">Nothing sold</div>
        </div>
      </div>

      <div class="chart-card">
        <h3>{{ chartTitle }}</h3>
        <apexchart
          v-if="profitStore.trend.categories.length"
          type="line"
          height="350"
          :options="chartOptions"
          :series="profitStore.trend.series"
        />
        <p v-else class="empty-row">No sales match these filters.</p>
        <p v-if="trendHasMissingCost" class="form-hint">Points with a missing cost are left blank rather than shown as zero profit.</p>
      </div>

      <div class="table-card">
        <h3>Breakdown by {{ breakdownLabel }}</h3>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>{{ breakdownLabel }}</th>
                <th>Quantity</th>
                <th>Revenue</th>
                <th>Cost</th>
                <th>Cost source</th>
                <th>Profit</th>
                <th>Margin</th>
                <th>Profit per unit</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in pageItems" :key="row.key">
                <td>{{ row.label }}</td>
                <td>
                  <div v-for="line in quantityLines(row.quantities)" :key="line">{{ line }}</div>
                </td>
                <td>₨{{ formatMoney(row.revenue) }}</td>
                <td v-if="row.cost_missing" class="muted">{{ COST_MISSING_MESSAGE }}</td>
                <td v-else>₨{{ formatMoney(row.cost) }}</td>
                <td>{{ costSourceLabel(row.cost_source) }}</td>
                <td v-if="row.cost_missing" class="muted">—</td>
                <td v-else>₨{{ formatMoney(row.profit_amount) }}</td>
                <td v-if="row.cost_missing" class="muted">—</td>
                <td v-else>{{ (Number(row.profit_ratio) * 100).toFixed(1) }}%</td>
                <td>
                  <span v-if="row.cost_missing" class="muted">—</span>
                  <span v-else-if="row.profit_per_unit !== null && row.unit">₨{{ formatMoney(row.profit_per_unit) }} / {{ row.unit }}</span>
                  <span v-else class="muted">Mixed units</span>
                </td>
              </tr>
              <tr v-if="profitStore.summaryRows.length === 0">
                <td colspan="8" class="empty-row">No sales match these filters.</td>
              </tr>
            </tbody>
          </table>
          <PaginationBar
            v-if="profitStore.summaryRows.length"
            :page="page"
            :totalPages="totalPages"
            :total="total"
            :pageSize="pageSize"
            @update:page="goTo"
            @update:pageSize="setPageSize"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Apexchart from 'vue3-apexcharts'
import type { ApexOptions } from 'apexcharts'
import { ref, computed, watch, onMounted } from 'vue'
import { useProfitStore } from '../stores/profit'
import { useProductsStore } from '../../products/stores/products'
import { useCustomersStore } from '../../customers/stores/customers'
import { useColorStore } from '../../products/stores/color'
import { useSizeRangeStore } from '../../products/stores/sizeRange'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import { useAuthStore } from '../../../shared/stores/auth'
import { formatMoney, formatQuantityLines, type UnitQuantity } from '../../../shared/utils/perUnit'
import type { ProfitFilters, ProfitGroupBy, ProfitMetric } from '../types'
import { COST_MISSING_MESSAGE, costSourceLabel } from '../utils/costSource'

const profitStore = useProfitStore()
const auth = useAuthStore()
const productsStore = useProductsStore()
const customersStore = useCustomersStore()
const colorStore = useColorStore()
const sizeRangeStore = useSizeRangeStore()

const filters = ref<{
  product: number | string | null
  size_range: number | string | null
  color: number | string | null
  city: string | null
  date_from: string
  date_to: string
  year: number | ''
  month: number | ''
  season: string
}>({
  product: '',
  size_range: '',
  color: '',
  city: '',
  date_from: '',
  date_to: '',
  year: '',
  month: '',
  season: '',
})
const breakdownBy = ref<ProfitGroupBy>('product')
const chartMetric = ref<ProfitMetric>('profit_amount')
const chartSeries = ref<ProfitGroupBy | ''>('')

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(computed(() => profitStore.summaryRows))

const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

const groupOptions: { value: ProfitGroupBy; label: string }[] = [
  { value: 'product', label: 'Article' },
  { value: 'month', label: 'Month' },
  { value: 'season', label: 'Season' },
  { value: 'year', label: 'Year' },
  { value: 'location', label: 'City' },
  { value: 'unit', label: 'Unit' },
]

const years = computed(() => {
  const current = new Date().getFullYear()
  return Array.from({ length: 6 }, (_, i) => current - i)
})

const productOptions = computed(() => [
  { value: '', label: 'All articles' },
  ...productsStore.products.map((p) => ({ value: p.id, label: p.name })),
])

const sizeOptions = computed(() => [
  { value: '', label: 'All sizes' },
  ...sizeRangeStore.sizeRanges.map((s) => ({ value: s.id, label: s.name })),
])

const colorOptions = computed(() => [
  { value: '', label: 'All colors' },
  ...colorStore.colors.map((c) => ({ value: c.id, label: c.name })),
])

const cityOptions = computed(() => {
  const set = new Set<string>()
  customersStore.customers.forEach((c) => {
    if (c.city) set.add(c.city)
  })
  return [
    { value: '', label: 'All cities' },
    ...Array.from(set).sort().map((city) => ({ value: city, label: city })),
  ]
})

const breakdownLabel = computed(() => groupOptions.find((o) => o.value === breakdownBy.value)?.label ?? '')

const chartTitle = computed(() => {
  const metric = { profit_amount: 'Profit', revenue: 'Revenue', quantity: 'Quantity' }[chartMetric.value]
  return `${metric} by ${breakdownLabel.value.toLowerCase()}`
})

const trendHasMissingCost = computed(() =>
  profitStore.trend.series.some((s) => s.cost_missing.some(Boolean)),
)

function quantityLines(quantities: UnitQuantity[]) {
  return formatQuantityLines(quantities)
}

function activeFilters(): ProfitFilters {
  const f: ProfitFilters = {}
  if (filters.value.product) f.product = filters.value.product
  if (filters.value.size_range) f.size_range = filters.value.size_range
  if (filters.value.color) f.color = filters.value.color
  if (filters.value.city) f.city = filters.value.city
  if (filters.value.date_from) f.date_from = filters.value.date_from
  if (filters.value.date_to) f.date_to = filters.value.date_to
  if (filters.value.year) f.year = filters.value.year
  if (filters.value.month) f.month = filters.value.month
  if (filters.value.season) f.season = filters.value.season
  return f
}

async function refresh() {
  if (!auth.isManager) return
  const f = activeFilters()
  await Promise.all([
    profitStore.fetchSummary(f),
    profitStore.fetchSummary(f, breakdownBy.value),
    profitStore.fetchTrend(f, breakdownBy.value, chartSeries.value || undefined, chartMetric.value),
  ])
}

const chartOptions = computed<ApexOptions>(() => ({
  chart: { type: 'line', height: 350, toolbar: { show: true }, zoom: { enabled: true } },
  stroke: { curve: 'smooth', width: 3 },
  dataLabels: { enabled: false },
  xaxis: { categories: profitStore.trend.categories },
  yaxis: { title: { text: chartMetric.value === 'quantity' ? 'Quantity' : chartMetric.value === 'revenue' ? 'Revenue (₨)' : 'Profit (₨)' } },
  legend: { position: 'top', show: profitStore.trend.series.length > 1 },
  colors: ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'],
  tooltip: { y: { formatter: (val: number) => (chartMetric.value === 'quantity' ? String(val) : `₨${val.toLocaleString('en-PK')}`) } },
}))

function resetFilters() {
  filters.value = { product: '', size_range: '', color: '', city: '', date_from: '', date_to: '', year: '', month: '', season: '' }
  breakdownBy.value = 'product'
  chartMetric.value = 'profit_amount'
  chartSeries.value = ''
}

watch([filters, breakdownBy, chartMetric, chartSeries], refresh, { deep: true })
watch([filters, breakdownBy], reset, { deep: true })

onMounted(async () => {
  if (!auth.isManager) return
  await Promise.all([
    productsStore.fetchProducts(),
    customersStore.fetchCustomers(),
    colorStore.fetchColors(),
    sizeRangeStore.fetchSizeRanges(),
  ])
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
  border-radius: 0.375rem;
  font-weight: 500;
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

.filter-select,
.filter-input {
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

.qty-lines {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin-top: 0.25rem;
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

.table-wrap {
  overflow-x: auto;
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
  vertical-align: top;
}

.empty-row {
  text-align: center;
  color: #94a3b8;
  padding: 2rem !important;
}

.muted {
  color: #94a3b8;
}

@media (max-width: 768px) {
  .profit-analytics-page {
    padding: 1rem;
  }
}
</style>
