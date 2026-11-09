import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import api from '../../../../shared/api/axios'
import { useSalesStore } from '../sales'

vi.mock('../../../../shared/api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
}))

const sale = (id: number) => ({ id, bill_no: `BILL-${id}` }) as any

describe('sales store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('prepends the created sale to the list', async () => {
    const store = useSalesStore()
    store.sales = [sale(1)]
    vi.mocked(api.post).mockResolvedValue({ data: sale(2) })
    await store.createSale({ customer: 1, sale_type: 'REGULAR', amount_received: 0, payment_method: 'CASH', items: [] })
    expect(store.sales.map(s => s.id)).toEqual([2, 1])
  })

  it('removes the deleted sale from the list', async () => {
    const store = useSalesStore()
    store.sales = [sale(1), sale(2)]
    vi.mocked(api.delete).mockResolvedValue({})
    await store.deleteSale(1)
    expect(store.sales.map(s => s.id)).toEqual([2])
  })

  it('leaves the list untouched and rethrows when a write fails', async () => {
    const store = useSalesStore()
    store.sales = [sale(1)]
    vi.mocked(api.delete).mockRejectedValue({ response: { status: 400, data: { items: 'x' } } })
    await expect(store.deleteSale(1)).rejects.toBeTruthy()
    expect(store.sales.map(s => s.id)).toEqual([1])
    expect(store.error).toBeNull()
  })
})
