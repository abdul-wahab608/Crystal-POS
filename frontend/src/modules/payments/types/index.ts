export type PaymentDirection = 'INCOMING' | 'OUTGOING'
export type PaymentMethod = 'CASH' | 'BANK' | 'CHEQUE' | 'PARCHI'
export type PaymentStatus = 'PENDING' | 'PARTIAL' | 'COMPLETED' | 'OVERDUE'

export interface Payment {
  id: number
  payment_type: PaymentDirection | 'DIRECT'
  payment_method: PaymentMethod
  amount: string
  status: PaymentStatus
  customer: { id: number; name: string } | null
  vendor: { id: number; name: string } | null
  sale: { id: number; bill_no: string } | null
  purchase: { id: number } | null
  bank_account: { id: number; name: string } | null
  payment_date: string
  reference: string | null
  notes: string | null
}

export interface PaymentRequest {
  payment_type: PaymentDirection
  payment_method: PaymentMethod
  amount: string
  customer?: number
  vendor?: number
  sale?: number
  purchase?: number
  bank_account?: number
  payment_date: string
  reference?: string
  notes?: string
}

export interface PaymentFilters {
  payment_type?: PaymentDirection
  date_from?: string
  date_to?: string
  search?: string
}

export interface Vendor {
  id: number
  name: string
}

export interface BankAccount {
  id: number
  name: string
  bank_name: string
}
