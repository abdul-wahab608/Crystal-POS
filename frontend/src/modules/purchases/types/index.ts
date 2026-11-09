export interface PurchaseItem {
  id: number
  product: number | null
  product_name: string | null
  size_range: number | null
  size_range_name: string | null
  color: number | null
  color_name: string | null
  raw_material: number | null
  raw_material_name: string | null
  unit: string
  quantity: string
  unit_cost: string
  subtotal: string
}

export interface Purchase {
  id: number
  vendor: number
  vendor_name: string
  invoice_number: string
  total_amount: string
  paid_amount: string
  unpaid_amount: string
  payment_status: 'PAID' | 'PARTIAL' | 'UNPAID'
  date: string
  created_by: number | null
  items: PurchaseItem[]
}

export interface ProductLinePayload {
  product: number
  size_range: number
  color: number
  quantity: number
  unit_cost: number
}

export interface RawLinePayload {
  raw_material: number
  quantity: number
  unit_cost: number
}

export type PurchaseItemPayload = ProductLinePayload | RawLinePayload

export interface CreatePurchaseRequest {
  vendor: number
  invoice_number?: string
  items: PurchaseItemPayload[]
}

export interface SizeRange {
  id: number
  name: string
}

export interface Color {
  id: number
  name: string
}

export interface ProductVariantLine {
  id: number
  size_range: number
  size_range_name: string
  color: number
  color_name: string
  quantity: string
}

export interface Product {
  id: number
  name: string
  unit: string
  size_ranges: number[]
  variants: ProductVariantLine[]
}

export interface RawMaterialOption {
  id: number
  name: string
  unit: string
}
