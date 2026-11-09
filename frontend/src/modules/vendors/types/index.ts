export interface Vendor {
  id: number
  name: string
  phone: string | null
  address: string | null
  city: string | null
  contact_person: string | null
  balance: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface VendorFormPayload {
  name: string
  phone: string
  address: string
  city: string
  contact_person: string
  is_active: boolean
}

export interface VendorTransaction {
  id: number
  vendor: number
  type: 'PURCHASE' | 'PAYMENT'
  amount: string
  date: string
  reference: string | null
  notes: string | null
}

export interface VendorPayment {
  id: number
  purchase: { id: number } | null
}

export interface LedgerRow {
  id: number
  date: string
  type: 'PURCHASE' | 'PAYMENT'
  reference: string
  debit: number
  credit: number
  balance: number
}

export interface VendorPaymentPayload {
  vendor: number
  purchase?: number
  payment_method: 'CASH' | 'BANK' | 'CHEQUE' | 'PARCHI'
  amount: number
  bank_name?: string
  reference: string
  notes: string
}
