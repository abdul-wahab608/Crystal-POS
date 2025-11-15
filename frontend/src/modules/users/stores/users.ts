import { defineStore } from 'pinia'
import type { User, CreateUserRequest, UpdateUserRequest } from '../types'
import api from '../../../shared/api/axios'

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [] as User[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchUsers() {
      this.loading = true
      try {
        const res = await api.get<User[]>('/users/')
        this.users = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
      } finally {
        this.loading = false
      }
    },
    async createUser(payload: CreateUserRequest) {
      try {
        const res = await api.post<User>('/users/', payload)
        this.users.push(res.data)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async updateUser(id: number, payload: UpdateUserRequest) {
      try {
        const res = await api.patch<User>(`/users/${id}/`, payload)
        const idx = this.users.findIndex(u => u.id === id)
        if (idx !== -1) this.users[idx] = res.data
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    },
    async deleteUser(id: number) {
      try {
        await api.delete(`/users/${id}/`)
        this.users = this.users.filter(u => u.id !== id)
        this.error = null
      } catch (e: any) {
        this.error = e.response?.data?.message || e.message
        throw e
      }
    }
  }
}) 