<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProductsStore } from '../modules/products/stores/products'
import { useCustomersStore } from '../modules/customers/stores/customers'
import { useVendorsStore } from '../modules/vendors/stores/vendors'
import { useSalesStore } from '../modules/sales/stores/sales'
import { usePurchasesStore } from '../modules/purchases/stores/purchases'
import { usePaymentsStore} from '../modules/payments/stores/payments'
import { useRawMaterialsStore } from '../modules/raw_materials/stores/raw_materials'

const productsStore = useProductsStore()
const customersStore = useCustomersStore()
const vendorsStore = useVendorsStore()
const salesStore = useSalesStore()
const purchasesStore = usePurchasesStore()
const paymentsStore = usePaymentsStore()
const rawMaterialsStore = useRawMaterialsStore()

const loading = ref(true)
const activeTab = ref('overview')

// FILTERS
const dateFilter = ref('all')
const customStartDate = ref('')
const customEndDate = ref('')
const selectedCustomer = ref<number | 'all'>('all')
const selectedVendor = ref<number | 'all'>('all')
const selectedProduct = ref<number | 'all'>('all')

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      productsStore.fetchProducts().catch(() => {}),
      customersStore.fetchCustomers().catch(() => {}),
      vendorsStore.fetchVendors().catch(() => {}),
      salesStore.fetchSales().catch(() => {}),
      purchasesStore.fetchPurchases().catch(() => {}),
      paymentsStore.fetchPayments().catch(() => {}),
      rawMaterialsStore.fetchMaterials().catch(() => {})
    ])
  } finally {
    loading.value = false
  }
})

// DATE FILTERING
const filterByDate = (dateStr: string | undefined) => {
  if (!dateStr) return false
  const itemDate = new Date(dateStr)
  const now = new Date()
  
  switch (dateFilter.value) {
    case 'today':
      return itemDate.toDateString() === now.toDateString()
    case 'week':
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      return itemDate >= weekAgo
    case 'month':
      return itemDate.getMonth() === now.getMonth() && itemDate.getFullYear() === now.getFullYear()
    case 'year':
      return itemDate.getFullYear() === now.getFullYear()
    case 'custom':
      if (!customStartDate.value || !customEndDate.value) return true
      return itemDate >= new Date(customStartDate.value) && itemDate <= new Date(customEndDate.value)
    default:
      return true
  }
}

// FILTERED DATA
const filteredSales = computed(() => {
  return (salesStore.sales || []).filter(sale => {
    const dateMatch = filterByDate(sale.date)
    const customerMatch = selectedCustomer.value === 'all' || sale.customer === selectedCustomer.value
    let productMatch = true
    if (selectedProduct.value !== 'all') {
      productMatch = (sale.sale_items || []).some((item: any) => item.product === selectedProduct.value)
    }
    return dateMatch && customerMatch && productMatch
  })
})

const filteredPurchases = computed(() => {
  return (purchasesStore.purchases || []).filter(purchase => {
    const dateMatch = filterByDate(purchase.date)
    const vendorMatch = selectedVendor.value === 'all' || purchase.vendor === selectedVendor.value
    return dateMatch && vendorMatch
  })
})

// METRICS BASED ON FILTERS
const totalSales = computed(() => filteredSales.value.reduce((sum, s) => sum + Number(s.total_amount || 0), 0))
const totalPurchases = computed(() => filteredPurchases.value.reduce((sum, p) => sum + Number(p.total_amount || 0), 0))
const grossProfit = computed(() => totalSales.value - totalPurchases.value)
const profitMargin = computed(() => totalSales.value > 0 ? ((grossProfit.value / totalSales.value) * 100).toFixed(1) : '0.0')

// CHARTS DATA - Sales Trend
const salesTrendData = computed(() => {
  const dataMap: Record<string, number> = {}
  
  filteredSales.value.forEach(sale => {
    if (!sale.date) return
    const date = new Date(sale.date)
    let key = ''
    
    if (dateFilter.value === 'year' || dateFilter.value === 'all') {
      key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    } else {
      key = date.toISOString().split('T')[0]
    }
    
    dataMap[key] = (dataMap[key] || 0) + Number(sale.total_amount || 0)
  })
  
  const sorted = Object.entries(dataMap).sort((a, b) => a[0].localeCompare(b[0]))
  return {
    categories: sorted.map(([date]) => date),
    data: sorted.map(([, amount]) => Math.round(amount))
  }
})

const salesTrendOptions = computed(() => ({
  chart: { type: 'area', height: 350, toolbar: { show: true }, zoom: { enabled: true } },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3 },
  xaxis: { categories: salesTrendData.value.categories, title: { text: 'Date' } },
  yaxis: {
    title: { text: 'Sales (₨)' },
    labels: {
      formatter: (val: number) => {
        if (val >= 1000000) return `₨${(val / 1000000).toFixed(1)}M`
        if (val >= 1000) return `₨${(val / 1000).toFixed(1)}K`
        return `₨${val}`
      }
    }
  },
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.3 } },
  colors: ['#22c55e'],
  tooltip: { y: { formatter: (val: number) => `₨${val.toLocaleString('en-PK')}` } }
}))

// Customer Sales Distribution
const customerSalesData = computed(() => {
  const customerMap: Record<number, { name: string; amount: number }> = {}
  
  filteredSales.value.forEach(sale => {
    if (customerMap[sale.customer]) {
      customerMap[sale.customer].amount += Number(sale.total_amount || 0)
    } else {
      customerMap[sale.customer] = {
        name: sale.customer_name || 'Unknown',
        amount: Number(sale.total_amount || 0)
      }
    }
  })
  
  const sorted = Object.values(customerMap).sort((a, b) => b.amount - a.amount).slice(0, 10)
  return {
    categories: sorted.map(c => c.name),
    data: sorted.map(c => Math.round(c.amount))
  }
})

const customerSalesOptions = computed(() => ({
  chart: { type: 'bar', height: 350, toolbar: { show: true } },
  plotOptions: { bar: { horizontal: true, borderRadius: 4 } },
  dataLabels: { enabled: false },
  xaxis: {
    categories: customerSalesData.value.categories,
    labels: {
      formatter: (val: number) => {
        if (val >= 1000000) return `₨${(val / 1000000).toFixed(1)}M`
        if (val >= 1000) return `₨${(val / 1000).toFixed(1)}K`
        return `₨${val}`
      }
    }
  },
  colors: ['#3b82f6'],
  tooltip: { y: { formatter: (val: number) => `₨${val.toLocaleString('en-PK')}` } }
}))

// Product Sales Distribution
const productSalesData = computed(() => {
  const productMap: Record<number, { name: string; quantity: number; revenue: number }> = {}
  
  filteredSales.value.forEach(sale => {
    (sale.sale_items || []).forEach((item: any) => {
      if (productMap[item.product]) {
        productMap[item.product].quantity += Number(item.quantity || 0)
        productMap[item.product].revenue += Number(item.quantity || 0) * Number(item.unit_price || 0)
      } else {
        productMap[item.product] = {
          name: item.product_name || 'Unknown',
          quantity: Number(item.quantity || 0),
          revenue: Number(item.quantity || 0) * Number(item.unit_price || 0)
        }
      }
    })
  })
  
  const sorted = Object.values(productMap).sort((a, b) => b.revenue - a.revenue).slice(0, 10)
  return {
    labels: sorted.map(p => p.name),
    series: sorted.map(p => Math.round(p.revenue))
  }
})

const productSalesOptions = computed(() => ({
  chart: { type: 'donut', height: 350 },
  labels: productSalesData.value.labels,
  colors: ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16'],
  legend: { position: 'bottom' },
  plotOptions: {
    pie: {
      donut: {
        size: '70%',
        labels: {
          show: true,
          total: { show: true, label: 'Total Revenue' }
        }
      }
    }
  },
  tooltip: { y: { formatter: (val: number) => `₨${val.toLocaleString('en-PK')}` } }
}))

// Vendor Purchases Distribution
const vendorPurchasesData = computed(() => {
  const vendorMap: Record<number, { name: string; amount: number }> = {}
  
  filteredPurchases.value.forEach(purchase => {
    if (vendorMap[purchase.vendor]) {
      vendorMap[purchase.vendor].amount += Number(purchase.total_amount || 0)
    } else {
      vendorMap[purchase.vendor] = {
        name: purchase.vendor_name || 'Unknown',
        amount: Number(purchase.total_amount || 0)
      }
    }
  })
  
  const sorted = Object.values(vendorMap).sort((a, b) => b.amount - a.amount).slice(0, 10)
  return {
    categories: sorted.map(v => v.name),
    data: sorted.map(v => Math.round(v.amount))
  }
})

const vendorPurchasesOptions = computed(() => ({
  chart: { type: 'bar', height: 350, toolbar: { show: true } },
  plotOptions: { bar: { horizontal: true, borderRadius: 4 } },
  dataLabels: { enabled: false },
  xaxis: {
    categories: vendorPurchasesData.value.categories,
    labels: {
      formatter: (val: number) => {
        if (val >= 1000000) return `₨${(val / 1000000).toFixed(1)}M`
        if (val >= 1000) return `₨${(val / 1000).toFixed(1)}K`
        return `₨${val}`
      }
    }
  },
  colors: ['#f59e0b'],
  tooltip: { y: { formatter: (val: number) => `₨${val.toLocaleString('en-PK')}` } }
}))

// Payment Methods Distribution
const paymentMethodsData = computed(() => {
  const methodMap: Record<string, number> = {}
  
  const allPayments = paymentsStore.payments || []
  allPayments.forEach(payment => {
    const method = payment.payment_method || 'Unknown'
    methodMap[method] = (methodMap[method] || 0) + Number(payment.amount || 0)
  })
  
  return {
    labels: Object.keys(methodMap),
    series: Object.values(methodMap).map(v => Math.round(v))
  }
})

const paymentMethodsOptions = computed(() => ({
  chart: { type: 'pie', height: 350 },
  labels: paymentMethodsData.value.labels,
  colors: ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'],
  legend: { position: 'bottom' },
  tooltip: { y: { formatter: (val: number) => `₨${val.toLocaleString('en-PK')}` } }
}))

// Sales vs Purchases Comparison
const salesVsPurchasesData = computed(() => {
  const dataMap: Record<string, { sales: number; purchases: number }> = {}
  
  filteredSales.value.forEach(sale => {
    if (!sale.date) return
    const date = new Date(sale.date)
    let key = ''
    
    if (dateFilter.value === 'year' || dateFilter.value === 'all') {
      key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    } else {
      key = date.toISOString().split('T')[0]
    }
    
    if (!dataMap[key]) dataMap[key] = { sales: 0, purchases: 0 }
    dataMap[key].sales += Number(sale.total_amount || 0)
  })
  
  filteredPurchases.value.forEach(purchase => {
    if (!purchase.date) return
    const date = new Date(purchase.date)
    let key = ''
    
    if (dateFilter.value === 'year' || dateFilter.value === 'all') {
      key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    } else {
      key = date.toISOString().split('T')[0]
    }
    
    if (!dataMap[key]) dataMap[key] = { sales: 0, purchases: 0 }
    dataMap[key].purchases += Number(purchase.total_amount || 0)
  })
  
  const sorted = Object.entries(dataMap).sort((a, b) => a[0].localeCompare(b[0]))
  return {
    categories: sorted.map(([date]) => date),
    salesData: sorted.map(([, data]) => Math.round(data.sales)),
    purchasesData: sorted.map(([, data]) => Math.round(data.purchases))
  }
})

const salesVsPurchasesOptions = computed(() => ({
  chart: { type: 'line', height: 350, toolbar: { show: true }, zoom: { enabled: true } },
  stroke: { curve: 'smooth', width: 3 },
  dataLabels: { enabled: false },
  xaxis: { categories: salesVsPurchasesData.value.categories },
  yaxis: {
    title: { text: 'Amount (₨)' },
    labels: {
      formatter: (val: number) => {
        if (val >= 1000000) return `₨${(val / 1000000).toFixed(1)}M`
        if (val >= 1000) return `₨${(val / 1000).toFixed(1)}K`
        return `₨${val}`
      }
    }
  },
  colors: ['#22c55e', '#ef4444'],
  legend: { position: 'top' },
  tooltip: { y: { formatter: (val: number) => `₨${val.toLocaleString('en-PK')}` } }
}))

const formatCurrency = (amount: number) => {
  if (amount >= 1000000) return `₨${(amount / 1000000).toFixed(1)}M`
  if (amount >= 1000) return `₨${(amount / 1000).toFixed(1)}K`
  return `₨${amount.toLocaleString('en-PK', { maximumFractionDigits: 0 })}`
}

const resetFilters = () => {
  dateFilter.value = 'all'
  selectedCustomer.value = 'all'
  selectedVendor.value = 'all'
  selectedProduct.value = 'all'
  customStartDate.value = ''
  customEndDate.value = ''
}
</script>

<template>
  <div class="analytics-dashboard">
    <div class="dashboard-header">
      <div>
        <h1>📊 Advanced Analytics Dashboard</h1>
        <p class="subtitle">Data-driven insights with interactive filters and visualizations</p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading analytics...</p>
    </div>

    <div v-else class="dashboard-content">
      <!-- FILTERS PANEL -->
      <div class="filters-panel">
        <h3>🔍 Filters</h3>
        <div class="filters-grid">
          <div class="filter-group">
            <label>Date Range</label>
            <select v-model="dateFilter" class="filter-select">
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">Last 7 Days</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>

          <div v-if="dateFilter === 'custom'" class="filter-group">
            <label>Start Date</label>
            <input v-model="customStartDate" type="date" class="filter-input" />
          </div>

          <div v-if="dateFilter === 'custom'" class="filter-group">
            <label>End Date</label>
            <input v-model="customEndDate" type="date" class="filter-input" />
          </div>

          <div class="filter-group">
            <label>Customer</label>
            <select v-model="selectedCustomer" class="filter-select">
              <option :value="'all'">All Customers</option>
              <option v-for="customer in customersStore.customers" :key="customer.id" :value="customer.id">
                {{ customer.name }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Vendor</label>
            <select v-model="selectedVendor" class="filter-select">
              <option :value="'all'">All Vendors</option>
              <option v-for="vendor in vendorsStore.vendors" :key="vendor.id" :value="vendor.id">
                {{ vendor.name }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Product</label>
            <select v-model="selectedProduct" class="filter-select">
              <option :value="'all'">All Products</option>
              <option v-for="product in productsStore.products" :key="product.id" :value="product.id">
                {{ product.name }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <button @click="resetFilters" class="reset-btn">🔄 Reset Filters</button>
          </div>
        </div>
      </div>

      <!-- KEY METRICS -->
      <div class="kpi-row">
        <div class="kpi-card revenue">
          <div class="kpi-icon">💰</div>
          <div class="kpi-content">
            <div class="kpi-label">Total Sales</div>
            <div class="kpi-value">{{ formatCurrency(totalSales) }}</div>
            <div class="kpi-detail">{{ filteredSales.length }} transactions</div>
          </div>
        </div>

        <div class="kpi-card expense">
          <div class="kpi-icon">📊</div>
          <div class="kpi-content">
            <div class="kpi-label">Total Purchases</div>
            <div class="kpi-value">{{ formatCurrency(totalPurchases) }}</div>
            <div class="kpi-detail">{{ filteredPurchases.length }} orders</div>
          </div>
        </div>

        <div class="kpi-card profit">
          <div class="kpi-icon">📈</div>
          <div class="kpi-content">
            <div class="kpi-label">Gross Profit</div>
            <div class="kpi-value">{{ formatCurrency(grossProfit) }}</div>
            <div class="kpi-detail" :class="Number(profitMargin) >= 0 ? 'positive' : 'negative'">
              {{ profitMargin }}% margin
            </div>
          </div>
        </div>

        <div class="kpi-card info">
          <div class="kpi-icon">📋</div>
          <div class="kpi-content">
            <div class="kpi-label">Active Filters</div>
            <div class="kpi-value">{{ 
              [dateFilter !== 'all', selectedCustomer !== 'all', selectedVendor !== 'all', selectedProduct !== 'all'].filter(Boolean).length 
            }}</div>
            <div class="kpi-detail">filters applied</div>
          </div>
        </div>
      </div>

      <!-- CHARTS GRID -->
      <div class="charts-section">
        <div class="chart-card full">
          <h3>📈 Sales Trend Over Time</h3>
          <p class="chart-subtitle">Track revenue performance trends</p>
          <apexchart 
            type="area" 
            height="350" 
            :options="salesTrendOptions" 
            :series="[{ name: 'Sales', data: salesTrendData.data }]"
          />
        </div>

        <div class="chart-card full">
          <h3>⚖️ Sales vs Purchases Comparison</h3>
          <p class="chart-subtitle">Revenue vs expenses trend analysis</p>
          <apexchart 
            type="line" 
            height="350" 
            :options="salesVsPurchasesOptions" 
            :series="[
              { name: 'Sales', data: salesVsPurchasesData.salesData },
              { name: 'Purchases', data: salesVsPurchasesData.purchasesData }
            ]"
          />
        </div>

        <div class="chart-card">
          <h3>👥 Sales by Customer</h3>
          <p class="chart-subtitle">Top customers by revenue</p>
          <apexchart 
            type="bar" 
            height="350" 
            :options="customerSalesOptions" 
            :series="[{ name: 'Sales', data: customerSalesData.data }]"
          />
        </div>

        <div class="chart-card">
          <h3>📦 Sales by Product</h3>
          <p class="chart-subtitle">Product revenue distribution</p>
          <apexchart 
            type="donut" 
            height="350" 
            :options="productSalesOptions" 
            :series="productSalesData.series"
          />
        </div>

        <div class="chart-card">
          <h3>🏢 Purchases by Vendor</h3>
          <p class="chart-subtitle">Top vendors by purchase amount</p>
          <apexchart 
            type="bar" 
            height="350" 
            :options="vendorPurchasesOptions" 
            :series="[{ name: 'Purchases', data: vendorPurchasesData.data }]"
          />
        </div>

        <div class="chart-card">
          <h3>💳 Payment Methods</h3>
          <p class="chart-subtitle">Payment distribution by method</p>
          <apexchart 
            type="pie" 
            height="350" 
            :options="paymentMethodsOptions" 
            :series="paymentMethodsData.series"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analytics-dashboard {
  padding: 1.5rem;
  background: #f8fafc;
  min-height: 100vh;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.subtitle {
  color: #64748b;
  margin-top: 0.25rem;
  font-size: clamp(0.75rem, 2vw, 0.875rem);
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
  to { transform: rotate(360deg); }
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Filters Panel */
.filters-panel {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3b82f6;
}

.filters-panel h3 {
  font-size: clamp(1rem, 2.5vw, 1.125rem);
  margin: 0 0 1rem 0;
  color: #0f172a;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr));
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  font-weight: 600;
  color: #64748b;
}

.filter-select, .filter-input {
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  color: #0f172a;
  background: white;
  transition: border-color 0.2s;
}

.filter-select:focus, .filter-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.reset-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
  font-size: clamp(0.75rem, 2vw, 0.875rem);
}

.reset-btn:hover {
  transform: translateY(-2px);
}

/* KPI Cards */
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
  display: flex;
  gap: 1rem;
  align-items: center;
  min-width: 0;
}

.kpi-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  flex-shrink: 0;
}

.kpi-card.revenue .kpi-icon { background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); }
.kpi-card.expense .kpi-icon { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); }
.kpi-card.profit .kpi-icon { background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); }
.kpi-card.info .kpi-icon { background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); }

.kpi-content {
  flex: 1;
  min-width: 0;
}

.kpi-label {
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  color: #64748b;
  font-weight: 500;
}

.kpi-value {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 700;
  color: #0f172a;
  margin: 0.25rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kpi-detail {
  font-size: clamp(0.7rem, 1.8vw, 0.75rem);
  color: #64748b;
}

.kpi-detail.positive { color: #16a34a; font-weight: 600; }
.kpi-detail.negative { color: #dc2626; font-weight: 600; }

/* Charts */
.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 400px), 1fr));
  gap: 1.5rem;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-card.full {
  grid-column: 1 / -1;
}

.chart-card h3 {
  font-size: clamp(1rem, 2.5vw, 1.125rem);
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
}

.chart-subtitle {
  font-size: clamp(0.7rem, 1.8vw, 0.75rem);
  color: #64748b;
  margin: 0 0 1rem 0;
}

@media (max-width: 768px) {
  .analytics-dashboard {
    padding: 1rem;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }
}
</style>
