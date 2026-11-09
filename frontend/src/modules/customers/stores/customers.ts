import { defineStore } from 'pinia'
import type { Customer, CustomerRequest, CustomerLedger } from '../types'
import api from '../../../shared/api/axios'

export const useCustomersStore = defineStore('customers', {
  state: () => ({
    customers: [] as Customer[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchCustomers() {
      this.loading = true
      try {
        const res = await api.get<Customer[]>('/customers/')
        this.customers = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.detail || e.message
      } finally {
        this.loading = false
      }
    },
    async fetchLedger(id: number) {
      const res = await api.get<CustomerLedger>(`/customers/${id}/ledger/`)
      return res.data
    },
    async createCustomer(payload: CustomerRequest) {
      const res = await api.post<Customer>('/customers/', payload)
      this.customers.push(res.data)
      return res.data
    },
    async updateCustomer(id: number, payload: Partial<CustomerRequest>) {
      const res = await api.patch<Customer>(`/customers/${id}/`, payload)
      const idx = this.customers.findIndex(c => c.id === id)
      if (idx !== -1) this.customers[idx] = res.data
      return res.data
    },
    async deleteCustomer(id: number) {
      await api.delete(`/customers/${id}/`)
      this.customers = this.customers.filter(c => c.id !== id)
    },
  },
})
