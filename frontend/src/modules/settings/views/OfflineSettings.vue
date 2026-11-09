<template>
  <div class="offline-settings">
    <div class="settings-header">
      <h2>🔌 Offline & Sync Settings</h2>
      <p class="subtitle">Manage offline data and synchronization</p>
    </div>

    <div class="status-cards">
      <div class="status-card" :class="{ online: status.online, offline: !status.online }">
        <div class="status-icon">{{ status.online ? '🟢' : '🔴' }}</div>
        <div class="status-info">
          <h3>Server Status</h3>
          <p>{{ status.online ? 'Reachable' : 'Unreachable' }}</p>
        </div>
      </div>

      <div class="status-card">
        <div class="status-icon">📦</div>
        <div class="status-info">
          <h3>Sync Queue</h3>
          <p>{{ status.pending.length }} pending, {{ status.failed.length }} failed</p>
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

    <div class="sync-queue-section" v-if="status.pending.length > 0">
      <h3>📤 Pending Sync Items</h3>
      <div class="queue-list">
        <div v-for="item in pendingItems" :key="item.seq" class="queue-item">
          <div class="queue-method" :class="item.method">{{ item.method }}</div>
          <div class="queue-url">{{ item.url }}</div>
          <div class="queue-time">{{ formatTime(item.timestamp) }}</div>
        </div>
      </div>
      <PaginationBar
        :page="pendingPage"
        :totalPages="pendingTotalPages"
        :total="pendingTotal"
        :pageSize="pendingSize"
        @update:page="goToPendingPage"
        @update:pageSize="setPendingSize"
      />
      <div class="queue-actions">
        <button @click="syncNow" class="btn btn-primary">🔄 Sync Now</button>
      </div>
    </div>

    <div class="sync-queue-section failed-section" v-if="status.failed.length > 0">
      <h3>⚠️ Failed to Sync</h3>
      <p class="section-note">These changes were rejected by the server and were not saved. Discard them only after checking them.</p>
      <div class="queue-list">
        <div v-for="item in failedItems" :key="item.seq" class="queue-item failed-item">
          <div class="queue-method" :class="item.method">{{ item.method }}</div>
          <div class="queue-url">{{ item.url }}</div>
          <div class="queue-time">{{ formatTime(item.timestamp) }}</div>
          <div class="queue-reason">{{ item.failureReason }}</div>
          <button @click="discard(item.seq)" class="btn btn-danger btn-small">Discard</button>
        </div>
      </div>
      <PaginationBar
        :page="failedPage"
        :totalPages="failedTotalPages"
        :total="failedTotal"
        :pageSize="failedSize"
        @update:page="goToFailedPage"
        @update:pageSize="setFailedSize"
      />
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import offlineManager, { type OfflineStatus } from '@/shared/utils/offlineManager'
import indexedDBManager from '@/shared/utils/indexedDBManager'
import PaginationBar from '@/shared/components/PaginationBar.vue'
import { usePagination } from '@/shared/composables/usePagination'

const CACHE_STORES = ['customers', 'products', 'vendors', 'sales', 'purchases']

const status = ref<OfflineStatus>(offlineManager.getStatus())

const {
  page: pendingPage, pageSize: pendingSize, totalPages: pendingTotalPages, pageItems: pendingItems, total: pendingTotal,
  goTo: goToPendingPage, setPageSize: setPendingSize,
} = usePagination(computed(() => status.value.pending))
const {
  page: failedPage, pageSize: failedSize, totalPages: failedTotalPages, pageItems: failedItems, total: failedTotal,
  goTo: goToFailedPage, setPageSize: setFailedSize,
} = usePagination(computed(() => status.value.failed))
const cachedItems = ref(0)
let unsubscribe: (() => void) | null = null

const updateCacheCount = async () => {
  let total = 0
  for (const store of CACHE_STORES) {
    total += (await indexedDBManager.getAll(store)).length
  }
  cachedItems.value = total
}

const syncNow = () => offlineManager.checkReachability()

const discard = async (seq: number) => {
  if (!confirm('Discard this change? It was rejected by the server and is not saved anywhere else.')) return
  await offlineManager.discard(seq)
}

const clearCache = async (storeName: string) => {
  if (!confirm(`Clear ${storeName} cache?`)) return
  try {
    await indexedDBManager.clear(storeName)
    await updateCacheCount()
    alert(`✅ ${storeName} cache cleared`)
  } catch (error) {
    alert('❌ Failed to clear cache: ' + error)
  }
}

const clearAllCache = async () => {
  if (!confirm('Clear ALL cached data? This cannot be undone.')) return
  try {
    for (const store of [...CACHE_STORES, 'cache']) {
      await indexedDBManager.clear(store)
    }
    await updateCacheCount()
    alert('✅ All cache cleared')
  } catch (error) {
    alert('❌ Failed to clear cache: ' + error)
  }
}

const formatTime = (timestamp: string) => new Date(timestamp).toLocaleString()

onMounted(() => {
  unsubscribe = offlineManager.subscribe(next => {
    status.value = next
  })
  updateCacheCount()
})

onUnmounted(() => {
  if (unsubscribe) unsubscribe()
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

.failed-section {
  border-left: 4px solid #ef4444;
}

.sync-queue-section h3,
.cache-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.section-note {
  color: #6b7280;
  font-size: 14px;
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
  grid-template-columns: 80px 1fr 200px;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 14px;
}

.failed-item {
  grid-template-columns: 80px 1fr 200px 1fr auto;
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
.queue-method.patch { background: #ede9fe; color: #5b21b6; }
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

.queue-reason {
  color: #991b1b;
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

.btn-small {
  padding: 6px 12px;
  font-size: 13px;
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
