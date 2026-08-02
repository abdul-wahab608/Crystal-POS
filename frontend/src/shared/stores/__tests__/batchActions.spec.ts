/**
 * Tests for batch actions store
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBatchActionsStore } from '../batchActions'

// Mock axios
vi.mock('../../api/axios', () => ({
  default: {
    post: vi.fn(),
  },
}))

import api from '../../api/axios'

describe('BatchActionsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Selection Management', () => {
    it('should initialize with empty selection', () => {
      const store = useBatchActionsStore()
      expect(store.selectedCount('customers')).toBe(0)
      expect(store.hasSelection('customers')).toBe(false)
    })

    it('should toggle selection', () => {
      const store = useBatchActionsStore()
      
      store.toggleSelection('customers', 1)
      expect(store.isSelected('customers', 1)).toBe(true)
      expect(store.selectedCount('customers')).toBe(1)
      
      store.toggleSelection('customers', 1)
      expect(store.isSelected('customers', 1)).toBe(false)
      expect(store.selectedCount('customers')).toBe(0)
    })

    it('should select multiple items', () => {
      const store = useBatchActionsStore()
      
      store.selectMany('customers', [1, 2, 3])
      expect(store.selectedCount('customers')).toBe(3)
      expect(store.getSelectedIds('customers')).toEqual([1, 2, 3])
    })

    it('should select all items', () => {
      const store = useBatchActionsStore()
      
      store.selectAll('customers', [1, 2, 3, 4, 5])
      expect(store.selectedCount('customers')).toBe(5)
    })

    it('should clear selection for entity', () => {
      const store = useBatchActionsStore()
      
      store.selectAll('customers', [1, 2, 3])
      store.clearSelection('customers')
      expect(store.selectedCount('customers')).toBe(0)
    })

    it('should handle multiple entity types independently', () => {
      const store = useBatchActionsStore()
      
      store.selectMany('customers', [1, 2])
      store.selectMany('vendors', [10, 20, 30])
      
      expect(store.selectedCount('customers')).toBe(2)
      expect(store.selectedCount('vendors')).toBe(3)
      
      store.clearSelection('customers')
      expect(store.selectedCount('customers')).toBe(0)
      expect(store.selectedCount('vendors')).toBe(3)
    })
  })

  describe('Bulk Delete', () => {
    it('should call API and clear selection on success', async () => {
      const store = useBatchActionsStore()
      store.selectMany('customers', [1, 2, 3])
      
      vi.mocked(api.post).mockResolvedValueOnce({
        data: { deleted_count: 3, message: 'Deleted 3 records' }
      })
      
      const result = await store.bulkDelete('customers')
      
      expect(api.post).toHaveBeenCalledWith('/api/customers/bulk_delete/', { ids: [1, 2, 3] })
      expect(result.success).toBe(true)
      expect(result.count).toBe(3)
      expect(store.selectedCount('customers')).toBe(0)
    })

    it('should return error when no items selected', async () => {
      const store = useBatchActionsStore()
      
      const result = await store.bulkDelete('customers')
      
      expect(result.success).toBe(false)
      expect(result.message).toBe('No items selected')
      expect(api.post).not.toHaveBeenCalled()
    })

    it('should handle API errors', async () => {
      const store = useBatchActionsStore()
      store.selectMany('customers', [1])
      
      vi.mocked(api.post).mockRejectedValueOnce({
        response: { data: { error: 'Server error' } }
      })
      
      const result = await store.bulkDelete('customers')
      
      expect(result.success).toBe(false)
      expect(result.message).toBe('Server error')
    })
  })

  describe('Bulk Activate', () => {
    it('should call API for activation', async () => {
      const store = useBatchActionsStore()
      store.selectMany('customers', [1, 2])
      
      vi.mocked(api.post).mockResolvedValueOnce({
        data: { updated_count: 2, message: 'Activated 2 records' }
      })
      
      const result = await store.bulkActivate('customers')
      
      expect(api.post).toHaveBeenCalledWith('/api/customers/bulk_activate/', { ids: [1, 2] })
      expect(result.success).toBe(true)
      expect(result.count).toBe(2)
    })
  })

  describe('Bulk Deactivate', () => {
    it('should call API for deactivation', async () => {
      const store = useBatchActionsStore()
      store.selectMany('vendors', [5, 6])
      
      vi.mocked(api.post).mockResolvedValueOnce({
        data: { updated_count: 2, message: 'Deactivated 2 records' }
      })
      
      const result = await store.bulkDeactivate('vendors')
      
      expect(api.post).toHaveBeenCalledWith('/api/vendors/bulk_deactivate/', { ids: [5, 6] })
      expect(result.success).toBe(true)
    })
  })

  describe('Bulk Update', () => {
    it('should call API with update data', async () => {
      const store = useBatchActionsStore()
      store.selectMany('products', [1, 2, 3])
      
      vi.mocked(api.post).mockResolvedValueOnce({
        data: { updated_count: 3, message: 'Updated 3 records' }
      })
      
      const result = await store.bulkUpdate('products', { category: 'Electronics' })
      
      expect(api.post).toHaveBeenCalledWith('/api/products/bulk_update/', { 
        ids: [1, 2, 3], 
        data: { category: 'Electronics' } 
      })
      expect(result.success).toBe(true)
      expect(result.count).toBe(3)
    })
  })

  describe('Endpoint Mapping', () => {
    it('should use correct endpoint for raw_materials', async () => {
      const store = useBatchActionsStore()
      store.selectMany('raw_materials', [1])
      
      vi.mocked(api.post).mockResolvedValueOnce({
        data: { deleted_count: 1, message: 'Deleted' }
      })
      
      await store.bulkDelete('raw_materials')
      
      expect(api.post).toHaveBeenCalledWith('/api/raw-materials/bulk_delete/', { ids: [1] })
    })
  })
})
