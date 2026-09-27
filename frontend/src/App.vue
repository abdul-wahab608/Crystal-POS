<script setup lang="ts">
import { onMounted } from 'vue'
import ToastContainer from './shared/components/ToastContainer.vue'
import indexedDBManager from './shared/utils/indexedDBManager'

// Initialize IndexedDB on app startup
onMounted(async () => {
  try {
    localStorage.removeItem('offline_sync_queue')
    await indexedDBManager.init()
  } catch (error) {
    console.error('Failed to initialize IndexedDB:', error)
  }
})
</script>

<template>
  <div id="app">
    <router-view />
    <ToastContainer />
  </div>
</template>

<style>
#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style> 