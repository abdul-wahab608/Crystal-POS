import { defineStore } from 'pinia'
import type { Purchase, CreatePurchaseRequest, Product, SizeRange, Color, RawMaterialOption } from '../types'
import api from '../../../shared/api/axios'

export const usePurchasesStore = defineStore('purchases', {
  state: () => ({
    purchases: [] as Purchase[],
    products: [] as Product[],
    sizeRanges: [] as SizeRange[],
    colors: [] as Color[],
    rawMaterials: [] as RawMaterialOption[],
    loading: false,
  }),
  actions: {
    async fetchPurchases(filters: { unpaid?: boolean } = {}) {
      this.loading = true
      try {
        const res = await api.get<Purchase[]>('/purchases/', { params: filters.unpaid ? { unpaid: true } : undefined })
        this.purchases = res.data
      } finally {
        this.loading = false
      }
    },
    async fetchOpenBills(vendorId: number) {
      const res = await api.get<Purchase[]>('/purchases/', { params: { unpaid: true } })
      return res.data.filter(bill => bill.vendor === vendorId)
    },
    async fetchLookups() {
      const [products, sizeRanges, colors, rawMaterials] = await Promise.all([
        api.get<Product[]>('/products/'),
        api.get<SizeRange[]>('/products/size-ranges/'),
        api.get<Color[]>('/products/colors/'),
        api.get<RawMaterialOption[]>('/raw-materials/materials/'),
      ])
      this.products = products.data
      this.sizeRanges = sizeRanges.data
      this.colors = colors.data
      this.rawMaterials = rawMaterials.data
    },
    async createPurchase(payload: CreatePurchaseRequest) {
      const res = await api.post<Purchase>('/purchases/', payload)
      this.purchases.unshift(res.data)
    },
    async deletePurchase(id: number) {
      await api.delete(`/purchases/${id}/`)
      this.purchases = this.purchases.filter(p => p.id !== id)
    },
  },
})
