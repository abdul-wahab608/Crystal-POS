/**
 * Export store for managing data exports to CSV/Excel
 */
import { defineStore } from 'pinia'
import api from '../api/axios'

export type ExportFormat = 'csv' | 'excel'

export interface ExportField {
  key: string
  label: string
  selected: boolean
}

export const useExportStore = defineStore('export', {
  state: () => ({
    exporting: false,
    error: null as string | null,
  }),

  actions: {
    /**
     * Export data from an entity endpoint
     * @param entityType - The entity type (customers, vendors, products, raw_materials, assets)
     * @param format - Export format (csv or excel)
     * @param fields - Optional array of field names to export
     */
    async exportData(
      entityType: string,
      format: ExportFormat = 'csv',
      fields?: string[]
    ) {
      this.exporting = true
      this.error = null

      // Map entity types to API endpoints
      const endpointMap: Record<string, string> = {
        customers: '/api/customers',
        vendors: '/api/vendors',
        products: '/api/products',
        raw_materials: '/api/raw-materials',
        assets: '/api/assets',
      }

      const endpoint = endpointMap[entityType]
      if (!endpoint) {
        this.error = `Unknown entity type: ${entityType}`
        this.exporting = false
        return
      }

      try {
        // Build query params
        const params = new URLSearchParams()
        params.append('export_format', format === 'excel' ? 'excel' : 'csv')
        if (fields && fields.length > 0) {
          params.append('fields', fields.join(','))
        }

        const response = await api.get(`${endpoint}/export/?${params.toString()}`, {
          responseType: 'blob',
        })

        // Get filename from response headers or generate one
        const contentDisposition = response.headers['content-disposition']
        let filename = `${entityType}.${format === 'excel' ? 'xlsx' : 'csv'}`
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="(.+)"/)
          if (match) {
            filename = match[1]
          }
        }

        // Download the file
        const blob = new Blob([response.data], {
          type: format === 'excel'
            ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            : 'text/csv;charset=utf-8;',
        })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        return true
      } catch (e: any) {
        this.error = e.response?.data?.error || e.message || 'Export failed'
        throw new Error(this.error!)
      } finally {
        this.exporting = false
      }
    },
  },
})
