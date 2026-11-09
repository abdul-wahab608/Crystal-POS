import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../../../shared/api/axios'
import type { RawMaterial, RawMaterialFormPayload, RawMaterialUsage, CreateRawMaterialUsage } from '../types'

export const useRawMaterialsStore = defineStore('rawMaterials', () => {
  const materials = ref<RawMaterial[]>([])
  const loading = ref(false)

  const lowStock = computed(() => materials.value.filter(material => material.needs_reorder))

  async function fetchMaterials() {
    loading.value = true
    try {
      const { data } = await api.get<RawMaterial[]>('/raw-materials/materials/')
      materials.value = data
    } finally {
      loading.value = false
    }
  }

  async function createMaterial(payload: RawMaterialFormPayload) {
    await api.post('/raw-materials/materials/', payload)
    await fetchMaterials()
  }

  async function updateMaterial(id: number, payload: Partial<RawMaterialFormPayload>) {
    await api.patch(`/raw-materials/materials/${id}/`, payload)
    await fetchMaterials()
  }

  async function deleteMaterial(id: number) {
    await api.delete(`/raw-materials/materials/${id}/`)
    await fetchMaterials()
  }

  async function createUsage(payload: CreateRawMaterialUsage) {
    await api.post('/raw-materials/usage/', payload)
    await fetchMaterials()
  }

  async function fetchUsage(materialId: number): Promise<RawMaterialUsage[]> {
    const { data } = await api.get<RawMaterialUsage[]>(`/raw-materials/materials/${materialId}/usage/`)
    return data
  }

  return {
    materials,
    loading,
    lowStock,
    fetchMaterials,
    createMaterial,
    updateMaterial,
    deleteMaterial,
    createUsage,
    fetchUsage,
  }
})
