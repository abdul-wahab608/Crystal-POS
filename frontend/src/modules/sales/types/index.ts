export interface SaleItem {
  id: number
  sale: number
  product: number
  product_name: string
  size_range: number
  size_range_name: string
  color: number
  color_name: string
  quantity_dozens: number
  unit_price: number
  subtotal: number
}

export interface Sale {
  id: number
  bill_no: string
  sale_type: 'WALK_IN' | 'PHONE_ORDER' | 'REGULAR'
  customer: number
  customer_name: string
  customer_city?: string
  total_amount: number
  total: number
  date: string
  payment_status: 'PAID' | 'PARTIAL' | 'UNPAID'
  sale_items: SaleItem[]
  items_count: number
  created_at?: string
}

export interface CreateSaleRequest {
  customer: number
  sale_type: 'WALK_IN' | 'PHONE_ORDER' | 'REGULAR'
  total_amount: number
  total?: number
  date: string
  payment_status: 'PAID' | 'PARTIAL' | 'UNPAID'
  items: SaleItemRequest[]
}

export interface SaleItemRequest {
  product_id: number
  size_range_id?: number
  color_id?: number
  quantity_dozens: number
  unit_price: number
}

export interface UpdateSaleRequest extends Partial<CreateSaleRequest> {}

export interface SaleStats {
  total: number
  totalAmount: number
  averageAmount: number
}
