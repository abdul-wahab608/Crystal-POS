<template>
  <div class="reports-page">
    <div class="page-header">
      <h1>Reports</h1>
    </div>

    <!-- Tab bar -->
    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key; loadTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Shared date filters -->
    <div class="filters-row">
      <div class="filter-group">
        <label>From</label>
        <input v-model="startDate" type="date" class="filter-input" />
      </div>
      <div class="filter-group">
        <label>To</label>
        <input v-model="endDate" type="date" class="filter-input" />
      </div>
      <button @click="loadTab(activeTab)" class="btn-apply" :disabled="loading">
        {{ loading ? 'Loading…' : 'Apply' }}
      </button>
      <button @click="exportExcel" class="btn-export">Export Excel</button>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">{{ error }}</div>

    <!-- ── Customer Report ── -->
    <div v-if="activeTab === 'customer'" class="table-section">
      <h2>Sales per Customer</h2>
      <table class="report-table">
        <thead>
          <tr>
            <th>Customer</th><th>City</th><th>Sales (₨)</th><th>Total Dozens</th><th>Transactions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.customer_id">
            <td>{{ row.customer_name }}</td>
            <td>{{ row.city || '—' }}</td>
            <td>₨{{ fmt(row.total_sales) }}</td>
            <td>{{ row.total_dozens }} dz</td>
            <td>{{ row.sale_count }}</td>
          </tr>
          <tr v-if="!rows.length && !loading" class="empty-row">
            <td colspan="5">No data for selected range.</td>
          </tr>
        </tbody>
        <tfoot v-if="rows.length">
          <tr>
            <td colspan="2"><strong>Total</strong></td>
            <td><strong>₨{{ fmt(sumField('total_sales')) }}</strong></td>
            <td><strong>{{ sumField('total_dozens') }} dz</strong></td>
            <td><strong>{{ sumField('sale_count') }}</strong></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- ── Area Report ── -->
    <div v-if="activeTab === 'area'" class="table-section">
      <h2>Sales per Area / City</h2>
      <table class="report-table">
        <thead>
          <tr>
            <th>City / Area</th><th>Sales (₨)</th><th>Total Dozens</th><th>Customers</th><th>Transactions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.area">
            <td>{{ row.area }}</td>
            <td>₨{{ fmt(row.total_sales) }}</td>
            <td>{{ row.total_dozens }} dz</td>
            <td>{{ row.customer_count }}</td>
            <td>{{ row.sale_count }}</td>
          </tr>
          <tr v-if="!rows.length && !loading" class="empty-row">
            <td colspan="5">No data for selected range.</td>
          </tr>
        </tbody>
        <tfoot v-if="rows.length">
          <tr>
            <td><strong>Total</strong></td>
            <td><strong>₨{{ fmt(sumField('total_sales')) }}</strong></td>
            <td><strong>{{ sumField('total_dozens') }} dz</strong></td>
            <td></td><td></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- ── Article Report ── -->
    <div v-if="activeTab === 'article'" class="table-section">
      <h2>Sales per Article (Product)</h2>
      <table class="report-table">
        <thead>
          <tr>
            <th>Product</th><th>Unit</th><th>Sales (₨)</th><th>Total Dozens</th><th>Transactions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.product_id">
            <td>{{ row.product_name }}</td>
            <td>{{ row.unit }}</td>
            <td>₨{{ fmt(row.total_sales) }}</td>
            <td>{{ row.total_dozens }} dz</td>
            <td>{{ row.sale_count }}</td>
          </tr>
          <tr v-if="!rows.length && !loading" class="empty-row">
            <td colspan="5">No data for selected range.</td>
          </tr>
        </tbody>
        <tfoot v-if="rows.length">
          <tr>
            <td colspan="2"><strong>Total</strong></td>
            <td><strong>₨{{ fmt(sumField('total_sales')) }}</strong></td>
            <td><strong>{{ sumField('total_dozens') }} dz</strong></td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- ── Sales Summary ── -->
    <div v-if="activeTab === 'summary'" class="table-section">
      <h2>Daily Sales Summary</h2>
      <table class="report-table">
        <thead>
          <tr>
            <th>Date</th><th>Sales (₨)</th><th>Total Dozens</th><th>Transactions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="String(row.date)">
            <td>{{ row.date }}</td>
            <td>₨{{ fmt(row.total_sales) }}</td>
            <td>{{ row.total_dozens }} dz</td>
            <td>{{ row.transaction_count }}</td>
          </tr>
          <tr v-if="!rows.length && !loading" class="empty-row">
            <td colspan="4">No data for selected range.</td>
          </tr>
        </tbody>
        <tfoot v-if="rows.length">
          <tr>
            <td><strong>Total</strong></td>
            <td><strong>₨{{ fmt(sumField('total_sales')) }}</strong></td>
            <td><strong>{{ sumField('total_dozens') }} dz</strong></td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- ── Inventory ── -->
    <div v-if="activeTab === 'inventory'" class="table-section">
      <h2>Stock Levels (in Dozens)</h2>
      <table class="report-table">
        <thead>
          <tr>
            <th>Product</th><th>Size Range</th><th>Color</th><th>Stock (dozens)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in rows" :key="i">
            <td>{{ row.product__name }}</td>
            <td>{{ row.size_range__name }}</td>
            <td>{{ row.color__name }}</td>
            <td :class="row.quantity_dozens < 5 ? 'low-stock' : ''">
              {{ row.quantity_dozens }} dz
            </td>
          </tr>
          <tr v-if="!rows.length && !loading" class="empty-row">
            <td colspan="4">No inventory data.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import axios from '@/shared/api/axios'

const tabs = [
  { key: 'customer', label: 'Per Customer' },
  { key: 'area',     label: 'Per Area/City' },
  { key: 'article',  label: 'Per Article' },
  { key: 'summary',  label: 'Sales Summary' },
  { key: 'inventory',label: 'Stock Levels' },
]

const activeTab = ref('customer')
const startDate = ref('')
const endDate = ref('')
const rows = ref<any[]>([])
const loading = ref(false)
const error = ref('')

const endpointMap: Record<string, string> = {
  customer:  '/api/reports/customer-report/',
  area:      '/api/reports/area-report/',
  article:   '/api/reports/article-report/',
  summary:   '/api/reports/sales-report/',
  inventory: '/api/reports/inventory-report/',
}

async function loadTab(tab: string) {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, string> = {}
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value
    const res = await axios.get(endpointMap[tab], { params })
    rows.value = Array.isArray(res.data) ? res.data : (res.data.results ?? [])
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? e?.message ?? 'Failed to load report'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function fmt(val: number | string): string {
  return Number(val || 0).toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function sumField(field: string): number {
  return rows.value.reduce((s, r) => s + Number(r[field] || 0), 0)
}

function exportExcel() {
  if (!rows.value.length) return
  const ws = XLSX.utils.json_to_sheet(rows.value)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, activeTab.value)
  const buf = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  const date = new Date().toISOString().split('T')[0]
  saveAs(new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), `report_${activeTab.value}_${date}.xlsx`)
}

onMounted(() => loadTab(activeTab.value))
</script>

<style scoped>
.reports-page { padding: 1.5rem; background: #f8fafc; min-height: 100vh; }
.page-header h1 { font-size: 1.75rem; font-weight: 700; color: #0f172a; margin: 0 0 1.25rem; }
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
.error-banner {
  background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5;
  border-radius: 8px; padding: .75rem 1rem; margin-bottom: 1rem; font-size: .875rem;
}
.table-section { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.table-section h2 { font-size: 1.125rem; font-weight: 600; color: #0f172a; margin: 0 0 1rem; }
.report-table { width: 100%; border-collapse: collapse; font-size: .875rem; }
.report-table th {
  background: #f1f5f9; text-align: left; padding: .625rem 1rem;
  font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0;
}
.report-table td { padding: .625rem 1rem; border-bottom: 1px solid #f1f5f9; color: #1e293b; }
.report-table tbody tr:hover { background: #f8fafc; }
.report-table tfoot td {
  padding: .75rem 1rem; border-top: 2px solid #e2e8f0; background: #f8fafc;
}
.empty-row td { text-align: center; color: #94a3b8; padding: 2rem; }
.low-stock { color: #dc2626; font-weight: 600; }
</style>
