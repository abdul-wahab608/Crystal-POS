import { defineStore } from 'pinia'
import type { Bill, Payment } from '../types/billing'
import api from '../../../shared/api/axios'

export const useBillStore = defineStore('bill', {
  state: () => ({
    bills: [] as Bill[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchBills() {
      this.loading = true
      this.error = null
      try {
        const res = await api.get<Bill[]>('/billing/bills/')
        this.bills = res.data || []
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        this.bills = []
      } finally {
        this.loading = false
      }
    },
    async createBill(payload: Partial<Bill>) {
      try {
        const res = await api.post<Bill>('/billing/bills/', payload)
        this.bills.push(res.data)
        this.error = null
        return res.data
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async addPayment(payload: Partial<Payment>) {
      try {
        const res = await api.post<Payment>('/billing/payments/', payload)
        this.error = null
        return res.data
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async fetchBill(id: number) {
      try {
        const res = await api.get<Bill>(`/billing/bills/${id}/`)
        return res.data
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
})
