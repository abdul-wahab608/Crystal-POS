import { defineStore } from 'pinia'
import type { CreateProductionRunRequest, Product, ProductionRun, RawMaterialOption } from '../types'
import api from '../../../shared/api/axios'

export const useProductionStore = defineStore('production', {
  state: () => ({
    runs: [] as ProductionRun[],
    products: [] as Product[],
    rawMaterials: [] as RawMaterialOption[],
    loading: false,
  }),
  actions: {
    async fetchRuns() {
      this.loading = true
      try {
        const res = await api.get<ProductionRun[]>('/production/runs/')
        this.runs = res.data
      } finally {
        this.loading = false
      }
    },
    async fetchLookups() {
      const [products, rawMaterials] = await Promise.all([
        api.get<Product[]>('/products/'),
        api.get<RawMaterialOption[]>('/raw-materials/materials/'),
      ])
      this.products = products.data
      this.rawMaterials = rawMaterials.data
    },
    async createRun(payload: CreateProductionRunRequest) {
      const res = await api.post<ProductionRun>('/production/runs/', payload)
      this.runs.unshift(res.data)
      await this.fetchLookups()
    },
    async deleteRun(id: number) {
      await api.delete(`/production/runs/${id}/`)
      this.runs = this.runs.filter(run => run.id !== id)
      await this.fetchLookups()
    },
  },
})
