import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../../../shared/api/axios'
import type {
  RawMaterial,
  RawMaterialUsage,
  RawMaterialPurchase,
  CreateRawMaterial,
  CreateRawMaterialUsage,
  CreateRawMaterialPurchase
} from '../types'

export const useRawMaterialsStore = defineStore('rawMaterials', () => {
  const materials = ref<RawMaterial[]>([])
  const usageHistory = ref<RawMaterialUsage[]>([])
  const purchaseHistory = ref<RawMaterialPurchase[]>([])
  const loading = ref(false)

  const lowStock = computed(() => {
    if (!Array.isArray(materials.value)) return []
    return materials.value.filter(material => material.needs_reorder)
  })

  async function fetchMaterials() {
    loading.value = true
    try {
      const response = await api.get('/raw-materials/materials/')
      materials.value = Array.isArray(response.data) ? response.data : []
    } catch (error) {
      materials.value = []
    } finally {
      loading.value = false
    }
  }

  async function createMaterial(data: CreateRawMaterial) {
    const response = await api.post('/raw-materials/materials/', data)
    return response.data
  }

  async function updateMaterial(id: number, data: CreateRawMaterial) {
    const response = await api.put(`/raw-materials/materials/${id}/`, data)
    return response.data
  }

  async function deleteMaterial(id: number) {
    await api.delete(`/raw-materials/materials/${id}/`)
  }

  async function createUsage(data: CreateRawMaterialUsage) {
    const response = await api.post('/raw-materials/usage/', data)
    return response.data
  }

  async function createPurchase(data: CreateRawMaterialPurchase) {
    const response = await api.post('/raw-materials/purchase/', data)
    return response.data
  }

  async function fetchUsageHistory(materialId: number) {
    try {
      const response = await api.get(`/raw-materials/materials/${materialId}/usage/`)
      usageHistory.value = Array.isArray(response.data) ? response.data : []
    } catch (error) {
      usageHistory.value = []
    }
  }

  async function fetchPurchaseHistory(materialId?: number) {
    try {
      if (materialId) {
        // Fetch purchase history for specific material
        const response = await api.get(`/raw-materials/materials/${materialId}/purchase/`)
        purchaseHistory.value = Array.isArray(response.data) ? response.data : []
      } else {
        // Fetch all purchase history
        const response = await api.get('/raw-materials/purchase/')
        purchaseHistory.value = Array.isArray(response.data) ? response.data : []
      }
    } catch (error) {
      purchaseHistory.value = []
    }
  }

  async function fetchLowStock() {
    try {
      const response = await api.get('/raw-materials/low_stock/')
      // Update materials with low stock flag
      const lowStockIds = Array.isArray(response.data) ? response.data.map((item: any) => item.id) : []
      materials.value = materials.value.map(material => ({
        ...material,
        needs_reorder: lowStockIds.includes(material.id)
      }))
    } catch (error) {
      materials.value = materials.value.map(material => ({
        ...material,
        needs_reorder: material.available_stock <= material.reorder_level
      }))
    }
  }

  return {
    materials,
    usageHistory,
    purchaseHistory,
    loading,
    lowStock,
    fetchMaterials,
    createMaterial,
    updateMaterial,
    deleteMaterial,
    createUsage,
    createPurchase,
    fetchUsageHistory,
    fetchPurchaseHistory,
    fetchLowStock
  }
}) 