
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
  product: number
  size_range: number
  color: number
  quantity_dozens: number
  created_at: string
}

export interface Product {
  id: number
  name: string
  unit: 'BAG' | 'KILO' | 'PCS' | 'KG' | 'L' | 'M' | 'BOX' | 'PACK' | 'UNIT' | 'GRAM' | 'TON' | 'GALLON' | 'FOOT' | 'YARD' | 'CM' | 'MM' | 'INCH' | 'POUND' | 'OUNCE' | 'CUP' | 'TABLESPOON' | 'TEASPOON'
  cop: number
  quantity: number
  size_range: number | null
  size_range_name?: string
  variants: ProductVariant[]
  created_at: string
  last_updated: string
}

export interface ProductHistory {
  id: number
  product: number
  change_type: 'SALE' | 'PURCHASE' | 'ADJUSTMENT'
  quantity_change: number
  date: string
  reference: string
  notes: string
}

export interface CreateProductRequest {
  name: string
  unit: 'BAG' | 'KILO' | 'PCS' | 'KG' | 'L' | 'M' | 'BOX' | 'PACK' | 'UNIT' | 'GRAM' | 'TON' | 'GALLON' | 'FOOT' | 'YARD' | 'CM' | 'MM' | 'INCH' | 'POUND' | 'OUNCE' | 'CUP' | 'TABLESPOON' | 'TEASPOON'
  cop: number
  quantity: number
}

export interface UpdateProductRequest {
  name?: string
  unit?: 'BAG' | 'KILO' | 'PCS' | 'KG' | 'L' | 'M' | 'BOX' | 'PACK' | 'UNIT' | 'GRAM' | 'TON' | 'GALLON' | 'FOOT' | 'YARD' | 'CM' | 'MM' | 'INCH' | 'POUND' | 'OUNCE' | 'CUP' | 'TABLESPOON' | 'TEASPOON'
  cop?: number
  quantity?: number
}

export interface ProductFilters {
  search?: string
  name?: string
  unit?: 'BAG' | 'KILO' | 'PCS' | 'KG' | 'L' | 'M' | 'BOX' | 'PACK' | 'UNIT' | 'GRAM' | 'TON' | 'GALLON' | 'FOOT' | 'YARD' | 'CM' | 'MM' | 'INCH' | 'POUND' | 'OUNCE' | 'CUP' | 'TABLESPOON' | 'TEASPOON'
  min_price?: number
  max_price?: number
  low_stock?: boolean
  in_stock?: boolean
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
} 