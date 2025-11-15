export interface RawMaterial {
  id: number
  name: string
  unit: string
  unit_price: number
  quantity: number
  available_stock: number
  supplier?: string
  supplier_contact?: string
  reorder_level: number
  needs_reorder: boolean
  created_at: string
  updated_at: string
}

export interface RawMaterialUsage {
  id: number
  raw_material: number
  quantity_used: number
  reference?: string
  notes?: string
  date_used: string
}

export interface RawMaterialPurchase {
  id: number
  raw_material: number
  quantity_purchased: number
  unit_price: number
  total_amount: number
  supplier?: string
  invoice_number?: string
  notes?: string
  purchase_date: string
}

export interface CreateRawMaterial {
  name: string
  unit: string
  unit_price: number
  quantity: number
  supplier?: string
  supplier_contact?: string
  reorder_level: number
}

export interface CreateRawMaterialUsage {
  raw_material: number
  quantity_used: number
  reference?: string
  notes?: string
}

export interface CreateRawMaterialPurchase {
  raw_material: number
  quantity_purchased: number
  unit_price: number
  supplier?: string
  invoice_number?: string
  notes?: string
} 