<script setup lang="ts">
import { ref, computed } from 'vue'
import { onMounted } from 'vue'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import { useProductsStore } from '@/modules/products/stores/products'
import { useCustomersStore } from '@/modules/customers/stores/customers'
import { useVendorsStore } from '@/modules/vendors/stores/vendors'
import { useSalesStore } from '@/modules/sales/stores/sales'
import { usePurchasesStore } from '@/modules/purchases/stores/purchases'
import { usePaymentsStore } from '@/modules/payments/stores/payments'
import { useRawMaterialsStore } from '@/modules/raw_materials/stores/raw_materials'

const productsStore = useProductsStore()
const customersStore = useCustomersStore()
const vendorsStore = useVendorsStore()
const salesStore = useSalesStore()
const purchasesStore = usePurchasesStore()
const paymentsStore = usePaymentsStore()
const rawMaterialsStore = useRawMaterialsStore()

const loading = ref(true)
const generating = ref(false)

// Report Type Selection
const reportType = ref('sales')
const reportTypes = [
  { value: 'sales', label: 'Sales Report', icon: '💰' },
  { value: 'purchases', label: 'Purchases Report', icon: '🛒' },
  { value: 'inventory', label: 'Inventory Report', icon: '📦' },
  { value: 'customers', label: 'Customer Report', icon: '👥' },
  { value: 'vendors', label: 'Vendor Report', icon: '🏢' },
  { value: 'payments', label: 'Payments Report', icon: '💳' },
  { value: 'financial', label: 'Financial Summary', icon: '📊' },
  { value: 'complete', label: 'Complete Report (All)', icon: '📋' }
]

// Filters
const dateFilter = ref('all')
const customStartDate = ref('')
const customEndDate = ref('')
const selectedCustomer = ref<number | 'all'>('all')
const selectedVendor = ref<number | 'all'>('all')
const selectedProduct = ref<number | 'all'>('all')
const includeDetails = ref(true)
const includeSummary = ref(true)

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

const filteredPayments = computed(() => {
  return (paymentsStore.payments || []).filter(payment => {
    const dateMatch = filterByDate(payment.date)
    const customerMatch = selectedCustomer.value === 'all' || payment.customer === selectedCustomer.value
    const vendorMatch = selectedVendor.value === 'all' || payment.vendor === selectedVendor.value
    return dateMatch && (customerMatch || vendorMatch)
  })
})

// REPORT GENERATION FUNCTIONS
const generateSalesReport = () => {
  const workbook = XLSX.utils.book_new()
  
  if (includeSummary.value) {
    const totalSales = filteredSales.value.reduce((sum, s) => sum + Number(s.total_amount || 0), 0)
    const paidSales = filteredSales.value.filter(s => s.payment_status === 'PAID').reduce((sum, s) => sum + Number(s.total_amount || 0), 0)
    const unpaidSales = filteredSales.value.filter(s => s.payment_status === 'UNPAID').reduce((sum, s) => sum + Number(s.total_amount || 0), 0)
    
    const summaryData = [
      ['SALES REPORT SUMMARY'],
      ['Generated:', new Date().toLocaleString()],
      ['Date Range:', dateFilter.value],
      [],
      ['Metric', 'Value'],
      ['Total Sales', `₨${totalSales.toLocaleString('en-PK')}`],
      ['Total Transactions', filteredSales.value.length],
      ['Paid Sales', `₨${paidSales.toLocaleString('en-PK')}`],
      ['Unpaid Sales', `₨${unpaidSales.toLocaleString('en-PK')}`],
      ['Average Transaction', `₨${(totalSales / filteredSales.value.length || 0).toLocaleString('en-PK')}`]
    ]
    
    const summarySheet = XLSX.utils.aoa_to_sheet(summaryData)
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary')
  }
  
  if (includeDetails.value) {
    const salesData = filteredSales.value.map(sale => ({
      'Sale ID': sale.id,
      'Date': new Date(sale.date).toLocaleDateString(),
      'Customer': sale.customer_name,
      'Total Amount': Number(sale.total_amount || 0),
      'Payment Status': sale.payment_status,
      'Receipt Number': sale.receipt_number || 'N/A'
    }))
    
    const salesSheet = XLSX.utils.json_to_sheet(salesData)
    XLSX.utils.book_append_sheet(workbook, salesSheet, 'Sales Details')
    
    const itemsData: any[] = []
    filteredSales.value.forEach(sale => {
      (sale.sale_items || []).forEach((item: any) => {
        itemsData.push({
          'Sale ID': sale.id,
          'Date': new Date(sale.date).toLocaleDateString(),
          'Customer': sale.customer_name,
          'Product': item.product_name,
          'Quantity': item.quantity,
          'Unit Price': item.unit_price,
          'Subtotal': Number(item.quantity) * Number(item.unit_price)
        })
      })
    })
    
    const itemsSheet = XLSX.utils.json_to_sheet(itemsData)
    XLSX.utils.book_append_sheet(workbook, itemsSheet, 'Sales Items')
  }
  
  return workbook
}

const generatePurchasesReport = () => {
  const workbook = XLSX.utils.book_new()
  
  if (includeSummary.value) {
    const totalPurchases = filteredPurchases.value.reduce((sum, p) => sum + Number(p.total_amount || 0), 0)
    
    const summaryData = [
      ['PURCHASES REPORT SUMMARY'],
      ['Generated:', new Date().toLocaleString()],
      [],
      ['Metric', 'Value'],
      ['Total Purchases', `₨${totalPurchases.toLocaleString('en-PK')}`],
      ['Total Orders', filteredPurchases.value.length]
    ]
    
    const summarySheet = XLSX.utils.aoa_to_sheet(summaryData)
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary')
  }
  
  if (includeDetails.value) {
    const purchasesData = filteredPurchases.value.map(purchase => ({
      'Purchase ID': purchase.id,
      'Date': new Date(purchase.date).toLocaleDateString(),
      'Vendor': purchase.vendor_name,
      'Total Amount': Number(purchase.total_amount || 0)
    }))
    
    const purchasesSheet = XLSX.utils.json_to_sheet(purchasesData)
    XLSX.utils.book_append_sheet(workbook, purchasesSheet, 'Purchases Details')
  }
  
  return workbook
}

const generateInventoryReport = () => {
  const workbook = XLSX.utils.book_new()
  
  let products = productsStore.products || []
  if (selectedProduct.value !== 'all') {
    products = products.filter(p => p.id === selectedProduct.value)
  }
  
  if (includeSummary.value) {
    const totalValue = products.reduce((sum, p) => sum + (Number(p.quantity || 0) * Number(p.price || 0)), 0)
    
    const summaryData = [
      ['INVENTORY REPORT SUMMARY'],
      ['Generated:', new Date().toLocaleString()],
      [],
      ['Metric', 'Value'],
      ['Total Products', products.length],
      ['Total Inventory Value', `₨${totalValue.toLocaleString('en-PK')}`]
    ]
    
    const summarySheet = XLSX.utils.aoa_to_sheet(summaryData)
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary')
  }
  
  if (includeDetails.value) {
    const productsData = products.map(product => ({
      'Product ID': product.id,
      'Name': product.name,
      'Type': product.product_type,
      'Quantity': product.quantity,
      'Unit Price': product.price,
      'Total Value': Number(product.quantity || 0) * Number(product.price || 0)
    }))
    
    const productsSheet = XLSX.utils.json_to_sheet(productsData)
    XLSX.utils.book_append_sheet(workbook, productsSheet, 'Products')
  }
  
  return workbook
}

const generateCustomersReport = () => {
  const workbook = XLSX.utils.book_new()
  
  let customers = customersStore.customers || []
  if (selectedCustomer.value !== 'all') {
    customers = customers.filter(c => c.id === selectedCustomer.value)
  }
  
  if (includeSummary.value) {
    const summaryData = [
      ['CUSTOMERS REPORT SUMMARY'],
      ['Generated:', new Date().toLocaleString()],
      [],
      ['Total Customers', customers.length]
    ]
    
    const summarySheet = XLSX.utils.aoa_to_sheet(summaryData)
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary')
  }
  
  if (includeDetails.value) {
    const customersData = customers.map(customer => {
      const customerSales = filteredSales.value.filter(s => s.customer === customer.id)
      const totalSales = customerSales.reduce((sum, s) => sum + Number(s.total_amount || 0), 0)
      
      return {
        'Customer ID': customer.id,
        'Name': customer.name,
        'Email': customer.email || 'N/A',
        'Phone': customer.phone || 'N/A',
        'Total Purchases': `₨${totalSales.toLocaleString('en-PK')}`,
        'Transaction Count': customerSales.length
      }
    })
    
    const customersSheet = XLSX.utils.json_to_sheet(customersData)
    XLSX.utils.book_append_sheet(workbook, customersSheet, 'Customers')
  }
  
  return workbook
}

const generateVendorsReport = () => {
  const workbook = XLSX.utils.book_new()
  
  let vendors = vendorsStore.vendors || []
  if (selectedVendor.value !== 'all') {
    vendors = vendors.filter(v => v.id === selectedVendor.value)
  }
  
  if (includeDetails.value) {
    const vendorsData = vendors.map(vendor => {
      const vendorPurchases = filteredPurchases.value.filter(p => p.vendor === vendor.id)
      const totalPurchases = vendorPurchases.reduce((sum, p) => sum + Number(p.total_amount || 0), 0)
      
      return {
        'Vendor ID': vendor.id,
        'Name': vendor.name,
        'Total Purchases': `₨${totalPurchases.toLocaleString('en-PK')}`,
        'Transaction Count': vendorPurchases.length
      }
    })
    
    const vendorsSheet = XLSX.utils.json_to_sheet(vendorsData)
    XLSX.utils.book_append_sheet(workbook, vendorsSheet, 'Vendors')
  }
  
  return workbook
}

const generatePaymentsReport = () => {
  const workbook = XLSX.utils.book_new()
  
  if (includeDetails.value) {
    const paymentsData = filteredPayments.value.map(payment => ({
      'Payment ID': payment.id,
      'Date': new Date(payment.date).toLocaleDateString(),
      'Type': payment.payment_type,
      'Method': payment.payment_method,
      'Amount': Number(payment.amount || 0),
      'Status': payment.status
    }))
    
    const paymentsSheet = XLSX.utils.json_to_sheet(paymentsData)
    XLSX.utils.book_append_sheet(workbook, paymentsSheet, 'Payments')
  }
  
  return workbook
}

const generateFinancialReport = () => {
  const workbook = XLSX.utils.book_new()
  
  const totalSales = filteredSales.value.reduce((sum, s) => sum + Number(s.total_amount || 0), 0)
  const totalPurchases = filteredPurchases.value.reduce((sum, p) => sum + Number(p.total_amount || 0), 0)
  const grossProfit = totalSales - totalPurchases
  
  const financialData = [
    ['FINANCIAL SUMMARY REPORT'],
    ['Generated:', new Date().toLocaleString()],
    [],
    ['Total Sales', `₨${totalSales.toLocaleString('en-PK')}`],
    ['Total Purchases', `₨${totalPurchases.toLocaleString('en-PK')}`],
    ['Gross Profit', `₨${grossProfit.toLocaleString('en-PK')}`]
  ]
  
  const financialSheet = XLSX.utils.aoa_to_sheet(financialData)
  XLSX.utils.book_append_sheet(workbook, financialSheet, 'Financial Summary')
  
  return workbook
}

const generateCompleteReport = () => {
  const workbook = XLSX.utils.book_new()
  
  const salesWB = generateSalesReport()
  const purchasesWB = generatePurchasesReport()
  const inventoryWB = generateInventoryReport()
  const customersWB = generateCustomersReport()
  const vendorsWB = generateVendorsReport()
  const paymentsWB = generatePaymentsReport()
  const financialWB = generateFinancialReport()
  
  salesWB.SheetNames.forEach(name => {
    XLSX.utils.book_append_sheet(workbook, salesWB.Sheets[name], `Sales_${name}`)
  })
  purchasesWB.SheetNames.forEach(name => {
    XLSX.utils.book_append_sheet(workbook, purchasesWB.Sheets[name], `Purchases_${name}`)
  })
  inventoryWB.SheetNames.forEach(name => {
    XLSX.utils.book_append_sheet(workbook, inventoryWB.Sheets[name], `Inventory_${name}`)
  })
  customersWB.SheetNames.forEach(name => {
    XLSX.utils.book_append_sheet(workbook, customersWB.Sheets[name], `Customers_${name}`)
  })
  vendorsWB.SheetNames.forEach(name => {
    XLSX.utils.book_append_sheet(workbook, vendorsWB.Sheets[name], `Vendors_${name}`)
  })
  paymentsWB.SheetNames.forEach(name => {
    XLSX.utils.book_append_sheet(workbook, paymentsWB.Sheets[name], `Payments_${name}`)
  })
  financialWB.SheetNames.forEach(name => {
    XLSX.utils.book_append_sheet(workbook, financialWB.Sheets[name], `Financial_${name}`)
  })
  
  return workbook
}

const generateReport = () => {
  generating.value = true
  
  try {
    let workbook: XLSX.WorkBook
    let filename = ''
    
    switch (reportType.value) {
      case 'sales':
        workbook = generateSalesReport()
        filename = 'Sales_Report'
        break
      case 'purchases':
        workbook = generatePurchasesReport()
        filename = 'Purchases_Report'
        break
      case 'inventory':
        workbook = generateInventoryReport()
        filename = 'Inventory_Report'
        break
      case 'customers':
        workbook = generateCustomersReport()
        filename = 'Customers_Report'
        break
      case 'vendors':
        workbook = generateVendorsReport()
        filename = 'Vendors_Report'
        break
      case 'payments':
        workbook = generatePaymentsReport()
        filename = 'Payments_Report'
        break
      case 'financial':
        workbook = generateFinancialReport()
        filename = 'Financial_Report'
        break
      case 'complete':
        workbook = generateCompleteReport()
        filename = 'Complete_Business_Report'
        break
      default:
        throw new Error('Invalid report type')
    }
    
    const timestamp = new Date().toISOString().split('T')[0]
    filename = `${filename}_${timestamp}.xlsx`
    
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    saveAs(blob, filename)
    
    alert(`Report "${filename}" generated successfully!`)
  } catch (error) {
    alert('Error generating report. Please try again.')
  } finally {
    generating.value = false
  }
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
  <div class="reports-module">
    <div class="reports-header">
      <h1>📊 Professional Reports Generator</h1>
      <p class="subtitle">Generate detailed Excel reports with custom filters</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading data...</p>
    </div>

    <div v-else class="reports-content">
      <div class="section-card">
        <h2>1️⃣ Select Report Type</h2>
        <div class="report-types-grid">
          <label 
            v-for="type in reportTypes" 
            :key="type.value"
            :class="['report-type-card', { selected: reportType === type.value }]"
          >
            <input type="radio" :value="type.value" v-model="reportType" hidden />
            <div class="report-icon">{{ type.icon }}</div>
            <div class="report-label">{{ type.label }}</div>
          </label>
        </div>
      </div>

      <div class="section-card">
        <h2>2️⃣ Configure Filters</h2>
        <div class="filters-grid">
          <div class="filter-group">
            <label>📅 Date Range</label>
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

          <div class="filter-group" v-if="reportType === 'sales' || reportType === 'customers' || reportType === 'complete'">
            <label>👤 Customer</label>
            <select v-model="selectedCustomer" class="filter-select">
              <option :value="'all'">All Customers</option>
              <option v-for="customer in customersStore.customers" :key="customer.id" :value="customer.id">
                {{ customer.name }}
              </option>
            </select>
          </div>

          <div class="filter-group" v-if="reportType === 'purchases' || reportType === 'vendors' || reportType === 'complete'">
            <label>🏢 Vendor</label>
            <select v-model="selectedVendor" class="filter-select">
              <option :value="'all'">All Vendors</option>
              <option v-for="vendor in vendorsStore.vendors" :key="vendor.id" :value="vendor.id">
                {{ vendor.name }}
              </option>
            </select>
          </div>

          <div class="filter-group" v-if="reportType === 'sales' || reportType === 'inventory' || reportType === 'complete'">
            <label>📦 Product</label>
            <select v-model="selectedProduct" class="filter-select">
              <option :value="'all'">All Products</option>
              <option v-for="product in productsStore.products" :key="product.id" :value="product.id">
                {{ product.name }}
              </option>
            </select>
          </div>

          <div class="filter-group full-width">
            <button @click="resetFilters" class="reset-btn">🔄 Reset All Filters</button>
          </div>
        </div>
      </div>

      <div class="section-card">
        <h2>3️⃣ Report Options</h2>
        <div class="options-grid">
          <label class="checkbox-label">
            <input type="checkbox" v-model="includeSummary" />
            <span>Include Summary Sheet</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="includeDetails" />
            <span>Include Detailed Data</span>
          </label>
        </div>
      </div>

      <div class="section-card generate-section">
        <button @click="generateReport" :disabled="generating" class="generate-btn">
          <span v-if="!generating">📥 Generate & Download Report</span>
          <span v-else>⏳ Generating...</span>
        </button>
        <p class="help-text">Excel (.xlsx) file will be downloaded</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reports-module { padding: 1.5rem; background: #f8fafc; min-height: 100vh; }
.reports-header h1 { font-size: clamp(1.5rem, 4vw, 2rem); font-weight: 700; color: #0f172a; margin: 0; }
.subtitle { color: #64748b; margin-top: 0.5rem; font-size: clamp(0.85rem, 2vw, 0.95rem); }
.loading-state { display: flex; flex-direction: column; align-items: center; padding: 4rem; color: #64748b; }
.spinner { width: 48px; height: 48px; border: 4px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.reports-content { display: flex; flex-direction: column; gap: 1.5rem; }
.section-card { background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.section-card h2 { font-size: clamp(1.125rem, 3vw, 1.25rem); font-weight: 600; color: #0f172a; margin: 0 0 1.5rem 0; }
.report-types-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 160px), 1fr)); gap: 1rem; }
.report-type-card { padding: 1.5rem; border: 2px solid #e2e8f0; border-radius: 12px; cursor: pointer; transition: all 0.2s; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 0.75rem; }
.report-type-card:hover { border-color: #3b82f6; transform: translateY(-2px); }
.report-type-card.selected { border-color: #3b82f6; background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); }
.report-icon { font-size: 2.5rem; }
.report-label { font-size: clamp(0.8rem, 2vw, 0.875rem); font-weight: 600; color: #0f172a; }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr)); gap: 1rem; }
.filter-group { display: flex; flex-direction: column; gap: 0.5rem; }
.filter-group.full-width { grid-column: 1 / -1; }
.filter-group label { font-size: clamp(0.8rem, 2vw, 0.875rem); font-weight: 600; color: #64748b; }
.filter-select, .filter-input { padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: clamp(0.8rem, 2vw, 0.875rem); color: #0f172a; background: white; transition: border-color 0.2s; }
.filter-select:focus, .filter-input:focus { outline: none; border-color: #3b82f6; }
.reset-btn { padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #64748b 0%, #475569 100%); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: transform 0.2s; font-size: clamp(0.8rem, 2vw, 0.875rem); }
.reset-btn:hover { transform: translateY(-2px); }
.options-grid { display: flex; flex-wrap: wrap; gap: 2rem; }
.checkbox-label { display: flex; align-items: center; gap: 0.75rem; font-size: clamp(0.875rem, 2vw, 1rem); color: #0f172a; cursor: pointer; }
.checkbox-label input[type="checkbox"] { width: 20px; height: 20px; cursor: pointer; }
.generate-section { text-align: center; }
.generate-btn { padding: 1.25rem 3rem; background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; border: none; border-radius: 12px; font-size: clamp(1rem, 2.5vw, 1.125rem); font-weight: 700; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3); }
.generate-btn:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 6px 16px rgba(34, 197, 94, 0.4); }
.generate-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.help-text { margin-top: 1rem; color: #64748b; font-size: clamp(0.8rem, 2vw, 0.875rem); }
</style>
