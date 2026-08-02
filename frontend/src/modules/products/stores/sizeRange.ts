import { defineStore } from 'pinia'
import axios from '../../../shared/api/axios'
import type { SizeRange } from '../types'

export const useSizeRangeStore = defineStore('sizeRange', {
  state: () => ({
    sizeRanges: [] as SizeRange[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchSizeRanges() {
      this.loading = true
      try {
        const res = await axios.get('/products/size-ranges/')
        this.sizeRanges = res.data
        this.error = null
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch size ranges'
      } finally {
        this.loading = false
      }
    },
    async addSizeRange(name: string) {
      try {
        const res = await axios.post('/products/size-ranges/', { name })
        this.sizeRanges.push(res.data)
        this.error = null
      } catch (err: any) {
        this.error = err.message || 'Failed to add size range'
      }
    },
    async deleteSizeRange(id: number) {
      try {
        await axios.delete(`/products/size-ranges/${id}/`)
        this.sizeRanges = this.sizeRanges.filter(sr => sr.id !== id)
        this.error = null
      } catch (err: any) {
        this.error = err.message || 'Failed to delete size range'
      }
    },
  },
})
