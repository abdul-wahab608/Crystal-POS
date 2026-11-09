export type SaleType = 'WALK_IN' | 'PHONE_ORDER' | 'REGULAR'
export type PaymentStatus = 'PAID' | 'PARTIAL' | 'UNPAID'
export type PaymentMethod = 'CASH' | 'BANK' | 'CHEQUE' | 'PARCHI'

export interface SaleItem {
  id: number
  product: number
  product_name: string
  size_range: number
  size_range_name: string
  color: number
  color_name: string
  quantity: string
  unit_price: string
  subtotal: string
}

export interface Sale {
  id: number
  bill_no: string
  sale_type: SaleType
  customer: number
  customer_name: string
  customer_city: string | null
  date: string
  total_amount: string
  amount_paid: string
  balance: string
  payment_status: PaymentStatus
  items_count: number
  sale_items: SaleItem[]
  created_by: number | null
}

export interface SaleItemRequest {
  product_id: number
  size_range_id: number
  color_id: number
  quantity: string
  unit_price: string
}

export interface CreateSaleRequest {
  customer: number
  sale_type: SaleType
  items: SaleItemRequest[]
  amount_received?: string
  payment_method?: PaymentMethod
}

export interface SaleFilters {
  customer?: number
  payment_status?: PaymentStatus
  date_from?: string
  date_to?: string
  search?: string
}

export interface CatalogVariant {
  id: number
  size_range: number
  size_range_name: string
  color: number
  color_name: string
  quantity: string
}

export interface CatalogProduct {
  id: number
  name: string
  unit: string
  size_ranges: number[]
  variants: CatalogVariant[]
}

export interface CatalogSizeRange {
  id: number
  name: string
}
