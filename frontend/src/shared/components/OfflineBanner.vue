<template>
  <div v-if="!isOnline" class="offline-banner">
    <div class="offline-content">
      <span class="offline-icon">🔴</span>
      <span class="offline-text">You are offline. Changes will be synced when connection is restored.</span>
      <span v-if="syncQueue > 0" class="sync-queue-badge">{{ syncQueue }} pending</span>
    </div>
  </div>
  <div v-else-if="syncQueue > 0" class="syncing-banner">
    <div class="syncing-content">
      <span class="syncing-icon">🔄</span>
      <span class="syncing-text">Syncing {{ syncQueue }} changes...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import offlineManager from '@/shared/utils/offlineManager'

const isOnline = ref(navigator.onLine)
const syncQueue = ref(0)

let unsubscribe: (() => void) | null = null

const updateStatus = (status: { online: boolean }) => {
  isOnline.value = status.online
  updateSyncQueue()
}

const updateSyncQueue = () => {
  const status = offlineManager.getSyncQueueStatus()
  syncQueue.value = status.total
}

onMounted(() => {
  // Subscribe to network changes
  unsubscribe = offlineManager.subscribe(updateStatus)
  
  // Update initial sync queue status
  updateSyncQueue()
  
  // Update sync queue periodically
  const interval = setInterval(updateSyncQueue, 3000)
  
  onUnmounted(() => {
    if (unsubscribe) unsubscribe()
    clearInterval(interval)
  })
})
</script>

<style scoped>
.offline-banner,
.syncing-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  padding: 12px 20px;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.offline-banner {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.syncing-banner {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.offline-content,
.syncing-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.offline-icon,
.syncing-icon {
  font-size: 18px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.syncing-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.sync-queue-badge {
  background: rgba(255, 255, 255, 0.3);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
</style>
