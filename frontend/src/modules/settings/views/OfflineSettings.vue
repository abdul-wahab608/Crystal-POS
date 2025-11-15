<template>
  <div class="offline-settings">
    <div class="settings-header">
      <h2>🔌 Offline & Sync Settings</h2>
      <p class="subtitle">Manage offline data and synchronization</p>
    </div>

    <div class="status-cards">
      <div class="status-card" :class="{ online: isOnline, offline: !isOnline }">
        <div class="status-icon">{{ isOnline ? '🟢' : '🔴' }}</div>
        <div class="status-info">
          <h3>Network Status</h3>
          <p>{{ isOnline ? 'Connected' : 'Offline Mode' }}</p>
        </div>
      </div>

      <div class="status-card">
        <div class="status-icon">📦</div>
        <div class="status-info">
          <h3>Sync Queue</h3>
          <p>{{ syncQueueStatus.total }} pending items</p>
        </div>
      </div>

      <div class="status-card">
        <div class="status-icon">💾</div>
        <div class="status-info">
          <h3>Cached Data</h3>
          <p>{{ cachedItems }} items stored</p>
        </div>
      </div>
    </div>

    <div class="sync-queue-section" v-if="syncQueueStatus.total > 0">
      <h3>📤 Pending Sync Items</h3>
      <div class="queue-list">
        <div
          v-for="item in syncQueueStatus.items"
          :key="item.id"
          class="queue-item"
        >
          <div class="queue-method" :class="item.method.toLowerCase()">
            {{ item.method }}
          </div>
          <div class="queue-url">{{ item.url }}</div>
          <div class="queue-time">{{ formatTime(item.timestamp) }}</div>
          <div class="queue-retries">Retries: {{ item.retries }}/{{ item.maxRetries }}</div>
        </div>
      </div>

      <div class="queue-actions">
        <button @click="syncNow" class="btn btn-primary" :disabled="!isOnline">
          🔄 Sync Now
        </button>
        <button @click="clearQueue" class="btn btn-danger">
          🗑️ Clear Queue
        </button>
      </div>
    </div>

    <div class="cache-section">
      <h3>💾 Cache Management</h3>
      <p>Clear cached data to free up space. Data will be re-downloaded when needed.</p>
      
      <div class="cache-actions">
        <button @click="clearCache('customers')" class="btn btn-secondary">
          Clear Customers Cache
        </button>
        <button @click="clearCache('products')" class="btn btn-secondary">
          Clear Products Cache
        </button>
        <button @click="clearCache('vendors')" class="btn btn-secondary">
          Clear Vendors Cache
        </button>
        <button @click="clearAllCache" class="btn btn-danger">
          Clear All Cache
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import offlineManager from '@/shared/utils/offlineManager'
import indexedDBManager from '@/shared/utils/indexedDBManager'

const isOnline = ref(navigator.onLine)
const syncQueueStatus = ref({ total: 0, items: [] })
const cachedItems = ref(0)

let unsubscribe: (() => void) | null = null
let intervalId: number | null = null

const updateStatus = (status: { online: boolean }) => {
  isOnline.value = status.online
  updateSyncQueueStatus()
}

const updateSyncQueueStatus = () => {
  syncQueueStatus.value = offlineManager.getSyncQueueStatus()
}

const updateCacheCount = async () => {
  try {
    const stores = ['customers', 'products', 'vendors', 'sales', 'purchases']
    let total = 0
    
    for (const store of stores) {
      const items = await indexedDBManager.getAll(store)
      total += items.length
    }
    
    cachedItems.value = total
  } catch (error) {
    console.error('Failed to count cached items:', error)
  }
}

const syncNow = async () => {
  if (!isOnline.value) return
  
  try {
    await offlineManager.processSyncQueue()
    alert('✅ Sync completed successfully!')
    updateSyncQueueStatus()
  } catch (error) {
    alert('❌ Sync failed: ' + error)
  }
}

const clearQueue = () => {
  if (confirm('Are you sure you want to clear the sync queue? Pending changes will be lost.')) {
    offlineManager.clearSyncQueue()
    updateSyncQueueStatus()
  }
}

const clearCache = async (storeName: string) => {
  if (confirm(`Clear ${storeName} cache?`)) {
    try {
      await indexedDBManager.clear(storeName)
      await updateCacheCount()
      alert(`✅ ${storeName} cache cleared`)
    } catch (error) {
      alert('❌ Failed to clear cache: ' + error)
    }
  }
}

const clearAllCache = async () => {
  if (confirm('Clear ALL cached data? This cannot be undone.')) {
    try {
      const stores = ['customers', 'products', 'vendors', 'sales', 'purchases', 'cache']
      for (const store of stores) {
        await indexedDBManager.clear(store)
      }
      await updateCacheCount()
      alert('✅ All cache cleared')
    } catch (error) {
      alert('❌ Failed to clear cache: ' + error)
    }
  }
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}

onMounted(() => {
  unsubscribe = offlineManager.subscribe(updateStatus)
  updateSyncQueueStatus()
  updateCacheCount()
  
  // Update every 3 seconds
  intervalId = window.setInterval(() => {
    updateSyncQueueStatus()
    updateCacheCount()
  }, 3000)
})

onUnmounted(() => {
  if (unsubscribe) unsubscribe()
  if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped>
.offline-settings {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.settings-header {
  margin-bottom: 30px;
}

.settings-header h2 {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.subtitle {
  color: #6b7280;
  font-size: 16px;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.status-card.online {
  border-left: 4px solid #10b981;
}

.status-card.offline {
  border-left: 4px solid #ef4444;
}

.status-icon {
  font-size: 40px;
}

.status-info h3 {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.status-info p {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.sync-queue-section,
.cache-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.sync-queue-section h3,
.cache-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.queue-item {
  display: grid;
  grid-template-columns: 80px 1fr 200px 120px;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 14px;
}

.queue-method {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  text-align: center;
  text-transform: uppercase;
  font-size: 12px;
}

.queue-method.post { background: #dbeafe; color: #1e40af; }
.queue-method.put { background: #fef3c7; color: #92400e; }
.queue-method.delete { background: #fee2e2; color: #991b1b; }

.queue-url {
  color: #4b5563;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.queue-time {
  color: #6b7280;
  font-size: 12px;
}

.queue-retries {
  color: #9ca3af;
  font-size: 12px;
}

.queue-actions,
.cache-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}
</style>
