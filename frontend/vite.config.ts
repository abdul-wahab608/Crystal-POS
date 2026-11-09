import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
import nightwatchPlugin from 'vite-plugin-nightwatch'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
    nightwatchPlugin(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  base: '/',
  build: {
    chunkSizeWarningLimit: 600,
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (!id.includes('node_modules')) return undefined
          if (id.includes('apexcharts')) return 'charts'
          if (id.includes('/xlsx/')) return 'xlsx'
          if (id.includes('/vue/') || id.includes('/pinia/') || id.includes('vue-router') || id.includes('@vue/')) return 'vue-vendor'
          return undefined
        }
      }
    }
  }
})
