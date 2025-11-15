import { saveAs } from 'file-saver'

export interface ExportOptions {
  filename?: string
  includeHeaders?: boolean
}

export function exportToCSV(data: any[], options: ExportOptions = {}) {
  const { filename = 'export.csv', includeHeaders = true } = options
  
  if (data.length === 0) {
    throw new Error('No data to export')
  }

  const headers = Object.keys(data[0])
  let csvContent = ''

  if (includeHeaders) {
    csvContent += headers.join(',') + '\n'
  }

  data.forEach(row => {
    const values = headers.map(header => {
      const value = row[header]
      // Escape commas and quotes
      if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
        return `"${value.replace(/"/g, '""')}"`
      }
      return value
    })
    csvContent += values.join(',') + '\n'
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  saveAs(blob, filename)
}

export function exportToJSON(data: any[], options: ExportOptions = {}) {
  const { filename = 'export.json' } = options
  
  const jsonContent = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonContent], { type: 'application/json' })
  saveAs(blob, filename)
}

export function generateReport(data: any[], reportType: string, options: ExportOptions = {}) {
  const timestamp = new Date().toISOString().split('T')[0]
  const filename = `${reportType}_${timestamp}.csv`
  
  return exportToCSV(data, { ...options, filename })
}

// Specific report generators
export function generateSalesReport(sales: any[]) {
  const reportData = sales.map(sale => ({
    'Sale ID': sale.id,
    'Date': sale.date,
    'Customer': sale.customer_name,
    'Total Amount': sale.total_amount,
    'Payment Method': sale.payment_method,
    'Status': sale.status
  }))
  
  return generateReport(reportData, 'sales_report')
}

export function generateInventoryReport(products: any[]) {
  const reportData = products.map(product => ({
    'Product ID': product.id,
    'Name': product.name,
    'Unit': product.unit,
    'COP (Cost of Production)': product.cop,
    'Quantity': product.quantity,
    'Total Value': product.cop * product.quantity,
    'Last Updated': product.last_updated
  }))
  
  return generateReport(reportData, 'inventory_report')
}

export function generateCustomerReport(customers: any[]) {
  const reportData = customers.map(customer => ({
    'Customer ID': customer.id,
    'Name': customer.name,
    'Email': customer.email,
    'Phone': customer.phone,
    'Address': customer.address,
    'Total Purchases': customer.total_purchases || 0,
    'Last Purchase': customer.last_purchase || 'Never'
  }))
  
  return generateReport(reportData, 'customer_report')
} 