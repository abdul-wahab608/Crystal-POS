import { defineStore } from 'pinia'
import type { Report, CreateReportRequest, UpdateReportRequest } from '../types'
import api from '../../../shared/api/axios'

export const useReportsStore = defineStore('reports', {
  state: () => ({
    reports: [] as Report[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchReports() {
      this.loading = true
      try {
        const res = await api.get<Report[]>('/reports/')
        this.reports = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
      } finally {
        this.loading = false
      }
    },
    async createReport(payload: CreateReportRequest) {
      try {
        const res = await api.post<Report>('/reports/', payload)
        this.reports.push(res.data)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async updateReport(id: number, payload: UpdateReportRequest) {
      try {
        const res = await api.patch<Report>(`/reports/${id}/`, payload)
        const idx = this.reports.findIndex(r => r.id === id)
        if (idx !== -1) this.reports[idx] = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async deleteReport(id: number) {
      try {
        await api.delete(`/reports/${id}/`)
        this.reports = this.reports.filter(r => r.id !== id)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
}) 