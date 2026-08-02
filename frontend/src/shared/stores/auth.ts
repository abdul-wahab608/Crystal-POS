import { defineStore } from 'pinia'
import api from '../api/axios'

interface User {
  id: number
  username: string
  email: string
  role: 'ADMIN' | 'MANAGER' | 'CASHIER' | 'STAFF'
  is_superuser?: boolean
}

interface LoginRequest {
  username: string
  password: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    token: localStorage.getItem('auth_token') || null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    isAdmin: (state) => state.user?.role === 'ADMIN',
    isSuperuser: (state) => state.user?.is_superuser === true,
    isManager: (state) => ['ADMIN', 'MANAGER'].includes(state.user?.role || ''),
    isCashier: (state) => ['ADMIN', 'MANAGER', 'CASHIER'].includes(state.user?.role || ''),
    canManageUsers: (state) => ['ADMIN'].includes(state.user?.role || ''),
    canManageProducts: (state) => ['ADMIN', 'MANAGER'].includes(state.user?.role || ''),
    canManageCustomers: (state) => ['ADMIN', 'MANAGER'].includes(state.user?.role || ''),
    canManageVendors: (state) => ['ADMIN', 'MANAGER'].includes(state.user?.role || ''),
    canManageSales: (state) => ['ADMIN', 'MANAGER', 'CASHIER', 'STAFF'].includes(state.user?.role || ''),
    canManagePurchases: (state) => ['ADMIN', 'MANAGER'].includes(state.user?.role || ''),
    canManagePayments: (state) => ['ADMIN', 'MANAGER', 'CASHIER'].includes(state.user?.role || ''),
    canViewReports: (state) => ['ADMIN', 'MANAGER'].includes(state.user?.role || ''),
    canManageAssets: (state) => ['ADMIN', 'MANAGER'].includes(state.user?.role || ''),
    canImport: (state) => state.user?.is_superuser === true,
  },

  actions: {
    async login(payload: LoginRequest) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.post('/users/auth/login/', payload)
        const { token, user } = response.data
        
        this.token = token
        this.user = user
        localStorage.setItem('auth_token', token)
        
        // Set the token in axios headers for future requests
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        return response.data
      } catch (e: any) {
        this.error = e.response?.data?.message || 'Login failed'
        throw e
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        if (this.token) {
          await api.post('/users/auth/logout/')
        }
      } catch (e) {
      } finally {
        this.user = null
        this.token = null
        this.error = null
        localStorage.removeItem('auth_token')
        
        // Remove the token from axios headers
        delete api.defaults.headers.common['Authorization']
      }
    },

    async fetchCurrentUser() {
      if (!this.token) return
      
      try {
        const response = await api.get('/users/auth/me/')
        this.user = response.data
      } catch (e) {
        console.log('Failed to fetch current user:', e)
        this.logout()
      }
    },

    hasPermission(permission: string): boolean {
      const permissionMap: Record<string, boolean> = {
        'manage_users': this.canManageUsers,
        'manage_products': this.canManageProducts,
        'manage_customers': this.canManageCustomers,
        'manage_vendors': this.canManageVendors,
        'manage_sales': this.canManageSales,
        'manage_purchases': this.canManagePurchases,
        'manage_payments': this.canManagePayments,
        'view_reports': this.canViewReports,
        'manage_assets': this.canManageAssets,
      }
      
      return permissionMap[permission] || false
    },

    // Initialize auth state on app startup
    async initializeAuth() {
      if (this.token) {
        // Set the token in axios headers
        api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        // Try to fetch current user
        await this.fetchCurrentUser()
      }
    }
  }
}) 