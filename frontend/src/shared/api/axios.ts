import axios from 'axios'

// Detect if running in Electron or browser
const isElectron = !!(window as any).electronAPI

// Get base URL - use dynamic port in Electron, default to 8000 in browser
const getBaseURL = async () => {
  if (isElectron) {
    try {
      const config = await (window as any).electronAPI.getConfig()
      return `http://127.0.0.1:${config.backendPort}/api`
    } catch (error) {
      console.error('Failed to get config from Electron:', error)
      return 'http://localhost:8000/api'
    }
  }
  return 'http://localhost:8000/api'
}

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Default, will be updated
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Update base URL dynamically on initialization
getBaseURL().then(url => {
  api.defaults.baseURL = url
  console.log('API Base URL:', url)
})

// Request interceptor to add auth token
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

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Export both as default and named export for compatibility
export { api }
export default api 