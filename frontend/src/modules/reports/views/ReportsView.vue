<template>
  <div class="reports-page">
    <div class="page-header">
      <h1>Reports</h1>
      <p class="subtitle">Quantities are shown in each product's own unit. Totals are per unit and never added across units.</p>
    </div>

    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="selectTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="filters-row">
      <div class="filter-group">
        <label for="report-from">From</label>
        <input id="report-from" v-model="startDate" type="date" class="filter-input" />
      </div>
      <div class="filter-group">
        <label for="report-to">To</label>
        <input id="report-to" v-model="endDate" type="date" class="filter-input" />
      </div>
      <div v-if="activeTab === 'customer'" class="filter-group entity-filter">
        <label for="report-customer">Customer</label>
        <SearchableSelect id="report-customer" v-model="customerId" :options="customerOptions" />
      </div>
      <div v-if="activeTab === 'article'" class="filter-group entity-filter">
        <label for="report-product">Article</label>
        <SearchableSelect id="report-product" v-model="productId" :options="productOptions" />
      </div>
      <button @click="loadTab(activeTab)" class="btn-apply" :disabled="loading">
        {{ loading ? 'Loading…' : 'Apply' }}
      </button>
      <button @click="exportExcel" class="btn-export" :disabled="!rows.length">Export Excel</button>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>

    <div class="table-section">
      <h2>{{ currentReport.title }}</h2>
      <div v-if="!rows.length && !loading" class="empty-state">No data for the selected range.</div>

      <template v-for="group in visibleGroups" :key="group.unit">
        <h3 class="unit-heading">Unit: {{ group.unit }}</h3>
        <div class="table-wrap">
          <table class="report-table">
            <thead>
              <tr>
                <th v-for="col in currentReport.columns" :key="col.key" :class="{ num: col.type !== 'text' }">{{ col.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in group.rows" :key="idx">
                <td
                  v-for="col in currentReport.columns"
                  :key="col.key"
                  :class="[{ num: col.type !== 'text' }, { 'low-stock': isLowStock(row, col.key) }]"
                >
                  {{ displayValue(row, col) }}
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td v-for="col in currentReport.columns" :key="col.key" :class="{ num: col.type !== 'text' }">
                  <strong v-if="col.key === currentReport.labelKey">Total {{ group.unit }}</strong>
                  <strong v-else-if="col.total">{{ displayValue(group.totals, col) }}</strong>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </template>
      <PaginationBar
        v-if="rows.length"
        :page="page"
        :totalPages="totalPages"
        :total="total"
        :pageSize="pageSize"
        @update:page="goTo"
        @update:pageSize="setPageSize"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import axios from '@/shared/api/axios'
import SearchableSelect from '@/shared/components/SearchableSelect.vue'
import PaginationBar from '@/shared/components/PaginationBar.vue'
import { usePagination } from '@/shared/composables/usePagination'
import { useCustomersStore } from '@/modules/customers/stores/customers'
import { useProductsStore } from '@/modules/products/stores/products'
import { formatMoney, formatQuantity, groupByUnit, sumField } from '@/shared/utils/perUnit'

type ColumnType = 'text' | 'money' | 'qty' | 'count'

interface ReportColumn {
  key: string
  label: string
  type: ColumnType
  total?: boolean
}

interface ReportConfig {
  title: string
  endpoint: string
  labelKey: string
  columns: ReportColumn[]
}

const reportConfigs: Record<string, ReportConfig> = {
  customer: {
    title: 'Sales per customer',
    endpoint: '/reports/customer-report/',
    labelKey: 'customer_name',
    columns: [
      { key: 'customer_name', label: 'Customer', type: 'text' },
      { key: 'city', label: 'City', type: 'text' },
      { key: 'unit', label: 'Unit', type: 'text' },
      { key: 'total_quantity', label: 'Quantity', type: 'qty', total: true },
      { key: 'total_sales', label: 'Sales (₨)', type: 'money', total: true },
      { key: 'sale_count', label: 'Transactions', type: 'count' },
    ],
  },
  area: {
    title: 'Sales per area / city',
    endpoint: '/reports/area-report/',
    labelKey: 'area',
    columns: [
      { key: 'area', label: 'City / Area', type: 'text' },
      { key: 'unit', label: 'Unit', type: 'text' },
      { key: 'total_quantity', label: 'Quantity', type: 'qty', total: true },
      { key: 'total_sales', label: 'Sales (₨)', type: 'money', total: true },
      { key: 'customer_count', label: 'Customers', type: 'count' },
      { key: 'sale_count', label: 'Transactions', type: 'count' },
    ],
  },
  article: {
    title: 'Sales per article',
    endpoint: '/reports/article-report/',
    labelKey: 'product_name',
    columns: [
      { key: 'product_name', label: 'Article', type: 'text' },
      { key: 'unit', label: 'Unit', type: 'text' },
      { key: 'total_quantity', label: 'Quantity', type: 'qty', total: true },
      { key: 'total_sales', label: 'Sales (₨)', type: 'money', total: true },
      { key: 'sale_count', label: 'Transactions', type: 'count' },
    ],
  },
  summary: {
    title: 'Daily sales summary',
    endpoint: '/reports/sales-report/',
    labelKey: 'date',
    columns: [
      { key: 'date', label: 'Date', type: 'text' },
      { key: 'unit', label: 'Unit', type: 'text' },
      { key: 'total_quantity', label: 'Quantity', type: 'qty', total: true },
      { key: 'total_sales', label: 'Sales (₨)', type: 'money', total: true },
      { key: 'transaction_count', label: 'Transactions', type: 'count' },
    ],
  },
  inventory: {
    title: 'Stock levels per variant',
    endpoint: '/reports/inventory-report/',
    labelKey: 'product',
    columns: [
      { key: 'product', label: 'Article', type: 'text' },
      { key: 'size_range', label: 'Size range', type: 'text' },
      { key: 'color', label: 'Color', type: 'text' },
      { key: 'unit', label: 'Unit', type: 'text' },
      { key: 'quantity', label: 'Stock', type: 'qty', total: true },
    ],
  },
}

const tabs = [
  { key: 'customer', label: 'Per customer' },
  { key: 'area', label: 'Per area / city' },
  { key: 'article', label: 'Per article' },
  { key: 'summary', label: 'Sales summary' },
  { key: 'inventory', label: 'Stock levels' },
]

const customersStore = useCustomersStore()
const productsStore = useProductsStore()

const activeTab = ref('customer')
const startDate = ref('')
const endDate = ref('')
const customerId = ref<number | string | null>('')
const productId = ref<number | string | null>('')
const rows = ref<Record<string, any>[]>([])
const loading = ref(false)
const error = ref('')

const currentReport = computed(() => reportConfigs[activeTab.value])

const customerOptions = computed(() => [
  { value: '', label: 'All customers' },
  ...customersStore.customers.map((c) => ({ value: c.id, label: c.name })),
])

const productOptions = computed(() => [
  { value: '', label: 'All articles' },
  ...productsStore.products.map((p) => ({ value: p.id, label: p.name })),
])

const groups = computed(() =>
  groupByUnit(rows.value).map((group) => {
    const totals: Record<string, number> = {}
    for (const col of currentReport.value.columns) {
      if (col.total) totals[col.key] = sumField(group.rows, col.key)
    }
    return { ...group, totals }
  }),
)

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(
  computed(() => groups.value.flatMap(group => group.rows)),
)
const pageRowSet = computed(() => new Set(pageItems.value))
const visibleGroups = computed(() =>
  groups.value
    .map(group => ({ ...group, rows: group.rows.filter(row => pageRowSet.value.has(row)) }))
    .filter(group => group.rows.length > 0),
)

function normalizeRow(tab: string, row: Record<string, any>): Record<string, any> {
  if (tab === 'inventory') {
    return {
      product: row.product__name,
      size_range: row.size_range__name ?? '',
      color: row.color__name ?? '',
      unit: row.product__unit,
      quantity: row.quantity,
    }
  }
  if (tab === 'summary') {
    return { ...row, date: String(row.date), total_sales: Number(row.total_sales), total_quantity: Number(row.total_quantity) }
  }
  return row
}

async function loadTab(tab: string) {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, string> = {}
    if (tab !== 'inventory') {
      if (startDate.value) params.start_date = startDate.value
      if (endDate.value) params.end_date = endDate.value
    }
    if (tab === 'customer' && customerId.value) params.customer = String(customerId.value)
    if (tab === 'article' && productId.value) params.product = String(productId.value)
    const res = await axios.get(reportConfigs[tab].endpoint, { params })
    const data = Array.isArray(res.data) ? res.data : (res.data.results ?? [])
    rows.value = data.map((row: Record<string, any>) => normalizeRow(tab, row))
    reset()
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? e?.message ?? 'Failed to load report'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function selectTab(tab: string) {
  activeTab.value = tab
  loadTab(tab)
}

function isLowStock(row: Record<string, any>, key: string) {
  return activeTab.value === 'inventory' && key === 'quantity' && Number(row.quantity) < 5
}

function displayValue(row: Record<string, any>, col: ReportColumn): string {
  const value = row[col.key]
  if (value === undefined || value === null || value === '') return col.type === 'text' ? '—' : ''
  if (col.type === 'money') return formatMoney(value)
  if (col.type === 'qty') return formatQuantity(value)
  if (col.type === 'count') return String(value)
  return String(value)
}

function exportExcel() {
  if (!rows.value.length) return
  const config = currentReport.value
  const exportRows: Record<string, string | number>[] = []
  for (const group of groups.value) {
    for (const row of group.rows) {
      exportRows.push(Object.fromEntries(config.columns.map((col) => [col.label, exportValue(row[col.key], col)])))
    }
    exportRows.push(Object.fromEntries(config.columns.map((col, idx) => {
      if (idx === 0) return [col.label, `Total ${group.unit}`]
      if (col.total) return [col.label, Number(group.totals[col.key].toFixed(2))]
      return [col.label, '']
    })))
    exportRows.push({})
  }
  const ws = XLSX.utils.json_to_sheet(exportRows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, activeTab.value)
  const buf = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  const date = new Date().toISOString().split('T')[0]
  saveAs(new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), `report_${activeTab.value}_${date}.xlsx`)
}

function exportValue(value: unknown, col: ReportColumn): string | number {
  if (value === undefined || value === null) return ''
  if (col.type === 'money' || col.type === 'qty' || col.type === 'count') return Number(value)
  return String(value)
}

onMounted(async () => {
  await Promise.all([customersStore.fetchCustomers(), productsStore.fetchProducts()])
  await loadTab(activeTab.value)
})
</script>

<style scoped>
.reports-page { padding: 1.5rem; background: #f8fafc; min-height: 100vh; }
.page-header h1 { font-size: 1.75rem; font-weight: 700; color: #0f172a; margin: 0; }
.subtitle { color: #64748b; margin: .25rem 0 1.25rem; font-size: .875rem; }
.tab-bar { display: flex; gap: .5rem; flex-wrap: wrap; margin-bottom: 1rem; }
.tab-btn {
  padding: .5rem 1.25rem; border: 2px solid #e2e8f0; border-radius: 8px;
  background: white; font-weight: 600; cursor: pointer; font-size: .875rem; color: #475569;
  transition: all .15s;
}
.tab-btn.active { border-color: #3b82f6; background: #eff6ff; color: #1d4ed8; }
.tab-btn:hover:not(.active) { border-color: #94a3b8; }
.filters-row { display: flex; align-items: flex-end; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.filter-group { display: flex; flex-direction: column; gap: .25rem; }
.filter-group label { font-size: .75rem; font-weight: 600; color: #64748b; }
.entity-filter { min-width: 220px; }
.filter-input {
  padding: .5rem .75rem; border: 2px solid #e2e8f0; border-radius: 8px;
  font-size: .875rem; background: white;
}
.filter-input:focus { outline: none; border-color: #3b82f6; }
.btn-apply {
  padding: .5rem 1.25rem; background: #3b82f6; color: white; border: none;
  border-radius: 8px; font-weight: 600; cursor: pointer;
}
.btn-apply:disabled { background: #93c5fd; cursor: not-allowed; }
.btn-export {
  padding: .5rem 1.25rem; background: #22c55e; color: white; border: none;
  border-radius: 8px; font-weight: 600; cursor: pointer; margin-left: auto;
}
.btn-export:disabled { background: #86efac; cursor: not-allowed; }
.error-banner {
  background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5;
  border-radius: 8px; padding: .75rem 1rem; margin-bottom: 1rem; font-size: .875rem;
}
.table-section { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.table-section h2 { font-size: 1.125rem; font-weight: 600; color: #0f172a; margin: 0 0 1rem; }
.unit-heading { font-size: .95rem; font-weight: 700; color: #1d4ed8; margin: 1.25rem 0 .5rem; }
.table-wrap { overflow-x: auto; }
.report-table { width: 100%; border-collapse: collapse; font-size: .875rem; }
.report-table th {
  background: #f1f5f9; text-align: left; padding: .625rem 1rem;
  font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; white-space: nowrap;
}
.report-table td { padding: .625rem 1rem; border-bottom: 1px solid #f1f5f9; color: #1e293b; }
.report-table tbody tr:hover { background: #f8fafc; }
.report-table tfoot td { padding: .75rem 1rem; border-top: 2px solid #e2e8f0; background: #f8fafc; }
.num { text-align: right; }
.empty-state { text-align: center; color: #94a3b8; padding: 2rem; }
.low-stock { color: #dc2626; font-weight: 600; }
</style>
