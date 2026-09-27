import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../../../shared/api/axios'
import type {
  CostComponentType,
  ProductCost,
  CreateProductCost,
  CurrentCost,
  ProfitFilters,
  ProfitSummaryTotals,
  ProfitSummaryRow,
  ProfitTrend,
  ProfitGroupBy,
  ProfitMetric,
} from '../types'

function toQuery(params: Record<string, any>) {
  const query: Record<string, string> = {}
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query[key] = String(value)
    }
  })
  return query
}

export const useProfitStore = defineStore('profit', () => {
  const costComponents = ref<CostComponentType[]>([])
  const productCosts = ref<ProductCost[]>([])
  const currentCost = ref<CurrentCost | null>(null)
  const summaryTotals = ref<ProfitSummaryTotals | null>(null)
  const summaryRows = ref<ProfitSummaryRow[]>([])
  const trend = ref<ProfitTrend>({ categories: [], series: [] })
  const loading = ref(false)

  async function fetchCostComponents() {
    const response = await api.get('/profit/cost-components/')
    costComponents.value = Array.isArray(response.data) ? response.data : (response.data?.results ?? [])
  }

  async function createCostComponent(name: string) {
    const response = await api.post('/profit/cost-components/', { name })
    costComponents.value.push(response.data)
    return response.data
  }

  async function fetchProductCosts(productId: number) {
    const response = await api.get('/profit/product-costs/', { params: { product: productId } })
    productCosts.value = Array.isArray(response.data) ? response.data : (response.data?.results ?? [])
  }

  async function addProductCost(data: CreateProductCost) {
    const response = await api.post('/profit/product-costs/', data)
    productCosts.value.unshift(response.data)
    return response.data
  }

  async function deleteProductCost(id: number) {
    await api.delete(`/profit/product-costs/${id}/`)
    productCosts.value = productCosts.value.filter((c) => c.id !== id)
  }

  async function fetchCurrentCost(productId: number, asOf?: string) {
    const response = await api.get('/profit/product-costs/current/', {
      params: toQuery({ product: productId, as_of: asOf }),
    })
    currentCost.value = response.data
    return response.data
  }

  async function fetchSummary(filters: ProfitFilters & { unit?: string }, groupBy?: ProfitGroupBy) {
    loading.value = true
    try {
      const response = await api.get('/profit/summary/', {
        params: toQuery({ ...filters, group_by: groupBy }),
      })
      if (groupBy) {
        summaryRows.value = response.data.rows || []
      } else {
        summaryTotals.value = response.data
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchTrend(
    filters: ProfitFilters & { unit?: string },
    x: ProfitGroupBy,
    series?: ProfitGroupBy,
    metric: ProfitMetric = 'profit_amount',
  ) {
    loading.value = true
    try {
      const response = await api.get('/profit/trend/', {
        params: toQuery({ ...filters, x, series, metric }),
      })
      trend.value = response.data
    } finally {
      loading.value = false
    }
  }

  return {
    costComponents,
    productCosts,
    currentCost,
    summaryTotals,
    summaryRows,
    trend,
    loading,
    fetchCostComponents,
    createCostComponent,
    fetchProductCosts,
    addProductCost,
    deleteProductCost,
    fetchCurrentCost,
    fetchSummary,
    fetchTrend,
  }
})
