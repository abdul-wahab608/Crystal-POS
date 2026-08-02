/**
 * Tests for export store
 * Note: Tests focus on store logic. Download functionality requires browser environment.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useExportStore } from '../export'

describe('ExportStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useExportStore()
      expect(store.exporting).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('exportData validation', () => {
    it('should set error for unknown entity type', async () => {
      const store = useExportStore()
      
      await store.exportData('unknown_entity', 'csv')
      
      expect(store.error).toBe('Unknown entity type: unknown_entity')
      expect(store.exporting).toBe(false)
    })

    it('should accept valid entity types', () => {
      const store = useExportStore()
      
      // These should not throw immediately (would fail at API call in real env)
      const validTypes = ['customers', 'vendors', 'products', 'raw_materials', 'assets']
      
      for (const type of validTypes) {
        store.error = null
        // Don't await - just check it doesn't reject entity type
        const promise = store.exportData(type, 'csv')
        // The promise will reject due to no mock, but error should not be about entity type
        promise.catch(() => {})
        expect(store.error).not.toBe(`Unknown entity type: ${type}`)
      }
    })
  })

  describe('Loading state', () => {
    it('should set exporting true when starting', async () => {
      const store = useExportStore()
      
      // Start export (will fail but that's ok for this test)
      const promise = store.exportData('customers', 'csv')
      
      // Should be exporting
      expect(store.exporting).toBe(true)
      
      // Wait for it to finish (with error)
      try { await promise } catch {}
      
      // Should not be exporting anymore
      expect(store.exporting).toBe(false)
    })
  })
})
