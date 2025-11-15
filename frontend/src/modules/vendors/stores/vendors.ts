import { defineStore } from 'pinia'
import type { Vendor, CreateVendorRequest, UpdateVendorRequest } from '../types'
import api from '../../../shared/api/axios'

export const useVendorsStore = defineStore('vendors', {
  state: () => ({
    vendors: [] as Vendor[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchVendors() {
      this.loading = true
      try {
        const res = await api.get<Vendor[]>('/vendors/')
        this.vendors = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
      } finally {
        this.loading = false
      }
    },
    async createVendor(payload: CreateVendorRequest) {
      try {
        const res = await api.post<Vendor>('/vendors/', payload)
        this.vendors.push(res.data)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async updateVendor(id: number, payload: UpdateVendorRequest) {
      try {
        const res = await api.patch<Vendor>(`/vendors/${id}/`, payload)
        const idx = this.vendors.findIndex(v => v.id === id)
        if (idx !== -1) this.vendors[idx] = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async deleteVendor(id: number) {
      try {
        await api.delete(`/vendors/${id}/`)
        this.vendors = this.vendors.filter(v => v.id !== id)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
}) 