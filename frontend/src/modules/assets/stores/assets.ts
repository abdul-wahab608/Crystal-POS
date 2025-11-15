import { defineStore } from 'pinia'
import type { Asset, CreateAssetRequest, UpdateAssetRequest } from '../types'
import api from '../../../shared/api/axios'

export const useAssetsStore = defineStore('assets', {
  state: () => ({
    assets: [] as Asset[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchAssets() {
      this.loading = true
      try {
        const res = await api.get<Asset[]>('/assets/')
        this.assets = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
      } finally {
        this.loading = false
      }
    },
    async createAsset(payload: CreateAssetRequest) {
      try {
        const res = await api.post<Asset>('/assets/', payload)
        this.assets.push(res.data)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async updateAsset(id: number, payload: UpdateAssetRequest) {
      try {
        const res = await api.patch<Asset>(`/assets/${id}/`, payload)
        const idx = this.assets.findIndex(a => a.id === id)
        if (idx !== -1) this.assets[idx] = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async deleteAsset(id: number) {
      try {
        await api.delete(`/assets/${id}/`)
        this.assets = this.assets.filter(a => a.id !== id)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
}) 