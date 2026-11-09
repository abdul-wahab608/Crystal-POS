import { defineStore } from 'pinia'
import type {
  Sale, CreateSaleRequest, SaleFilters, CatalogProduct, CatalogSizeRange,
} from '../types'
import api from '../../../shared/api/axios'

export const useSalesStore = defineStore('sales', {
  state: () => ({
    sales: [] as Sale[],
    products: [] as CatalogProduct[],
    sizeRanges: [] as CatalogSizeRange[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchSales(filters: SaleFilters = {}) {
      this.loading = true
      try {
        const res = await api.get<Sale[]>('/sales/', { params: filters })
        this.sales = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.detail || e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async fetchCustomerSales(customerId: number): Promise<Sale[]> {
      const res = await api.get<Sale[]>('/sales/', { params: { customer: customerId } })
      return res.data
    },
    async fetchCatalog() {
      const [products, sizeRanges] = await Promise.all([
        api.get<CatalogProduct[]>('/products/'),
        api.get<CatalogSizeRange[]>('/products/size-ranges/'),
      ])
      this.products = products.data
      this.sizeRanges = sizeRanges.data
    },
    async createSale(payload: CreateSaleRequest) {
      const res = await api.post<Sale>('/sales/', payload)
      this.sales.unshift(res.data)
      return res.data
    },
    async deleteSale(id: number) {
      await api.delete(`/sales/${id}/`)
      this.sales = this.sales.filter(s => s.id !== id)
    },
  },
})
