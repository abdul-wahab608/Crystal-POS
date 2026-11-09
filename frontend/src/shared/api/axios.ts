import axios, { type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import indexedDBManager from '../utils/indexedDBManager'
import offlineManager, { QueuedWriteError, type WriteMethod } from '../utils/offlineManager'
import { useToastStore } from '../stores/toast'
import { API_BASE_URL } from './baseUrl'

const WRITE_METHODS: string[] = ['post', 'put', 'patch', 'delete']

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

const cacheKeyFor = (config: InternalAxiosRequestConfig) =>
  `${config.method?.toUpperCase()} ${api.getUri(config)}`

const isQueueable = (config: InternalAxiosRequestConfig) =>
  WRITE_METHODS.includes(config.method?.toLowerCase() ?? '') &&
  !(config.url ?? '').includes('/auth/') &&
  !(config.data instanceof FormData)

const serializedBody = (data: unknown) =>
  typeof data === 'string' && data !== '' ? JSON.parse(data) : data

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  async (response) => {
    if (response.config.method?.toLowerCase() === 'get' && response.data) {
      await indexedDBManager.cacheResponse(cacheKeyFor(response.config), response.data)
    }
    return response
  },
  async (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        localStorage.removeItem('auth_token')
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }

    const config = error.config as InternalAxiosRequestConfig | undefined
    if (!config || axios.isCancel(error)) return Promise.reject(error)

    void offlineManager.checkReachability()
    const method = config.method?.toLowerCase()

    if (method === 'get') {
      const cached = await indexedDBManager.getCachedResponse(cacheKeyFor(config))
      if (cached === null) return Promise.reject(error)
      return {
        data: cached,
        status: 200,
        statusText: 'OK',
        headers: {},
        config,
        request: error.request,
      } as AxiosResponse
    }

    if (isQueueable(config)) {
      await offlineManager.enqueue(method as WriteMethod, api.getUri(config), serializedBody(config.data))
      useToastStore().warning('Saved offline', 'It will sync when the server is reachable.')
      throw new QueuedWriteError()
    }

    return Promise.reject(error)
  }
)

export { api }
export default api
