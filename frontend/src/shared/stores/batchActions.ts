/**
 * Batch Actions store for managing selection and bulk operations
 */
import { defineStore } from 'pinia'
import api from '../api/axios'

export type BatchAction = 'delete' | 'activate' | 'deactivate' | 'update'

export interface BatchActionResult {
  success: boolean
  count: number
  errors?: Array<{ id: number; error: string }>
  message: string
}

export const useBatchActionsStore = defineStore('batchActions', {
  state: () => ({
    // Selection state per entity
    selectedIds: {} as Record<string, number[]>,
    // Loading state
    loading: false,
    error: null as string | null,
  }),

  getters: {
    /**
     * Get selected IDs for a specific entity
     */
    getSelectedIds: (state) => (entityType: string): number[] => {
      return state.selectedIds[entityType] || []
    },

    /**
     * Check if an ID is selected for an entity
     */
    isSelected: (state) => (entityType: string, id: number): boolean => {
      return (state.selectedIds[entityType] || []).includes(id)
    },

    /**
     * Get count of selected items for an entity
     */
    selectedCount: (state) => (entityType: string): number => {
      return (state.selectedIds[entityType] || []).length
    },

    /**
     * Check if any items are selected for an entity
     */
    hasSelection: (state) => (entityType: string): boolean => {
      return (state.selectedIds[entityType] || []).length > 0
    },
  },

  actions: {
    /**
     * Toggle selection of an item
     */
    toggleSelection(entityType: string, id: number) {
      if (!this.selectedIds[entityType]) {
        this.selectedIds[entityType] = []
      }
      
      const index = this.selectedIds[entityType].indexOf(id)
      if (index === -1) {
        this.selectedIds[entityType].push(id)
      } else {
        this.selectedIds[entityType].splice(index, 1)
      }
    },

    /**
     * Select multiple items
     */
    selectMany(entityType: string, ids: number[]) {
      if (!this.selectedIds[entityType]) {
        this.selectedIds[entityType] = []
      }
      
      for (const id of ids) {
        if (!this.selectedIds[entityType].includes(id)) {
          this.selectedIds[entityType].push(id)
        }
      }
    },

    /**
     * Select all items from a list
     */
    selectAll(entityType: string, ids: number[]) {
      this.selectedIds[entityType] = [...ids]
    },

    /**
     * Clear all selections for an entity
     */
    clearSelection(entityType: string) {
      this.selectedIds[entityType] = []
    },

    /**
     * Clear all selections across all entities
     */
    clearAllSelections() {
      this.selectedIds = {}
    },

    /**
     * Get API endpoint for entity type
     */
    _getEndpoint(entityType: string): string {
      const endpointMap: Record<string, string> = {
        customers: '/api/customers',
        vendors: '/api/vendors',
        products: '/api/products',
        raw_materials: '/api/raw-materials',
        assets: '/api/assets',
      }
      return endpointMap[entityType] || `/api/${entityType}`
    },

    /**
     * Bulk delete selected items
     */
    async bulkDelete(entityType: string): Promise<BatchActionResult> {
      const ids = this.selectedIds[entityType] || []
      
      if (ids.length === 0) {
        return { success: false, count: 0, message: 'No items selected' }
      }

      this.loading = true
      this.error = null

      try {
        const endpoint = this._getEndpoint(entityType)
        const response = await api.post(`${endpoint}/bulk_delete/`, { ids })
        
        // Clear selection after successful delete
        this.clearSelection(entityType)
        
        return {
          success: true,
          count: response.data.deleted_count,
          errors: response.data.errors,
          message: response.data.message,
        }
      } catch (e: any) {
        this.error = e.response?.data?.error || e.message
        return {
          success: false,
          count: 0,
          message: this.error || 'Delete failed',
        }
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk activate selected items
     */
    async bulkActivate(entityType: string): Promise<BatchActionResult> {
      const ids = this.selectedIds[entityType] || []
      
      if (ids.length === 0) {
        return { success: false, count: 0, message: 'No items selected' }
      }

      this.loading = true
      this.error = null

      try {
        const endpoint = this._getEndpoint(entityType)
        const response = await api.post(`${endpoint}/bulk_activate/`, { ids })
        
        return {
          success: true,
          count: response.data.updated_count,
          message: response.data.message,
        }
      } catch (e: any) {
        this.error = e.response?.data?.error || e.message
        return {
          success: false,
          count: 0,
          message: this.error || 'Activation failed',
        }
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk deactivate selected items
     */
    async bulkDeactivate(entityType: string): Promise<BatchActionResult> {
      const ids = this.selectedIds[entityType] || []
      
      if (ids.length === 0) {
        return { success: false, count: 0, message: 'No items selected' }
      }

      this.loading = true
      this.error = null

      try {
        const endpoint = this._getEndpoint(entityType)
        const response = await api.post(`${endpoint}/bulk_deactivate/`, { ids })
        
        return {
          success: true,
          count: response.data.updated_count,
          message: response.data.message,
        }
      } catch (e: any) {
        this.error = e.response?.data?.error || e.message
        return {
          success: false,
          count: 0,
          message: this.error || 'Deactivation failed',
        }
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk update selected items with custom data
     */
    async bulkUpdate(entityType: string, data: Record<string, any>): Promise<BatchActionResult> {
      const ids = this.selectedIds[entityType] || []
      
      if (ids.length === 0) {
        return { success: false, count: 0, message: 'No items selected' }
      }

      this.loading = true
      this.error = null

      try {
        const endpoint = this._getEndpoint(entityType)
        const response = await api.post(`${endpoint}/bulk_update/`, { ids, data })
        
        return {
          success: true,
          count: response.data.updated_count,
          message: response.data.message,
        }
      } catch (e: any) {
        this.error = e.response?.data?.error || e.message
        return {
          success: false,
          count: 0,
          message: this.error || 'Update failed',
        }
      } finally {
        this.loading = false
      }
    },
  },
})
