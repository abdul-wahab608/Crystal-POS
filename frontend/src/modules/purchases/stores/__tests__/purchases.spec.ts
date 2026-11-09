import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePurchasesStore } from '../purchases'

vi.mock('../../../../shared/api/axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

import api from '../../../../shared/api/axios'

describe('PurchasesStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('posts vendor and item lines without a client-computed total', async () => {
    const store = usePurchasesStore()
    vi.mocked(api.post).mockResolvedValueOnce({ data: { id: 7, vendor: 2, items: [], total_amount: '30.00' } })

    await store.createPurchase({ vendor: 2, items: [{ product: 5, quantity: 3, unit_cost: 10 }] })

    expect(api.post).toHaveBeenCalledWith('/purchases/', { vendor: 2, items: [{ product: 5, quantity: 3, unit_cost: 10 }] })
    expect(store.purchases[0].id).toBe(7)
  })

  it('removes the deleted purchase from the list', async () => {
    const store = usePurchasesStore()
    store.purchases = [{ id: 1 } as any, { id: 2 } as any]
    vi.mocked(api.delete).mockResolvedValueOnce({ data: null })

    await store.deletePurchase(1)

    expect(api.delete).toHaveBeenCalledWith('/purchases/1/')
    expect(store.purchases.map(p => p.id)).toEqual([2])
  })
})
