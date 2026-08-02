import { defineStore } from 'pinia'
import axios from '../../../shared/api/axios'
import type { ProductVariant } from '../types'

export const useProductVariantStore = defineStore('productVariant', {
  state: () => ({
    variants: [] as ProductVariant[],
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
    async addVariant(variant: Partial<ProductVariant>) {
      try {
        const res = await axios.post('/products/product-variants/', variant)
        this.variants.push(res.data)
        this.error = null
      } catch (err: any) {
        this.error = err.message || 'Failed to add variant'
      }
    },
    async deleteVariant(id: number) {
      try {
        await axios.delete(`/products/product-variants/${id}/`)
        this.variants = this.variants.filter(v => v.id !== id)
        this.error = null
      } catch (err: any) {
        this.error = err.message || 'Failed to delete variant'
      }
    },
  },
})
