import { describe, it, expect, beforeEach, vi } from 'vitest'
import { AxiosError } from 'axios'
import { setActivePinia, createPinia } from 'pinia'

const db = vi.hoisted(() => ({ rows: new Map<string, Map<unknown, any>>() }))

vi.mock('../../utils/indexedDBManager', () => {
  const table = (name: string) => {
    if (!db.rows.has(name)) db.rows.set(name, new Map())
    return db.rows.get(name)!
  }
  return {
    default: {
      getAll: async (store: string) => [...table(store).values()],
      save: async (store: string, row: any) => {
        table(store).set(row.seq ?? row.key, row)
      },
      cacheResponse: async (key: string, data: unknown) => {
        table('cache').set(key, { key, data })
      },
      getCachedResponse: async (key: string) => table('cache').get(key)?.data ?? null,
    },
  }
})

vi.mock('../../utils/offlineManager', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../utils/offlineManager')>()
  return {
    ...actual,
    default: { enqueue: vi.fn(), checkReachability: vi.fn() },
  }
})

import api from '../axios'
import offlineManager, { QueuedWriteError } from '../../utils/offlineManager'

const networkError = (config: any) => new AxiosError('Network Error', 'ERR_NETWORK', config)

const respond = (config: any, status: number, data: unknown) => ({
  data,
  status,
  statusText: String(status),
  headers: {},
  config,
})

describe('api offline behaviour', () => {
  let adapter: ReturnType<typeof vi.fn>

  beforeEach(() => {
    setActivePinia(createPinia())
    db.rows.clear()
    vi.clearAllMocks()
    adapter = vi.fn()
    api.defaults.adapter = adapter as any
  })

  it('queues a write on network error and rejects with QueuedWriteError', async () => {
    adapter.mockImplementation(async (config) => {
      throw networkError(config)
    })

    const err = await api.post('/customers/', { name: 'Ali' }).catch(e => e)

    expect(err).toBeInstanceOf(QueuedWriteError)
    expect(offlineManager.enqueue).toHaveBeenCalledWith('post', 'http://localhost:8010/api/customers/', { name: 'Ali' })
    expect(offlineManager.checkReachability).toHaveBeenCalled()
  })

  it('does not queue auth requests', async () => {
    adapter.mockImplementation(async (config) => {
      throw networkError(config)
    })

    const err = await api.post('/users/auth/login/', { username: 'a' }).catch(e => e)

    expect(err).toBeInstanceOf(AxiosError)
    expect(err).not.toBeInstanceOf(QueuedWriteError)
    expect(offlineManager.enqueue).not.toHaveBeenCalled()
  })

  it('does not queue a write that the server rejected', async () => {
    adapter.mockImplementation(async (config) => {
      const error = new AxiosError('Bad Request', 'ERR_BAD_REQUEST', config, null, respond(config, 400, {}) as any)
      throw error
    })

    const err = await api.post('/customers/', {}).catch(e => e)

    expect(err).not.toBeInstanceOf(QueuedWriteError)
    expect(offlineManager.enqueue).not.toHaveBeenCalled()
  })

  it('falls back to the cached GET response when the network fails, keyed by query params', async () => {
    adapter.mockImplementation(async (config) => respond(config, 200, [{ id: 1, page: config.params?.page }]))
    await api.get('/customers/', { params: { page: 1 } })

    adapter.mockImplementation(async (config) => {
      throw networkError(config)
    })

    const cached = await api.get('/customers/', { params: { page: 1 } })
    expect(cached.data).toEqual([{ id: 1, page: 1 }])

    await expect(api.get('/customers/', { params: { page: 2 } })).rejects.toBeInstanceOf(AxiosError)
  })

  it('rejects a GET network error when nothing is cached', async () => {
    adapter.mockImplementation(async (config) => {
      throw networkError(config)
    })

    await expect(api.get('/products/')).rejects.toBeInstanceOf(AxiosError)
  })
})
