import { defineStore } from 'pinia'
import type { Purchase, CreatePurchaseRequest, UpdatePurchaseRequest } from '../types'
import api from '../../../shared/api/axios'

export const usePurchasesStore = defineStore('purchases', {
  state: () => ({
    purchases: [] as Purchase[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchPurchases() {
      this.loading = true
      try {
        const res = await api.get<Purchase[]>('/purchases/')
        this.purchases = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
      } finally {
        this.loading = false
      }
    },
    async createPurchase(payload: CreatePurchaseRequest) {
      try {
        const res = await api.post<Purchase>('/purchases/', payload)
        this.purchases.push(res.data)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async updatePurchase(id: number, payload: UpdatePurchaseRequest) {
      try {
        const res = await api.patch<Purchase>(`/purchases/${id}/`, payload)
        const idx = this.purchases.findIndex(p => p.id === id)
        if (idx !== -1) this.purchases[idx] = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async deletePurchase(id: number) {
      try {
        await api.delete(`/purchases/${id}/`)
        this.purchases = this.purchases.filter(p => p.id !== id)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
}) 