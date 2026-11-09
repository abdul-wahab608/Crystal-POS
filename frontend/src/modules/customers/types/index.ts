export type CustomerType = 'REGULAR' | 'WALK_IN'

export interface Customer {
  id: number
  name: string
  phone: string | null
  address: string | null
  city: string | null
  customer_type: CustomerType
  balance: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CustomerRequest {
  name: string
  phone: string
  address: string
  city: string
  customer_type: CustomerType
  is_active: boolean
}

export interface LedgerRow {
  id: number
  date: string
  type: 'SALE' | 'PAYMENT' | 'REVERSAL'
  reference: string | null
  notes: string | null
  debit: string | null
  credit: string | null
  balance: string
}

export interface CustomerLedger {
  customer: Customer
  rows: LedgerRow[]
}
