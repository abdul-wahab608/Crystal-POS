<script setup lang="ts">
import { onMounted } from 'vue'
import ToastContainer from './shared/components/ToastContainer.vue'
import OfflineBanner from './shared/components/OfflineBanner.vue'
import indexedDBManager from './shared/utils/indexedDBManager'

// Initialize IndexedDB on app startup
onMounted(async () => {
  try {
    await indexedDBManager.init()
    console.log('✅ App initialized with offline support')
  } catch (error) {
    console.error('Failed to initialize IndexedDB:', error)
  }
})
</script>

<template>
  <div id="app">
    <OfflineBanner />
    <router-view />
    <ToastContainer />
  </div>
</template>

<style>
#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style> 