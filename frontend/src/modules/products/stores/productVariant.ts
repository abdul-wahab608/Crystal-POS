import { defineStore } from 'pinia'
import axios from '../../../shared/api/axios'
import type { VariantRecord } from '../types'

export const useProductVariantStore = defineStore('productVariant', {
  state: () => ({
    variants: [] as VariantRecord[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchVariants(productId?: number) {
      this.loading = true
      try {
        let url = '/products/product-variants/'
        if (productId) url += `?product=${productId}`
        const res = await axios.get(url)
        this.variants = res.data
        this.error = null
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch variants'
      } finally {
        this.loading = false
      }
    },
  },
})
