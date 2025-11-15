import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import VueApexCharts from 'vue3-apexcharts'

import App from './App.vue'
import router from './router'
import { permission } from './shared/directives/permission'
import { useAuthStore } from './shared/stores/auth'
import api from './shared/api/axios'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(VueApexCharts)

// Register permission directive
app.directive('permission', permission)

// Initialize authentication
const authStore = useAuthStore()

// Set up axios interceptors
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, logout user
      authStore.logout()
      router.push('/')
    }
    return Promise.reject(error)
  }
)

// Initialize auth state
authStore.initializeAuth()

app.mount('#app')
