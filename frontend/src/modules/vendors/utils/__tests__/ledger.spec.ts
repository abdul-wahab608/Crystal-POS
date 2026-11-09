import { describe, it, expect } from 'vitest'
import { buildLedger, openingBalance } from '../ledger'
import type { VendorTransaction } from '../../types'

const txn = (id: number, type: VendorTransaction['type'], amount: string, date: string): VendorTransaction => ({
  id, vendor: 1, type, amount, date, reference: `R${id}`, notes: null,
})

describe('vendor ledger', () => {
  const transactions = [
    txn(2, 'PAYMENT', '5.00', '2026-03-02T10:00:00Z'),
    txn(1, 'PURCHASE', '20.00', '2026-03-01T10:00:00Z'),
    txn(3, 'PURCHASE', '3.00', '2026-03-03T10:00:00Z'),
  ]

  it('orders rows by date and runs the balance through purchases and payments', () => {
    const rows = buildLedger({ balance: '18.00' }, transactions)
    expect(rows.map(row => row.id)).toEqual([1, 2, 3])
    expect(rows.map(row => row.balance)).toEqual([20, 15, 18])
    expect(rows[0]).toMatchObject({ type: 'PURCHASE', debit: 20, credit: 0 })
    expect(rows[1]).toMatchObject({ type: 'PAYMENT', debit: 0, credit: 5 })
  })

  it('starts from an opening balance when the vendor balance was set outside the ledger', () => {
    expect(openingBalance({ balance: '30.00' }, transactions)).toBe(12)
    expect(buildLedger({ balance: '30.00' }, transactions)[0].balance).toBe(32)
  })

  it('has no rows and a zero opening balance for a vendor with no history', () => {
    expect(buildLedger({ balance: '0' }, [])).toEqual([])
    expect(openingBalance({ balance: '0' }, [])).toBe(0)
  })
})
