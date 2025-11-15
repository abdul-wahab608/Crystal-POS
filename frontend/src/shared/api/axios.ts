import axios from 'axios'
import offlineManager from '../utils/offlineManager'
import indexedDBManager from '../utils/indexedDBManager'

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
  async (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Handle offline mode
    if (!offlineManager.checkOnlineStatus()) {
      // Check if we have cached data for GET requests
      if (config.method?.toLowerCase() === 'get') {
        const cacheKey = `${config.method}_${config.url}`;
        const cachedData = await indexedDBManager.getCachedResponse(cacheKey);
        
        if (cachedData) {
          console.log('📦 Using cached data for:', config.url);
          // Return cached data as a fulfilled promise
          return Promise.reject({
            config,
            response: {
              data: cachedData,
              status: 200,
              statusText: 'OK (Cached)',
              headers: {},
              config
            },
            isCached: true
          });
        }
      }

      // For POST/PUT/DELETE, add to sync queue
      if (['post', 'put', 'delete', 'patch'].includes(config.method?.toLowerCase() || '')) {
        offlineManager.addToSyncQueue({
          method: config.method,
          url: config.baseURL + config.url,
          data: config.data
        });

        return Promise.reject({
          message: 'Request queued for sync when online',
          isOffline: true,
          config
        });
      }

      return Promise.reject({
        message: 'No internet connection',
        isOffline: true,
        config
      });
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  async (response) => {
    // Cache GET responses
    if (response.config.method?.toLowerCase() === 'get' && response.data) {
      const cacheKey = `${response.config.method}_${response.config.url}`;
      await indexedDBManager.cacheResponse(cacheKey, response.data, 1800000); // 30 min TTL
    }

    return response
  },
  (error) => {
    // Handle cached response
    if (error.isCached) {
      return Promise.resolve(error.response);
    }

    // Handle offline mode
    if (error.isOffline) {
      console.warn('⚠️ Offline:', error.message);
      return Promise.reject(error);
    }

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