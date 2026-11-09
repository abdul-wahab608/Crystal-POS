import { defineStore } from 'pinia'
import type { Vendor, VendorFormPayload, VendorPayment, VendorPaymentPayload, VendorTransaction } from '../types'
import api from '../../../shared/api/axios'

export const useVendorsStore = defineStore('vendors', {
  state: () => ({
    vendors: [] as Vendor[],
    loading: false,
  }),
  actions: {
    async fetchVendors() {
      this.loading = true
      try {
        const res = await api.get<Vendor[]>('/vendors/')
        this.vendors = res.data
      } finally {
        this.loading = false
      }
    },
    async createVendor(payload: VendorFormPayload) {
      await api.post('/vendors/', payload)
      await this.fetchVendors()
    },
    async updateVendor(id: number, payload: Partial<VendorFormPayload>) {
      await api.patch(`/vendors/${id}/`, payload)
      await this.fetchVendors()
    },
    async deleteVendor(id: number) {
      await api.delete(`/vendors/${id}/`)
      await this.fetchVendors()
    },
    async fetchLedger(vendorId: number): Promise<VendorTransaction[]> {
      const res = await api.get<VendorTransaction[]>('/vendors/vendor-transactions/', { params: { vendor: vendorId } })
      return res.data
    },
    async fetchVendorPayments(vendorId: number): Promise<VendorPayment[]> {
      const res = await api.get<VendorPayment[]>('/payments/by_vendor/', { params: { vendor_id: vendorId } })
      return res.data
    },
    async recordPayment(payload: VendorPaymentPayload) {
      await api.post('/payments/', { ...payload, payment_type: 'OUTGOING' })
      await this.fetchVendors()
    },
  },
})
