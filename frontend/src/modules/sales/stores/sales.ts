import { defineStore } from 'pinia'
import type { Sale, CreateSaleRequest, UpdateSaleRequest } from '../types'
import api from '../../../shared/api/axios'

export const useSalesStore = defineStore('sales', {
  state: () => ({
    sales: [] as Sale[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchSales() {
      this.loading = true
      this.error = null
      
      try {
        const res = await api.get<Sale[]>('/sales/')
        this.sales = res.data || []
      } catch (e: any) {
        if (e.response?.status === 403) {
          this.error = 'Access denied. Please check your permissions or login again.'
        } else {
          this.error = e.response?.data?.message || e.message
        }
        this.sales = []
      } finally {
        this.loading = false
      }
    },
    async createSale(payload: CreateSaleRequest) {
      try {
        const res = await api.post<Sale>('/sales/', payload)
        this.sales.push(res.data)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.response?.data || e.message
        throw e
      }
    },
    async updateSale(id: number, payload: UpdateSaleRequest) {
      try {
        const res = await api.patch<Sale>(`/sales/${id}/`, payload)
        const idx = this.sales.findIndex(s => s.id === id)
        if (idx !== -1) this.sales[idx] = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async deleteSale(id: number) {
      try {
        await api.delete(`/sales/${id}/`)
        this.sales = this.sales.filter(s => s.id !== id)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
}) 