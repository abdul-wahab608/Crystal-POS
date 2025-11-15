import { defineStore } from 'pinia'
import api from '@/shared/api/axios'
import type { Product, CreateProductRequest, UpdateProductRequest } from '../types'

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [] as Product[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchProducts() {
      this.loading = true
      this.error = null
      
      try {
        const res = await api.get<Product[]>('/products/')
        this.products = res.data || []
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        this.products = []
      } finally {
        this.loading = false
      }
    },
    async createProduct(payload: CreateProductRequest) {
      try {
        // Check for existing product with same name, unit, and cop
        const existing = this.products.find(p => p.name === payload.name && p.unit === payload.unit && p.cop === payload.cop)
        if (existing) {
          // Update the quantity (replace, not increment)
          await this.updateProduct(existing.id, { ...payload })
          return existing
        }
        const res = await api.post<Product>('/products/', payload)
        if (!Array.isArray(this.products)) {
          this.products = []
        }
        this.products.push(res.data)
        this.error = null
        return res.data
      } catch (e: any) {
        this.error = e.response?.data?.message || e.response?.data || e.message
        throw e
      }
    },
    async updateProduct(id: number, payload: UpdateProductRequest) {
      try {
        const res = await api.patch<Product>(`/products/${id}/`, payload)
        
        // Ensure products is an array
        if (!Array.isArray(this.products)) {
          this.products = []
        }
        
        const idx = this.products.findIndex(p => p.id === id)
        if (idx !== -1) this.products[idx] = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async deleteProduct(id: number) {
      try {
        await api.delete(`/products/${id}/`)
        
        // Ensure products is an array
        if (!Array.isArray(this.products)) {
          this.products = []
        }
        
        this.products = this.products.filter(p => p.id !== id)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
}) 