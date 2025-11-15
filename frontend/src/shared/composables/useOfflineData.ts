/**
 * Composable for offline-aware data fetching
 */

import { ref, computed } from 'vue'
import indexedDBManager from '@/shared/utils/indexedDBManager'
import offlineManager from '@/shared/utils/offlineManager'

export function useOfflineData<T>(storeName: string) {
  const data = ref<T[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isOffline = computed(() => !offlineManager.checkOnlineStatus())

  /**
   * Fetch data with offline support
   */
  const fetchData = async (apiCall: () => Promise<T[]>) => {
    loading.value = true
    error.value = null

    try {
      if (offlineManager.checkOnlineStatus()) {
        // Online: fetch from API
        const result = await apiCall()
        data.value = result

        // Cache to IndexedDB
        await indexedDBManager.saveAll(storeName, result)
      } else {
        // Offline: load from IndexedDB
        const cached = await indexedDBManager.getAll(storeName)
        data.value = cached as T[]

        if (cached.length === 0) {
          error.value = 'No offline data available'
        }
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch data'

      // Try loading from cache on error
      try {
        const cached = await indexedDBManager.getAll(storeName)
        if (cached.length > 0) {
          data.value = cached as T[]
          error.value = 'Using cached data (offline)'
        }
      } catch (cacheErr) {
        console.error('Failed to load cache:', cacheErr)
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Save data locally
   */
  const saveLocal = async (item: T) => {
    await indexedDBManager.save(storeName, item)
  }

  /**
   * Delete data locally
   */
  const deleteLocal = async (id: number | string) => {
    await indexedDBManager.delete(storeName, id)
  }

  /**
   * Clear all local data
   */
  const clearLocal = async () => {
    await indexedDBManager.clear(storeName)
  }

  return {
    data,
    loading,
    error,
    isOffline,
    fetchData,
    saveLocal,
    deleteLocal,
    clearLocal
  }
}
