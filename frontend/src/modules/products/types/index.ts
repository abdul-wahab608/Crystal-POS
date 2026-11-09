import type { CostSource } from '../../profit/types'

export interface SizeRange {
  id: number
  name: string
  created_at: string
}

export interface Color {
  id: number
  name: string
  created_at: string
}

export interface ProductVariant {
  id: number
  size_range: number
  size_range_name: string
  color: number
  color_name: string
  quantity: number | string
}

export interface VariantRecord extends ProductVariant {
  product: number
  created_at: string
}

export interface Product {
  id: number
  name: string
  unit: string
  cop: number | string
  cost_source: CostSource
  quantity: number | string
  product_type: 'MANUFACTURED' | 'PURCHASED'
  size_ranges: number[]
  variants: ProductVariant[]
  created_at: string
  last_updated: string
}

export interface VariantInput {
  size_range: number
  color: number
  quantity: number
}

export interface ProductPayload {
  name: string
  unit: string
  cop: number
  product_type: 'MANUFACTURED' | 'PURCHASED'
  size_ranges: number[]
  variants: VariantInput[]
}

export type CreateProductRequest = ProductPayload
export type UpdateProductRequest = Partial<ProductPayload>
