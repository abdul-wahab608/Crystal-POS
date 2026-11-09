import { describe, it, expect, beforeEach, vi } from 'vitest'
import type { QueuedWrite } from '../offlineManager'

const db = vi.hoisted(() => ({ rows: new Map<string, Map<unknown, any>>() }))

vi.mock('../indexedDBManager', () => {
  const table = (name: string) => {
    if (!db.rows.has(name)) db.rows.set(name, new Map())
    return db.rows.get(name)!
  }
  return {
    default: {
      save: async (store: string, row: any) => {
        table(store).set(row.seq ?? row.key, structuredClone(row))
      },
      getAll: async (store: string) => [...table(store).values()].map(r => structuredClone(r)),
      delete: async (store: string, id: unknown) => {
        table(store).delete(id)
      },
    },
  }
})

vi.mock('axios', () => ({
  default: { get: vi.fn(), request: vi.fn() },
}))

const ok = (status: number, data: unknown = {}) => ({ status, data })

describe('offlineManager', () => {
  let offlineManager: typeof import('../offlineManager').default
  let axios: { get: ReturnType<typeof vi.fn>; request: ReturnType<typeof vi.fn> }

  beforeEach(async () => {
    vi.resetModules()
    db.rows.clear()
    localStorage.clear()
    const { createPinia, setActivePinia } = await import('pinia')
    setActivePinia(createPinia())
    offlineManager = (await import('../offlineManager')).default
    axios = (await import('axios')).default as any
    axios.get.mockReset()
    axios.request.mockReset()
  })

  it('replays queued writes FIFO and removes them after success', async () => {
    await offlineManager.enqueue('post', 'http://localhost:8010/api/customers/', { name: 'A' })
    await offlineManager.enqueue('patch', 'http://localhost:8010/api/customers/1/', { name: 'B' })
    await offlineManager.enqueue('delete', 'http://localhost:8010/api/customers/2/', undefined)
    axios.request.mockResolvedValue(ok(200))

    await offlineManager.flush()

    expect(axios.request.mock.calls.map(c => c[0].method)).toEqual(['post', 'patch', 'delete'])
    expect(axios.request.mock.calls.map(c => c[0].url)).toEqual([
      'http://localhost:8010/api/customers/',
      'http://localhost:8010/api/customers/1/',
      'http://localhost:8010/api/customers/2/',
    ])
    expect(axios.request.mock.calls[0][0].data).toEqual({ name: 'A' })
    expect(offlineManager.getStatus().pending).toEqual([])
    expect(offlineManager.getStatus().failed).toEqual([])
  })

  it('sends the auth token that is current at send time', async () => {
    await offlineManager.enqueue('post', 'http://localhost:8010/api/sales/', {})
    localStorage.setItem('auth_token', 'fresh-token')
    axios.request.mockResolvedValue(ok(201))

    await offlineManager.flush()

    expect(axios.request.mock.calls[0][0].headers).toEqual({ Authorization: 'Bearer fresh-token' })
  })

  it('moves a 4xx write to the failed list and keeps replaying the rest', async () => {
    await offlineManager.enqueue('post', 'http://localhost:8010/api/customers/', { name: '' })
    await offlineManager.enqueue('post', 'http://localhost:8010/api/customers/', { name: 'Valid' })
    axios.request
      .mockResolvedValueOnce(ok(400, { name: ['This field may not be blank.'] }))
      .mockResolvedValueOnce(ok(201))

    await offlineManager.flush()

    const status = offlineManager.getStatus()
    expect(axios.request).toHaveBeenCalledTimes(2)
    expect(status.pending).toEqual([])
    expect(status.failed).toHaveLength(1)
    expect(status.failed[0].data).toEqual({ name: '' })
    expect(status.failed[0].failureReason).toContain('HTTP 400')
    expect(db.rows.get('syncQueue')!.size).toBe(1)
  })

  it('stops replay on a network error and keeps the item pending', async () => {
    await offlineManager.enqueue('post', 'http://localhost:8010/api/customers/', { name: 'A' })
    await offlineManager.enqueue('post', 'http://localhost:8010/api/customers/', { name: 'B' })
    axios.request.mockRejectedValueOnce(new Error('Network Error'))

    await offlineManager.flush()

    expect(axios.request).toHaveBeenCalledTimes(1)
    expect(offlineManager.getStatus().pending).toHaveLength(2)
    expect(offlineManager.getStatus().online).toBe(false)
  })

  it('retries 5xx responses up to the limit before marking failed', async () => {
    await offlineManager.enqueue('put', 'http://localhost:8010/api/sales/1/', {})
    axios.request.mockResolvedValue(ok(500))

    await offlineManager.flush()
    await offlineManager.flush()
    expect(offlineManager.getStatus().pending).toHaveLength(1)

    await offlineManager.flush()
    expect(offlineManager.getStatus().pending).toEqual([])
    expect(offlineManager.getStatus().failed).toHaveLength(1)
  })

  it('marks reachable only when the health probe returns 200', async () => {
    axios.get.mockResolvedValueOnce(ok(200))
    await offlineManager.checkReachability()
    expect(offlineManager.getStatus().online).toBe(true)

    axios.get.mockRejectedValueOnce(new Error('ECONNREFUSED'))
    await offlineManager.checkReachability()
    expect(offlineManager.getStatus().online).toBe(false)
    expect(axios.get.mock.calls[0][0]).toBe('http://localhost:8010/api/health/')
  })

  it('flushes the queue when a probe finds the server reachable', async () => {
    await offlineManager.enqueue('post', 'http://localhost:8010/api/customers/', {})
    axios.get.mockResolvedValueOnce(ok(200))
    axios.request.mockResolvedValue(ok(201))

    await offlineManager.checkReachability()

    expect(axios.request).toHaveBeenCalledTimes(1)
    expect(offlineManager.getStatus().pending).toEqual([])
  })

  it('discards a failed item and persists the removal', async () => {
    await offlineManager.enqueue('post', 'http://localhost:8010/api/customers/', {})
    axios.request.mockResolvedValue(ok(409, { detail: 'duplicate' }))
    await offlineManager.flush()
    const failed = offlineManager.getStatus().failed as QueuedWrite[]

    await offlineManager.discard(failed[0].seq)

    expect(offlineManager.getStatus().failed).toEqual([])
    expect(db.rows.get('syncQueue')!.size).toBe(0)
  })
})
