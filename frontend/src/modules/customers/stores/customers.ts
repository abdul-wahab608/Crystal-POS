import { defineStore } from 'pinia'
import type { Customer, CreateCustomerRequest, UpdateCustomerRequest } from '../types'
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
        this.error = e.response?.data?.message || e.message
      } finally {
        this.loading = false
      }
    },
    async createCustomer(payload: CreateCustomerRequest) {
      try {
        const res = await api.post<Customer>('/customers/', payload)
        this.customers.push(res.data)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async updateCustomer(id: number, payload: UpdateCustomerRequest) {
      try {
        const res = await api.patch<Customer>(`/customers/${id}/`, payload)
        const idx = this.customers.findIndex(c => c.id === id)
        if (idx !== -1) this.customers[idx] = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async deleteCustomer(id: number) {
      try {
        await api.delete(`/customers/${id}/`)
        this.customers = this.customers.filter(c => c.id !== id)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
}) 