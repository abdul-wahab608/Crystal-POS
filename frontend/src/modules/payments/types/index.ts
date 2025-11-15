export interface Payment {
  id: number
  amount: number
  payment_type: string
  payment_method: string
  customer?: number | { id: number; name: string }
  vendor?: number | { id: number; name: string }
  direct_payment_to_vendor?: number | { id: number; name: string }
  related_entity: string
  payment_date: string
  date: string
  status: string
  reference_number: string
  notes: string
  bank_name?: string
  account_number?: string
  created_at: string
  updated_at: string
}

export interface CreatePaymentRequest {
  amount: number
  payment_type: string
  payment_method: string
  customer?: number
  vendor?: number
  related_entity: string
  payment_date: string
  date: string
  status: string
  reference_number: string
  notes: string
}

export interface UpdatePaymentRequest extends Partial<CreatePaymentRequest> {}

export interface PaymentStats {
  total: number
  incoming: number
  outgoing: number
  totalAmount: number
} 