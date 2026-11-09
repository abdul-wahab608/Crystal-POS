import axios from 'axios'
import { API_BASE_URL } from '../api/baseUrl'
import { useToastStore } from '../stores/toast'
import indexedDBManager from './indexedDBManager'

const PROBE_INTERVAL_MS = 10000
const PROBE_TIMEOUT_MS = 3000
const SYNC_TIMEOUT_MS = 30000
const MAX_SERVER_RETRIES = 3
const SYNC_STORE = 'syncQueue'

export type WriteMethod = 'post' | 'put' | 'patch' | 'delete'

export interface QueuedWrite {
  seq: number
  method: WriteMethod
  url: string
  data?: unknown
  timestamp: string
  retries: number
  status: 'pending' | 'failed'
  failureReason?: string
}

export interface OfflineStatus {
  online: boolean
  syncing: boolean
  pending: QueuedWrite[]
  failed: QueuedWrite[]
}

export class QueuedWriteError extends Error {
  readonly queued = true

  constructor() {
    super('Saved offline. It will sync when the server is reachable.')
    this.name = 'QueuedWriteError'
  }
}

type Listener = (status: OfflineStatus) => void

class OfflineManager {
  private online = true
  private syncing = false
  private items: QueuedWrite[] = []
  private loading: Promise<void> | null = null
  private flushing: Promise<void> | null = null
  private lastSeq = 0
  private listeners = new Set<Listener>()

  start() {
    void this.load()
    setInterval(() => void this.checkReachability(), PROBE_INTERVAL_MS)
    void this.checkReachability()
  }

  subscribe(listener: Listener) {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  getStatus(): OfflineStatus {
    return {
      online: this.online,
      syncing: this.syncing,
      pending: this.items.filter(item => item.status === 'pending'),
      failed: this.items.filter(item => item.status === 'failed'),
    }
  }

  async enqueue(method: WriteMethod, url: string, data: unknown) {
    await this.load()
    const seq = Math.max(Date.now(), this.lastSeq + 1)
    const item: QueuedWrite = {
      seq,
      method,
      url,
      data,
      timestamp: new Date().toISOString(),
      retries: 0,
      status: 'pending',
    }
    await indexedDBManager.save(SYNC_STORE, item)
    this.lastSeq = seq
    this.items.push(item)
    this.notify()
  }

  async discard(seq: number) {
    await this.load()
    await indexedDBManager.delete(SYNC_STORE, seq)
    this.items = this.items.filter(item => item.seq !== seq)
    this.notify()
  }

  async checkReachability() {
    const reachable = await this.probe()
    this.setOnline(reachable)
    if (reachable) await this.flush()
  }

  flush(): Promise<void> {
    if (!this.flushing) {
      this.flushing = this.runFlush().finally(() => {
        this.flushing = null
      })
    }
    return this.flushing
  }

  private async probe() {
    try {
      const res = await axios.get(`${API_BASE_URL}/health/`, {
        timeout: PROBE_TIMEOUT_MS,
        validateStatus: () => true,
      })
      return res.status === 200
    } catch {
      return false
    }
  }

  private async runFlush() {
    await this.load()
    if (!this.items.some(item => item.status === 'pending')) return

    this.syncing = true
    this.notify()
    try {
      for (const item of this.items.filter(i => i.status === 'pending')) {
        const keepGoing = await this.send(item)
        if (!keepGoing) break
      }
    } finally {
      this.syncing = false
      this.notify()
    }
  }

  private async send(item: QueuedWrite): Promise<boolean> {
    const token = localStorage.getItem('auth_token')
    let response
    try {
      response = await axios.request({
        method: item.method,
        url: item.url,
        data: item.data,
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        timeout: SYNC_TIMEOUT_MS,
        validateStatus: () => true,
      })
    } catch {
      this.setOnline(false)
      return false
    }

    const { status } = response
    if (status >= 200 && status < 300) {
      await this.remove(item)
      return true
    }
    if (status === 401) return false
    if (status >= 500) {
      item.retries += 1
      if (item.retries < MAX_SERVER_RETRIES) {
        await indexedDBManager.save(SYNC_STORE, item)
        return false
      }
      await this.markFailed(item, `server error ${status}`)
      return true
    }
    await this.markFailed(item, `HTTP ${status}: ${JSON.stringify(response.data ?? null).slice(0, 200)}`)
    return true
  }

  private async remove(item: QueuedWrite) {
    await indexedDBManager.delete(SYNC_STORE, item.seq)
    this.items = this.items.filter(i => i !== item)
    this.notify()
  }

  private async markFailed(item: QueuedWrite, reason: string) {
    item.status = 'failed'
    item.failureReason = reason
    await indexedDBManager.save(SYNC_STORE, item)
    this.notify()
    useToastStore().error(
      'Offline change failed to sync',
      `${item.method.toUpperCase()} ${item.url}: ${reason}. Review it in Offline Settings.`
    )
  }

  private setOnline(value: boolean) {
    if (value === this.online) return
    this.online = value
    this.notify()
  }

  private load() {
    if (!this.loading) {
      this.loading = indexedDBManager.getAll(SYNC_STORE).then(rows => {
        this.items = rows as QueuedWrite[]
        this.lastSeq = this.items.reduce((max, item) => Math.max(max, item.seq), 0)
      })
    }
    return this.loading
  }

  private notify() {
    const status = this.getStatus()
    this.listeners.forEach(listener => listener(status))
  }
}

const offlineManager = new OfflineManager();

export default offlineManager;
