<script setup lang="ts">
import { onMounted } from 'vue'
import ToastContainer from './shared/components/ToastContainer.vue'
import indexedDBManager from './shared/utils/indexedDBManager'
import offlineManager from './shared/utils/offlineManager'

onMounted(async () => {
  try {
    await indexedDBManager.init()
  } catch (error) {
    console.error('Failed to initialize IndexedDB:', error)
  }
  offlineManager.start()
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