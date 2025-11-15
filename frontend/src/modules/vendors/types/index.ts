export interface VendorProduct {
  id?: number
  vendor: number
  vendor_name?: string
  product_type: 'PRODUCT' | 'RAW_MATERIAL'
  product?: number
  raw_material?: number
  item_name: string
  item_unit: string
  unit_price: number
  minimum_order_quantity: number
  lead_time_days: number
  is_preferred: boolean
  is_active: boolean
  notes?: string
  last_purchase_date?: string
  last_purchase_price?: number
  created_at?: string
  updated_at?: string
}

export interface Vendor {
  id: number
  name: string
  email: string
  phone: string
  address: string
  contact_person: string
  is_active: boolean
  vendor_products?: VendorProduct[]
  total_products_count?: number
  created_at: string
  updated_at: string
}

export interface CreateVendorRequest {
  name: string
  email: string
  phone: string
  address: string
  contact_person: string
  is_active: boolean
  vendor_products?: any[]
}

export interface UpdateVendorRequest extends Partial<CreateVendorRequest> {}

export interface VendorStats {
  total: number
  active: number
  inactive: number
} 