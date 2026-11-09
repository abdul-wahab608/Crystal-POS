import { defineStore } from 'pinia'
import type { Payment, PaymentRequest, PaymentFilters, Vendor, BankAccount } from '../types'
import api from '../../../shared/api/axios'

export const usePaymentsStore = defineStore('payments', {
  state: () => ({
    payments: [] as Payment[],
    vendors: [] as Vendor[],
    bankAccounts: [] as BankAccount[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchPayments(filters: PaymentFilters = {}) {
      this.loading = true
      try {
        const res = await api.get<Payment[]>('/payments/', { params: filters })
        this.payments = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.detail || e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async fetchFormOptions() {
      const [vendors, banks] = await Promise.all([
        api.get<Vendor[]>('/vendors/'),
        api.get<BankAccount[]>('/bank-accounts/'),
      ])
      this.vendors = vendors.data
      this.bankAccounts = banks.data.filter((b: any) => b.is_active !== false)
    },
    async createPayment(payload: PaymentRequest) {
      const res = await api.post<{ id: number }>('/payments/', payload)
      return res.data
    },
    async deletePayment(id: number) {
      await api.delete(`/payments/${id}/`)
      this.payments = this.payments.filter(p => p.id !== id)
    },
  },
})
