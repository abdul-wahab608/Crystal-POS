export interface PurchaseItem {
  id: number
  purchase: number
  product: number
  product_name: string
  quantity: string
  unit_cost: string
  subtotal: string
}

export interface Purchase {
  id: number
  vendor: number
  vendor_name: string
  total_amount: string
  date: string
  created_by: number | null
  items: PurchaseItem[]
}

export interface CreatePurchaseItem {
  product: number
  quantity: number
  unit_cost: number
  subtotal: number
}

export interface CreatePurchaseRequest {
  vendor: number
  total_amount: number
  items: CreatePurchaseItem[]
}

export interface UpdatePurchaseRequest {
  vendor?: number
  total_amount?: number
}