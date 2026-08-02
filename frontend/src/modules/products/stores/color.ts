import { defineStore } from 'pinia'
import axios from '../../../shared/api/axios'
import type { Color } from '../types'

export const useColorStore = defineStore('color', {
  state: () => ({
    colors: [] as Color[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchColors() {
      this.loading = true
      try {
        const res = await axios.get('/products/colors/')
        this.colors = res.data
        this.error = null
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch colors'
      } finally {
        this.loading = false
      }
    },
    async addColor(name: string) {
      try {
        const res = await axios.post('/products/colors/', { name })
        this.colors.push(res.data)
        this.error = null
      } catch (err: any) {
        this.error = err.message || 'Failed to add color'
      }
    },
    async deleteColor(id: number) {
      try {
        await axios.delete(`/products/colors/${id}/`)
        this.colors = this.colors.filter(c => c.id !== id)
        this.error = null
      } catch (err: any) {
        this.error = err.message || 'Failed to delete color'
      }
    },
  },
})
