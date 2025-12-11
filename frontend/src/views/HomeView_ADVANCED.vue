<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProductsStore } from '../modules/products/stores/products'
import { useCustomersStore } from '../modules/customers/stores/customers'
import { useVendorsStore } from '../modules/vendors/stores/vendors'
import { useSalesStore } from '../modules/sales/stores/sales'
import { usePurchasesStore } from '../modules/purchases/stores/purchases'
import { usePaymentsStore } from '../modules/payments/stores/payments'
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
const selectedPeriod = ref('all')
const selectedCustomer = ref('all')
const selectedVendor = ref('all')
const selectedProduct = ref('all')

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      productsStore.fetchProducts().catch(e => console.error('Products error:', e)),
      customersStore.fetchCustomers().catch(e => console.error('Customers error:', e)),
      vendorsStore.fetchVendors().catch(e => console.error('Vendors error:', e)),
      salesStore.fetchSales().catch(e => console.error('Sales error:', e)),
      purchasesStore.fetchPurchases().catch(e => console.error('Purchases error:', e)),
      paymentsStore.fetchPayments().catch(e => console.error('Payments error:', e)),
      rawMaterialsStore.fetchMaterials().catch(e => console.error('Raw materials error:', e))
    ])
  } catch (error) {
    console.error('Dashboard loading error:', error)
  } finally {
    loading.value = false
  }
})

// ==================== INVENTORY ANALYTICS ====================
const inventoryByProduct = computed(() => {
  return (productsStore.products || []).map((p: any) => ({
    id: p.id,
    name: p.name,
    type: p.type || p.product_type,
    quantity: p.quantity || 0,
    value: (p.quantity || 0) * (p.cost_per_unit || p.price || 0),
    status: p.quantity === 0 ? 'Out of Stock' : p.quantity <= 10 ? 'Low Stock' : 'In Stock'
  })).sort((a, b) => b.value - a.value)
})

const inventoryByRawMaterial = computed(() => {
  return (rawMaterialsStore.materials || []).map(m => ({
    id: m.id,
    name: m.name,
    quantity: m.quantity || 0,
    unit: m.unit || '',
    status: m.needs_reorder ? 'Reorder Needed' : 'Available'
  }))
})

const manufacturedProducts = computed(() => 
  inventoryByProduct.value.filter(p => p.type === 'MANUFACTURED')
)

const purchasedProducts = computed(() => 
  inventoryByProduct.value.filter(p => p.type === 'PURCHASED')
)

const totalInventoryValue = computed(() => 
  inventoryByProduct.value.reduce((sum, p) => sum + p.value, 0)
)

// ==================== SALES ANALYTICS ====================
const salesByCustomer = computed(() => {
  const customerMap: Record<number, { id: number; name: string; totalSales: number; transactionCount: number }> = {};
  
  (salesStore.sales || []).forEach((sale: any) => {
    const customerId = sale.customer
    const customerName = sale.customer_name || 'Unknown'
    
    if (customerMap[customerId]) {
      customerMap[customerId].totalSales += Number(sale.total_amount || 0)
      customerMap[customerId].transactionCount++
    } else {
      customerMap[customerId] = {
        id: customerId,
        name: customerName,
        totalSales: Number(sale.total_amount || 0),
        transactionCount: 1
      }
    }
  })
  
  return Object.values(customerMap).sort((a, b) => b.totalSales - a.totalSales)
})

const salesByProduct = computed(() => {
  const productMap: Record<number, { id: number; name: string; quantitySold: number; revenue: number }> = {};
  
  (salesStore.sales || []).forEach((sale: any) => {
    (sale.sale_items || []).forEach((item: any) => {
      const productId = item.product
      if (productMap[productId]) {
        productMap[productId].quantitySold += Number(item.quantity || 0)
        productMap[productId].revenue += Number(item.quantity || 0) * Number(item.unit_price || 0)
      } else {
        productMap[productId] = {
          id: productId,
          name: item.product_name || 'Unknown',
          quantitySold: Number(item.quantity || 0),
          revenue: Number(item.quantity || 0) * Number(item.unit_price || 0)
        }
      }
    })
  })
  
  return Object.values(productMap).sort((a, b) => b.revenue - a.revenue)
})

const salesByMonth = computed(() => {
  const monthMap: Record<string, number> = {};
  
  (salesStore.sales || []).forEach((sale: any) => {
    if (!sale.date) return
    const date = new Date(sale.date)
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    monthMap[monthKey] = (monthMap[monthKey] || 0) + Number(sale.total_amount || 0)
  })
  
  return Object.entries(monthMap)
    .map(([month, total]) => ({ month, total }))
    .sort((a, b) => a.month.localeCompare(b.month))
})

const topCustomers = computed(() => salesByCustomer.value.slice(0, 5))
const topProducts = computed(() => salesByProduct.value.slice(0, 5))
const totalSalesRevenue = computed(() => (salesStore.sales || []).reduce((sum, s) => sum + Number(s.total_amount || 0), 0))

// ==================== VENDOR ANALYTICS ====================
const purchasesByVendor = computed(() => {
  const vendorMap: Record<number, { id: number; name: string; totalPurchases: number; transactionCount: number; products: string[] }> = {};
  
  (purchasesStore.purchases || []).forEach((purchase: any) => {
    const vendorId = purchase.vendor
    const vendorName = purchase.vendor_name || 'Unknown'
    
    if (vendorMap[vendorId]) {
      vendorMap[vendorId].totalPurchases += Number(purchase.total_amount || 0)
      vendorMap[vendorId].transactionCount++
    } else {
      vendorMap[vendorId] = {
        id: vendorId,
        name: vendorName,
        totalPurchases: Number(purchase.total_amount || 0),
        transactionCount: 1,
        products: []
      }
    }
  })
  
  return Object.values(vendorMap).sort((a, b) => b.totalPurchases - a.totalPurchases)
})

const topVendors = computed(() => purchasesByVendor.value.slice(0, 5))
const totalPurchasesCost = computed(() => (purchasesStore.purchases || []).reduce((sum, p) => sum + Number(p.total_amount || 0), 0))

// ==================== FINANCIAL ANALYTICS - INCOMING ====================
const incomingPayments = computed(() => (paymentsStore.payments || []).filter(p => p.payment_type === 'INCOMING'))

const incomingByMethod = computed(() => {
  const methodMap: Record<string, number> = {}
  
  incomingPayments.value.forEach(payment => {
    const method = payment.payment_method || 'Unknown'
    methodMap[method] = (methodMap[method] || 0) + Number(payment.amount || 0)
  })
  
  return Object.entries(methodMap).map(([method, amount]) => ({ method, amount }))
})

const incomingByCustomer = computed(() => {
  const customerMap: Record<number, { name: string; totalAmount: number; paymentCount: number }> = {};
  
  incomingPayments.value.forEach((payment: any) => {
    const customerId = payment.customer
    if (!customerId) return
    
    const customer = customersStore.customers?.find(c => c.id === customerId)
    const customerName = customer?.name || 'Unknown'
    
    if (customerMap[customerId]) {
      customerMap[customerId].totalAmount += Number(payment.amount || 0)
      customerMap[customerId].paymentCount++
    } else {
      customerMap[customerId] = {
        name: customerName,
        totalAmount: Number(payment.amount || 0),
        paymentCount: 1
      }
    }
  })
  
  return Object.values(customerMap).sort((a, b) => b.totalAmount - a.totalAmount)
})

const totalIncoming = computed(() => incomingPayments.value.reduce((sum, p) => sum + Number(p.amount || 0), 0))
const completedIncoming = computed(() => incomingPayments.value.filter(p => p.status === 'COMPLETED').reduce((sum, p) => sum + Number(p.amount || 0), 0))
const pendingIncoming = computed(() => totalIncoming.value - completedIncoming.value)

// ==================== FINANCIAL ANALYTICS - OUTGOING ====================
const outgoingPayments = computed(() => (paymentsStore.payments || []).filter(p => p.payment_type === 'OUTGOING'))

const outgoingByMethod = computed(() => {
  const methodMap: Record<string, number> = {}
  
  outgoingPayments.value.forEach(payment => {
    const method = payment.payment_method || 'Unknown'
    methodMap[method] = (methodMap[method] || 0) + Number(payment.amount || 0)
  })
  
  return Object.entries(methodMap).map(([method, amount]) => ({ method, amount }))
})

const outgoingByVendor = computed(() => {
  const vendorMap: Record<number, { name: string; totalAmount: number; paymentCount: number }> = {};
  
  outgoingPayments.value.forEach((payment: any) => {
    const vendorId = payment.vendor
    if (!vendorId) return
    
    const vendor = vendorsStore.vendors?.find(v => v.id === vendorId)
    const vendorName = vendor?.name || 'Unknown'
    
    if (vendorMap[vendorId]) {
      vendorMap[vendorId].totalAmount += Number(payment.amount || 0)
      vendorMap[vendorId].paymentCount++
    } else {
      vendorMap[vendorId] = {
        name: vendorName,
        totalAmount: Number(payment.amount || 0),
        paymentCount: 1
      }
    }
  })
  
  return Object.values(vendorMap).sort((a, b) => b.totalAmount - a.totalAmount)
})

const totalOutgoing = computed(() => outgoingPayments.value.reduce((sum, p) => sum + Number(p.amount || 0), 0))
const completedOutgoing = computed(() => outgoingPayments.value.filter(p => p.status === 'COMPLETED').reduce((sum, p) => sum + Number(p.amount || 0), 0))
const pendingOutgoing = computed(() => totalOutgoing.value - completedOutgoing.value)

// ==================== KEY METRICS ====================
const grossProfit = computed(() => totalSalesRevenue.value - totalPurchasesCost.value)
const profitMargin = computed(() => totalSalesRevenue.value > 0 ? ((grossProfit.value / totalSalesRevenue.value) * 100).toFixed(1) : '0.0')
const cashFlow = computed(() => completedIncoming.value - completedOutgoing.value)

const formatCurrency = (amount: number) => {
  if (amount >= 1000000) return `₨${(amount / 1000000).toFixed(1)}M`
  if (amount >= 1000) return `₨${(amount / 1000).toFixed(1)}K`
  return `₨${amount.toLocaleString('en-PK', { maximumFractionDigits: 0 })}`
}

const formatCurrencyFull = (amount: number) => `₨${amount.toLocaleString('en-PK', { minimumFractionDigits: 2 })}`
</script>

<template>
  <div class="advanced-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1>Advanced Analytics Dashboard</h1>
        <p class="subtitle">Comprehensive business intelligence and performance metrics</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading analytics...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="dashboard-content">
      <!-- Navigation Tabs -->
      <div class="tabs-container">
        <button 
          @click="activeTab = 'overview'" 
          :class="['tab-btn', { active: activeTab === 'overview' }]"
        >
          📊 Overview
        </button>
        <button 
          @click="activeTab = 'inventory'" 
          :class="['tab-btn', { active: activeTab === 'inventory' }]"
        >
          📦 Inventory
        </button>
        <button 
          @click="activeTab = 'sales'" 
          :class="['tab-btn', { active: activeTab === 'sales' }]"
        >
          💰 Sales
        </button>
        <button 
          @click="activeTab = 'vendors'" 
          :class="['tab-btn', { active: activeTab === 'vendors' }]"
        >
          🏢 Vendors
        </button>
        <button 
          @click="activeTab = 'financials'" 
          :class="['tab-btn', { active: activeTab === 'financials' }]"
        >
          💵 Financials
        </button>
      </div>

      <!-- OVERVIEW TAB -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <!-- Key KPIs -->
        <div class="kpi-row">
          <div class="kpi-card revenue">
            <div class="kpi-icon">💰</div>
            <div class="kpi-content">
              <div class="kpi-label">Total Sales</div>
              <div class="kpi-value">{{ formatCurrency(totalSalesRevenue) }}</div>
              <div class="kpi-detail">From {{ salesStore.sales?.length || 0 }} transactions</div>
            </div>
          </div>

          <div class="kpi-card expense">
            <div class="kpi-icon">📊</div>
            <div class="kpi-content">
              <div class="kpi-label">Total Purchases</div>
              <div class="kpi-value">{{ formatCurrency(totalPurchasesCost) }}</div>
              <div class="kpi-detail">{{ purchasesStore.purchases?.length || 0 }} purchase orders</div>
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

          <div class="kpi-card cash">
            <div class="kpi-icon">💵</div>
            <div class="kpi-content">
              <div class="kpi-label">Cash Flow</div>
              <div class="kpi-value">{{ formatCurrency(cashFlow) }}</div>
              <div class="kpi-detail" :class="cashFlow >= 0 ? 'positive' : 'negative'">
                {{ cashFlow >= 0 ? 'Positive' : 'Negative' }} flow
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Grid -->
        <div class="stats-section">
          <h2 class="section-title">Quick Stats</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">🏭</div>
              <div class="stat-content">
                <div class="stat-value">{{ manufacturedProducts.length }}</div>
                <div class="stat-label">Manufactured Products</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">📦</div>
              <div class="stat-content">
                <div class="stat-value">{{ rawMaterialsStore.materials?.length || 0 }}</div>
                <div class="stat-label">Raw Materials</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">👥</div>
              <div class="stat-content">
                <div class="stat-value">{{ customersStore.customers?.length || 0 }}</div>
                <div class="stat-label">Total Customers</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">🏢</div>
              <div class="stat-content">
                <div class="stat-value">{{ vendorsStore.vendors?.length || 0 }}</div>
                <div class="stat-label">Total Vendors</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Performers -->
        <div class="performers-section">
          <div class="performer-card">
            <h3>🏆 Top Customers</h3>
            <div class="performer-list">
              <div v-for="customer in topCustomers" :key="customer.id" class="performer-item">
                <div class="performer-name">{{ customer.name }}</div>
                <div class="performer-value">{{ formatCurrency(customer.totalSales) }}</div>
              </div>
              <div v-if="topCustomers.length === 0" class="empty-state">No customer data</div>
            </div>
          </div>

          <div class="performer-card">
            <h3>🏆 Top Products</h3>
            <div class="performer-list">
              <div v-for="product in topProducts" :key="product.id" class="performer-item">
                <div class="performer-name">{{ product.name }}</div>
                <div class="performer-value">{{ formatCurrency(product.revenue) }}</div>
              </div>
              <div v-if="topProducts.length === 0" class="empty-state">No product data</div>
            </div>
          </div>

          <div class="performer-card">
            <h3>🏆 Top Vendors</h3>
            <div class="performer-list">
              <div v-for="vendor in topVendors" :key="vendor.id" class="performer-item">
                <div class="performer-name">{{ vendor.name }}</div>
                <div class="performer-value">{{ formatCurrency(vendor.totalPurchases) }}</div>
              </div>
              <div v-if="topVendors.length === 0" class="empty-state">No vendor data</div>
            </div>
          </div>
        </div>
      </div>

      <!-- INVENTORY TAB -->
      <div v-if="activeTab === 'inventory'" class="tab-content">
        <h2 class="section-title">Inventory Analytics</h2>
        
        <!-- Inventory Summary -->
        <div class="inventory-summary">
          <div class="summary-card">
            <div class="summary-icon">🏭</div>
            <div class="summary-content">
              <div class="summary-label">Manufactured Products</div>
              <div class="summary-value">{{ manufacturedProducts.length }}</div>
              <div class="summary-detail">Value: {{ formatCurrency(manufacturedProducts.reduce((s, p) => s + p.value, 0)) }}</div>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">🛒</div>
            <div class="summary-content">
              <div class="summary-label">Purchased Products</div>
              <div class="summary-value">{{ purchasedProducts.length }}</div>
              <div class="summary-detail">Value: {{ formatCurrency(purchasedProducts.reduce((s, p) => s + p.value, 0)) }}</div>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">📦</div>
            <div class="summary-content">
              <div class="summary-label">Raw Materials</div>
              <div class="summary-value">{{ inventoryByRawMaterial.length }}</div>
              <div class="summary-detail">{{ inventoryByRawMaterial.filter(m => m.status === 'Reorder Needed').length }} need reorder</div>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">💰</div>
            <div class="summary-content">
              <div class="summary-label">Total Inventory Value</div>
              <div class="summary-value">{{ formatCurrency(totalInventoryValue) }}</div>
              <div class="summary-detail">All products combined</div>
            </div>
          </div>
        </div>

        <!-- Product Inventory Table -->
        <div class="data-table-section">
          <h3>All Products Inventory</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Product Name</div>
              <div class="table-cell">Type</div>
              <div class="table-cell">Quantity</div>
              <div class="table-cell">Value</div>
              <div class="table-cell">Status</div>
            </div>
            <div v-for="product in inventoryByProduct" :key="product.id" class="table-row">
              <div class="table-cell">{{ product.name }}</div>
              <div class="table-cell">{{ product.type === 'MANUFACTURED' ? 'Manufactured' : 'Purchased' }}</div>
              <div class="table-cell">{{ product.quantity }}</div>
              <div class="table-cell">{{ formatCurrencyFull(product.value) }}</div>
              <div class="table-cell">
                <span :class="['status-badge', product.status.replace(' ', '-').toLowerCase()]">
                  {{ product.status }}
                </span>
              </div>
            </div>
            <div v-if="inventoryByProduct.length === 0" class="empty-row">No products in inventory</div>
          </div>
        </div>

        <!-- Raw Materials Table -->
        <div class="data-table-section">
          <h3>Raw Materials Inventory</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Material Name</div>
              <div class="table-cell">Quantity</div>
              <div class="table-cell">Unit</div>
              <div class="table-cell">Status</div>
            </div>
            <div v-for="material in inventoryByRawMaterial" :key="material.id" class="table-row">
              <div class="table-cell">{{ material.name }}</div>
              <div class="table-cell">{{ material.quantity }}</div>
              <div class="table-cell">{{ material.unit }}</div>
              <div class="table-cell">
                <span :class="['status-badge', material.status.replace(' ', '-').toLowerCase()]">
                  {{ material.status }}
                </span>
              </div>
            </div>
            <div v-if="inventoryByRawMaterial.length === 0" class="empty-row">No raw materials in inventory</div>
          </div>
        </div>
      </div>

      <!-- SALES TAB -->
      <div v-if="activeTab === 'sales'" class="tab-content">
        <h2 class="section-title">Sales Analytics</h2>

        <!-- Sales by Customer -->
        <div class="data-table-section">
          <h3>Sales by Customer</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Customer Name</div>
              <div class="table-cell">Total Sales</div>
              <div class="table-cell">Transactions</div>
              <div class="table-cell">Avg. Transaction</div>
            </div>
            <div v-for="customer in salesByCustomer" :key="customer.id" class="table-row">
              <div class="table-cell">{{ customer.name }}</div>
              <div class="table-cell">{{ formatCurrencyFull(customer.totalSales) }}</div>
              <div class="table-cell">{{ customer.transactionCount }}</div>
              <div class="table-cell">{{ formatCurrencyFull(customer.totalSales / customer.transactionCount) }}</div>
            </div>
            <div v-if="salesByCustomer.length === 0" class="empty-row">No sales data available</div>
          </div>
        </div>

        <!-- Sales by Product -->
        <div class="data-table-section">
          <h3>Sales by Product</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Product Name</div>
              <div class="table-cell">Quantity Sold</div>
              <div class="table-cell">Revenue</div>
              <div class="table-cell">% of Total</div>
            </div>
            <div v-for="product in salesByProduct" :key="product.id" class="table-row">
              <div class="table-cell">{{ product.name }}</div>
              <div class="table-cell">{{ product.quantitySold }}</div>
              <div class="table-cell">{{ formatCurrencyFull(product.revenue) }}</div>
              <div class="table-cell">{{ ((product.revenue / totalSalesRevenue) * 100).toFixed(1) }}%</div>
            </div>
            <div v-if="salesByProduct.length === 0" class="empty-row">No product sales data</div>
          </div>
        </div>

        <!-- Sales by Month -->
        <div class="data-table-section">
          <h3>Sales by Month</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Month</div>
              <div class="table-cell">Total Sales</div>
            </div>
            <div v-for="item in salesByMonth" :key="item.month" class="table-row">
              <div class="table-cell">{{ item.month }}</div>
              <div class="table-cell">{{ formatCurrencyFull(item.total) }}</div>
            </div>
            <div v-if="salesByMonth.length === 0" class="empty-row">No monthly data</div>
          </div>
        </div>
      </div>

      <!-- VENDORS TAB -->
      <div v-if="activeTab === 'vendors'" class="tab-content">
        <h2 class="section-title">Vendor Analytics</h2>

        <!-- Purchases by Vendor -->
        <div class="data-table-section">
          <h3>Purchases by Vendor</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Vendor Name</div>
              <div class="table-cell">Total Purchases</div>
              <div class="table-cell">Transactions</div>
              <div class="table-cell">Avg. Order Value</div>
            </div>
            <div v-for="vendor in purchasesByVendor" :key="vendor.id" class="table-row">
              <div class="table-cell">{{ vendor.name }}</div>
              <div class="table-cell">{{ formatCurrencyFull(vendor.totalPurchases) }}</div>
              <div class="table-cell">{{ vendor.transactionCount }}</div>
              <div class="table-cell">{{ formatCurrencyFull(vendor.totalPurchases / vendor.transactionCount) }}</div>
            </div>
            <div v-if="purchasesByVendor.length === 0" class="empty-row">No vendor data available</div>
          </div>
        </div>
      </div>

      <!-- FINANCIALS TAB -->
      <div v-if="activeTab === 'financials'" class="tab-content">
        <h2 class="section-title">Financial Analytics</h2>

        <!-- Financial Overview Cards -->
        <div class="financial-overview">
          <div class="fin-card incoming">
            <h3>💰 Incoming (Receivables)</h3>
            <div class="fin-stats">
              <div class="fin-stat">
                <span class="fin-label">Total Expected:</span>
                <span class="fin-value">{{ formatCurrencyFull(totalIncoming) }}</span>
              </div>
              <div class="fin-stat">
                <span class="fin-label">Completed:</span>
                <span class="fin-value positive">{{ formatCurrencyFull(completedIncoming) }}</span>
              </div>
              <div class="fin-stat">
                <span class="fin-label">Pending:</span>
                <span class="fin-value warning">{{ formatCurrencyFull(pendingIncoming) }}</span>
              </div>
            </div>
          </div>

          <div class="fin-card outgoing">
            <h3>📤 Outgoing (Payables)</h3>
            <div class="fin-stats">
              <div class="fin-stat">
                <span class="fin-label">Total Expected:</span>
                <span class="fin-value">{{ formatCurrencyFull(totalOutgoing) }}</span>
              </div>
              <div class="fin-stat">
                <span class="fin-label">Completed:</span>
                <span class="fin-value positive">{{ formatCurrencyFull(completedOutgoing) }}</span>
              </div>
              <div class="fin-stat">
                <span class="fin-label">Pending:</span>
                <span class="fin-value danger">{{ formatCurrencyFull(pendingOutgoing) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Incoming by Payment Method -->
        <div class="data-table-section">
          <h3>Incoming Payments by Method</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Payment Method</div>
              <div class="table-cell">Total Amount</div>
              <div class="table-cell">% of Total</div>
            </div>
            <div v-for="item in incomingByMethod" :key="item.method" class="table-row">
              <div class="table-cell">{{ item.method }}</div>
              <div class="table-cell">{{ formatCurrencyFull(item.amount) }}</div>
              <div class="table-cell">{{ ((item.amount / totalIncoming) * 100).toFixed(1) }}%</div>
            </div>
            <div v-if="incomingByMethod.length === 0" class="empty-row">No incoming payments</div>
          </div>
        </div>

        <!-- Incoming by Customer -->
        <div class="data-table-section">
          <h3>Incoming Payments by Customer</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Customer Name</div>
              <div class="table-cell">Total Amount</div>
              <div class="table-cell">Payment Count</div>
              <div class="table-cell">Avg. Payment</div>
            </div>
            <div v-for="customer in incomingByCustomer" :key="customer.name" class="table-row">
              <div class="table-cell">{{ customer.name }}</div>
              <div class="table-cell">{{ formatCurrencyFull(customer.totalAmount) }}</div>
              <div class="table-cell">{{ customer.paymentCount }}</div>
              <div class="table-cell">{{ formatCurrencyFull(customer.totalAmount / customer.paymentCount) }}</div>
            </div>
            <div v-if="incomingByCustomer.length === 0" class="empty-row">No customer payments</div>
          </div>
        </div>

        <!-- Outgoing by Payment Method -->
        <div class="data-table-section">
          <h3>Outgoing Payments by Method</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Payment Method</div>
              <div class="table-cell">Total Amount</div>
              <div class="table-cell">% of Total</div>
            </div>
            <div v-for="item in outgoingByMethod" :key="item.method" class="table-row">
              <div class="table-cell">{{ item.method }}</div>
              <div class="table-cell">{{ formatCurrencyFull(item.amount) }}</div>
              <div class="table-cell">{{ ((item.amount / totalOutgoing) * 100).toFixed(1) }}%</div>
            </div>
            <div v-if="outgoingByMethod.length === 0" class="empty-row">No outgoing payments</div>
          </div>
        </div>

        <!-- Outgoing by Vendor -->
        <div class="data-table-section">
          <h3>Outgoing Payments by Vendor</h3>
          <div class="data-table">
            <div class="table-header">
              <div class="table-cell">Vendor Name</div>
              <div class="table-cell">Total Amount</div>
              <div class="table-cell">Payment Count</div>
              <div class="table-cell">Avg. Payment</div>
            </div>
            <div v-for="vendor in outgoingByVendor" :key="vendor.name" class="table-row">
              <div class="table-cell">{{ vendor.name }}</div>
              <div class="table-cell">{{ formatCurrencyFull(vendor.totalAmount) }}</div>
              <div class="table-cell">{{ vendor.paymentCount }}</div>
              <div class="table-cell">{{ formatCurrencyFull(vendor.totalAmount / vendor.paymentCount) }}</div>
            </div>
            <div v-if="outgoingByVendor.length === 0" class="empty-row">No vendor payments</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.advanced-dashboard {
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

/* Tabs */
.tabs-container {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: #64748b;
  font-weight: 600;
  font-size: clamp(0.8rem, 2vw, 0.875rem);
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.tab-btn.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  font-size: clamp(1.125rem, 3vw, 1.25rem);
  font-weight: 600;
  color: #0f172a;
  margin: 0;
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
.kpi-card.cash .kpi-icon { background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); }

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

/* Stats Grid */
.stats-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-value {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 700;
  color: #0f172a;
}

.stat-label {
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  color: #64748b;
}

/* Performers */
.performers-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
  gap: 1.5rem;
}

.performer-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.performer-card h3 {
  font-size: clamp(1rem, 2.5vw, 1.125rem);
  margin: 0 0 1rem 0;
  color: #0f172a;
}

.performer-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.performer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.performer-name {
  font-size: clamp(0.8rem, 2vw, 0.875rem);
  color: #0f172a;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.performer-value {
  font-size: clamp(0.8rem, 2vw, 0.875rem);
  color: #3b82f6;
  font-weight: 700;
  white-space: nowrap;
}

/* Inventory & Data Tables */
.inventory-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
  gap: 1rem;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 1rem;
  align-items: center;
}

.summary-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.summary-content {
  flex: 1;
  min-width: 0;
}

.summary-label {
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  color: #64748b;
  font-weight: 500;
}

.summary-value {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: 700;
  color: #0f172a;
  margin: 0.25rem 0;
}

.summary-detail {
  font-size: clamp(0.7rem, 1.8vw, 0.75rem);
  color: #94a3b8;
}

.data-table-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.data-table-section h3 {
  font-size: clamp(1rem, 2.5vw, 1.125rem);
  margin: 0 0 1rem 0;
  color: #0f172a;
}

.data-table {
  overflow-x: auto;
}

.table-header, .table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 1rem;
  padding: 0.75rem;
  align-items: center;
}

.table-header {
  background: #f8fafc;
  border-radius: 8px;
  font-weight: 600;
  color: #0f172a;
  font-size: clamp(0.75rem, 2vw, 0.875rem);
}

.table-row {
  border-bottom: 1px solid #f1f5f9;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: clamp(0.7rem, 1.8vw, 0.75rem);
  font-weight: 600;
  white-space: nowrap;
  display: inline-block;
}

.status-badge.in-stock { background: #dcfce7; color: #16a34a; }
.status-badge.low-stock { background: #fef3c7; color: #d97706; }
.status-badge.out-of-stock { background: #fee2e2; color: #dc2626; }
.status-badge.available { background: #dcfce7; color: #16a34a; }
.status-badge.reorder-needed { background: #fef3c7; color: #d97706; }

.empty-row, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #94a3b8;
  font-size: clamp(0.8rem, 2vw, 0.875rem);
}

/* Financial Cards */
.financial-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));
  gap: 1.5rem;
}

.fin-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.fin-card h3 {
  font-size: clamp(1rem, 2.5vw, 1.125rem);
  margin: 0 0 1rem 0;
  color: #0f172a;
}

.fin-stats {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.fin-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.fin-label {
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  color: #64748b;
  font-weight: 500;
}

.fin-value {
  font-size: clamp(0.875rem, 2.2vw, 1rem);
  color: #0f172a;
  font-weight: 700;
}

.fin-value.positive { color: #16a34a; }
.fin-value.warning { color: #d97706; }
.fin-value.danger { color: #dc2626; }

@media (max-width: 768px) {
  .advanced-dashboard {
    padding: 1rem;
  }

  .table-header, .table-row {
    grid-template-columns: 1.5fr 1fr 1fr 0.8fr;
    gap: 0.5rem;
    padding: 0.5rem;
  }
}
</style>
