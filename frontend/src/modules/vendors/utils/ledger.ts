import type { LedgerRow, Vendor, VendorTransaction } from '../types'

const toCents = (value: string | number) => Math.round(Number(value) * 100)

const debitCents = (row: VendorTransaction) => (row.type === 'PURCHASE' ? toCents(row.amount) : 0)
const creditCents = (row: VendorTransaction) => (row.type === 'PAYMENT' ? toCents(row.amount) : 0)

export function openingBalance(vendor: Pick<Vendor, 'balance'>, transactions: VendorTransaction[]): number {
  const net = transactions.reduce((sum, row) => sum + debitCents(row) - creditCents(row), 0)
  return (toCents(vendor.balance) - net) / 100
}

export function buildLedger(vendor: Pick<Vendor, 'balance'>, transactions: VendorTransaction[]): LedgerRow[] {
  const ordered = [...transactions].sort((a, b) => {
    const byDate = new Date(a.date).getTime() - new Date(b.date).getTime()
    return byDate !== 0 ? byDate : a.id - b.id
  })
  let running = toCents(openingBalance(vendor, transactions))
  return ordered.map(row => {
    running += debitCents(row) - creditCents(row)
    return {
      id: row.id,
      date: row.date,
      type: row.type,
      reference: row.reference ?? '',
      debit: debitCents(row) / 100,
      credit: creditCents(row) / 100,
      balance: running / 100,
    }
  })
}
