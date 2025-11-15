export interface Purchase {
  id: number
  vendor: number
  vendor_name: string
  total_amount: number
  invoice_number: string
  payment_status: string
  date: string
  created_at: string
}

export interface CreatePurchaseRequest {
  vendor: number
  total_amount: number
  invoice_number: string
  payment_status?: string
}

export interface UpdatePurchaseRequest {
  vendor?: number
  total_amount?: number
  invoice_number?: string
  payment_status?: string
} 