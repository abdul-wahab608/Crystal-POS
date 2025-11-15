<script setup lang="ts">
import ToastContainer from './shared/components/ToastContainer.vue'
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