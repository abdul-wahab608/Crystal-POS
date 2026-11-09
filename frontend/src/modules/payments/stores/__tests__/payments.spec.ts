import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import api from '../../../../shared/api/axios'
import { usePaymentsStore } from '../payments'

vi.mock('../../../../shared/api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

const payment = (id: number) => ({ id, amount: '10.00' }) as any

describe('payments store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('passes direction and date filters to the list request', async () => {
    const store = usePaymentsStore()
    vi.mocked(api.get).mockResolvedValue({ data: [payment(1)] })
    await store.fetchPayments({ payment_type: 'INCOMING', date_from: '2026-11-01', date_to: '2026-11-09' })
    expect(api.get).toHaveBeenCalledWith('/payments/', {
      params: { payment_type: 'INCOMING', date_from: '2026-11-01', date_to: '2026-11-09' },
    })
    expect(store.payments.map(p => p.id)).toEqual([1])
  })

  it('posts a new payment and returns the saved row without touching the list', async () => {
    const store = usePaymentsStore()
    store.payments = [payment(1)]
    vi.mocked(api.post).mockResolvedValue({ data: { id: 2 } })
    const saved = await store.createPayment({
      payment_type: 'INCOMING', payment_method: 'CASH', amount: '10.00', customer: 1, payment_date: '2026-11-09',
    })
    expect(saved.id).toBe(2)
    expect(store.payments.map(p => p.id)).toEqual([1])
  })

  it('removes a deleted payment', async () => {
    const store = usePaymentsStore()
    store.payments = [payment(1), payment(2)]
    vi.mocked(api.delete).mockResolvedValue({})
    await store.deletePayment(1)
    expect(store.payments.map(p => p.id)).toEqual([2])
  })
})
