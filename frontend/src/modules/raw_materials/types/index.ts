export interface RawMaterial {
  id: number
  name: string
  unit: string
  quantity: string
  reorder_level: string
  needs_reorder: boolean
  created_at: string
  updated_at: string
}

export interface RawMaterialUsage {
  id: number
  raw_material: number
  raw_material_name: string
  quantity_used: string
  reference: string | null
  notes: string | null
  date_used: string
}

export interface RawMaterialFormPayload {
  name: string
  unit: string
  reorder_level: number
  quantity?: number
}

export interface CreateRawMaterialUsage {
  raw_material: number
  quantity_used: number
  reference: string
  notes: string
}
