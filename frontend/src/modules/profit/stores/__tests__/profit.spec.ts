import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProfitStore } from '../profit'

vi.mock('../../../../shared/api/axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

import api from '../../../../shared/api/axios'

describe('ProfitStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('cost components', () => {
    it('fetches cost components without the /api/ prefix (axios baseURL already has it)', async () => {
      const store = useProfitStore()
      vi.mocked(api.get).mockResolvedValueOnce({ data: [{ id: 1, name: 'Raw Material', is_system: true, created_at: '' }] })

      await store.fetchCostComponents()

      expect(api.get).toHaveBeenCalledWith('/profit/cost-components/')
      expect(store.costComponents).toHaveLength(1)
      expect(store.costComponents[0].name).toBe('Raw Material')
    })

    it('creates a custom cost component and appends it to state', async () => {
      const store = useProfitStore()
      vi.mocked(api.post).mockResolvedValueOnce({ data: { id: 5, name: 'Packaging', is_system: false, created_at: '' } })

      const created = await store.createCostComponent('Packaging')

      expect(api.post).toHaveBeenCalledWith('/profit/cost-components/', { name: 'Packaging' })
      expect(created.name).toBe('Packaging')
      expect(store.costComponents).toContainEqual(created)
    })
  })

  describe('product costs', () => {
    it('fetches product costs filtered by product id', async () => {
      const store = useProfitStore()
      vi.mocked(api.get).mockResolvedValueOnce({
        data: [{ id: 1, product: 7, product_name: 'Widget', component_type: 1, component_type_name: 'Labor', amount_per_dozen: '10.00', valid_from: '2026-01-01', created_at: '' }],
      })

      await store.fetchProductCosts(7)

      expect(api.get).toHaveBeenCalledWith('/profit/product-costs/', { params: { product: 7 } })
      expect(store.productCosts).toHaveLength(1)
    })

    it('adds a new cost version by unshifting, never mutating existing rows', async () => {
      const store = useProfitStore()
      store.productCosts = [
        { id: 1, product: 7, product_name: 'Widget', component_type: 1, component_type_name: 'Labor', amount_per_dozen: '10.00', valid_from: '2026-01-01', created_at: '' },
      ]
      vi.mocked(api.post).mockResolvedValueOnce({
        data: { id: 2, product: 7, product_name: 'Widget', component_type: 1, component_type_name: 'Labor', amount_per_dozen: '12.00', valid_from: '2026-04-01', created_at: '' },
      })

      await store.addProductCost({ product: 7, component_type: 1, amount_per_dozen: 12, valid_from: '2026-04-01' })

      expect(store.productCosts).toHaveLength(2)
      expect(store.productCosts[0].id).toBe(2)
      expect(store.productCosts[1].id).toBe(1)
    })

    it('deletes a cost entry and removes it from state', async () => {
      const store = useProfitStore()
      store.productCosts = [
        { id: 1, product: 7, product_name: 'Widget', component_type: 1, component_type_name: 'Labor', amount_per_dozen: '10.00', valid_from: '2026-01-01', created_at: '' },
      ]
      vi.mocked(api.delete).mockResolvedValueOnce({ data: null })

      await store.deleteProductCost(1)

      expect(api.delete).toHaveBeenCalledWith('/profit/product-costs/1/')
      expect(store.productCosts).toHaveLength(0)
    })

    it('fetches the current effective cost, omitting as_of when not provided', async () => {
      const store = useProfitStore()
      vi.mocked(api.get).mockResolvedValueOnce({
        data: { product: 7, as_of: '2026-08-09', components: [], total_per_dozen: '15.00', using_fallback_cop: true },
      })

      await store.fetchCurrentCost(7)

      expect(api.get).toHaveBeenCalledWith('/profit/product-costs/current/', { params: { product: '7' } })
      expect(store.currentCost?.using_fallback_cop).toBe(true)
    })
  })

  describe('summary and trend', () => {
    it('populates summaryTotals when no group_by is passed', async () => {
      const store = useProfitStore()
      vi.mocked(api.get).mockResolvedValueOnce({
        data: { unit: 'dozen', quantity: 15, revenue: '1790.00', cost: '670.00', profit_amount: '1120.00', profit_ratio: '0.625', profit_per_unit: '74.66' },
      })

      await store.fetchSummary({ city: 'Lahore' })

      expect(api.get).toHaveBeenCalledWith('/profit/summary/', { params: { city: 'Lahore' } })
      expect(store.summaryTotals?.profit_amount).toBe('1120.00')
    })

    it('populates summaryRows and strips empty filter values when group_by is passed', async () => {
      const store = useProfitStore()
      vi.mocked(api.get).mockResolvedValueOnce({
        data: { unit: 'dozen', group_by: 'location', rows: [{ key: 'Lahore', label: 'Lahore', unit: 'dozen', quantity: 18, revenue: '1240.00', cost: '470.00', profit_amount: '770.00', profit_ratio: '0.62', profit_per_unit: '42.7' }] },
      })

      await store.fetchSummary({ city: '', product: '' }, 'location')

      expect(api.get).toHaveBeenCalledWith('/profit/summary/', { params: { group_by: 'location' } })
      expect(store.summaryRows).toHaveLength(1)
      expect(store.summaryRows[0].label).toBe('Lahore')
    })

    it('fetches trend data shaped for the chart', async () => {
      const store = useProfitStore()
      vi.mocked(api.get).mockResolvedValueOnce({
        data: { categories: ['2026-01', '2026-04'], series: [{ name: 'Tracked Widget', data: [650, 350] }] },
      })

      await store.fetchTrend({ product: 3 }, 'month', 'product' as any, 'profit_amount')

      expect(api.get).toHaveBeenCalledWith('/profit/trend/', {
        params: { product: '3', x: 'month', series: 'product', metric: 'profit_amount' },
      })
      expect(store.trend.categories).toEqual(['2026-01', '2026-04'])
      expect(store.trend.series[0].name).toBe('Tracked Widget')
    })
  })
})
