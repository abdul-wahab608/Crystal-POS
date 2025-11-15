export interface SaleItem {
  id: number
  sale: number
  product: number
  product_name: string
  quantity: number
  unit_price: number
  total_price: number
}

export interface Sale {
  id: number
  customer: number
  customer_name: string
  total_amount: number
  total: number
  date: string
  payment_status: string
  sale_items: SaleItem[]
  created_at: string
  updated_at: string
}

export interface CreateSaleItem {
  product_id: number
  quantity: number
}

export interface CreateSaleRequest {
  customer: number
  total_amount: number
  date: string
  payment_status: string
  items: SaleItemRequest[]
}

export interface SaleItemRequest {
  product_id: number
  quantity: number
}

export interface UpdateSaleRequest extends Partial<CreateSaleRequest> {}

export interface SaleStats {
  total: number
  totalAmount: number
  averageAmount: number
} 