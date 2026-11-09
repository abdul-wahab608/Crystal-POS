export interface ProductionRunItem {
  id: number
  variant: number
  variant_label: string
  unit: string
  quantity: string
}

export interface ProductionRunInput {
  id: number
  raw_material: number
  raw_material_name: string
  unit: string
  quantity: string
}

export interface ProductionRun {
  id: number
  date: string
  reference: string
  notes: string
  items: ProductionRunItem[]
  inputs: ProductionRunInput[]
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
  variants: ProductVariantLine[]
}

export interface RawMaterialOption {
  id: number
  name: string
  unit: string
  quantity: string
}

export interface CreateProductionRunRequest {
  reference: string
  notes: string
  items: { variant: number; quantity: number }[]
  inputs: { raw_material: number; quantity: number }[]
}
