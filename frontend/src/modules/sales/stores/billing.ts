import { defineStore } from 'pinia'
import type { Invoice, Payment } from '../types/billing'
import api from '../../../shared/api/axios'

export const useInvoiceStore = defineStore('invoice', {
  state: () => ({
    invoices: [] as Invoice[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchInvoices() {
      this.loading = true
      this.error = null
      try {
        const res = await api.get<Invoice[]>('/billing/invoices/')
        this.invoices = res.data || []
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        this.invoices = []
      } finally {
        this.loading = false
      }
    },
    async createInvoice(payload: Partial<Invoice>) {
      try {
        const res = await api.post<Invoice>('/billing/invoices/', payload)
        this.invoices.push(res.data)
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
    async fetchInvoice(id: number) {
      try {
        const res = await api.get<Invoice>(`/billing/invoices/${id}/`)
        return res.data
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
})
