import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('../../../../shared/api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
}))

import api from '../../../../shared/api/axios'
import { useVendorBill } from '../useVendorBill'

const bill = (id: number, unpaid: string, vendor = 1) => ({
  id,
  vendor,
  date: '2026-11-01T10:00:00Z',
  total_amount: '500.00',
  paid_amount: '0.00',
  unpaid_amount: unpaid,
  payment_status: 'UNPAID',
  invoice_number: '',
  vendor_name: 'V',
  created_by: null,
  items: [],
})

describe('useVendorBill', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('offers only the selected vendor bills that still have a balance', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: [bill(3, '200.00', 1), bill(4, '50.00', 2)] })
    const vendorBill = useVendorBill()

    await vendorBill.loadBills(1)

    expect(api.get).toHaveBeenCalledWith('/purchases/', { params: { unpaid: true } })
    expect(vendorBill.options.value.map(o => o.value)).toEqual([3])
    expect(vendorBill.options.value[0].label).toContain('Purchase #3')
  })

  it('refuses an amount above the chosen bill unpaid balance', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: [bill(3, '200.00')] })
    const vendorBill = useVendorBill()
    await vendorBill.loadBills(1)
    vendorBill.billId.value = 3

    expect(vendorBill.billError(250)).toContain('Purchase #3')
    expect(vendorBill.billError(200)).toBe('')
  })

  it('does not check the amount when no bill is chosen', async () => {
    const vendorBill = useVendorBill()

    expect(vendorBill.billError(99999)).toBe('')
  })
})
