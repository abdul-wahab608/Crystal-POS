import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      include: ['src/**/__tests__/*.{test,spec}.{js,ts}'],
      globals: true,
      root: fileURLToPath(new URL('./', import.meta.url)),
    },
  })
)
