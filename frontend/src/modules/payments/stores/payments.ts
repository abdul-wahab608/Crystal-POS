import { defineStore } from 'pinia'
import type { Payment, CreatePaymentRequest, UpdatePaymentRequest } from '../types'
import api from '../../../shared/api/axios'

export const usePaymentsStore = defineStore('payments', {
  state: () => ({
    payments: [] as Payment[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchPayments() {
      this.loading = true
      try {
        const res = await api.get<Payment[]>('/payments/')
        this.payments = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
      } finally {
        this.loading = false
      }
    },
    async createPayment(payload: CreatePaymentRequest) {
      try {
        const res = await api.post<Payment>('/payments/', payload)
        this.payments.push(res.data)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async updatePayment(id: number, payload: UpdatePaymentRequest) {
      try {
        const res = await api.patch<Payment>(`/payments/${id}/`, payload)
        const idx = this.payments.findIndex(p => p.id === id)
        if (idx !== -1) this.payments[idx] = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async deletePayment(id: number) {
      try {
        await api.delete(`/payments/${id}/`)
        this.payments = this.payments.filter(p => p.id !== id)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
}) 