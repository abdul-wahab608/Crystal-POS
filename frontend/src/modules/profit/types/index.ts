export interface CostComponentType {
  id: number
  name: string
  is_system: boolean
  created_at: string
}

export interface ProductCost {
  id: number
  product: number
  product_name: string
  component_type: number
  component_type_name: string
  amount_per_dozen: number | string
  valid_from: string
  created_at: string
}

export interface CreateProductCost {
  product: number
  component_type: number
  amount_per_dozen: number
  valid_from: string
}

export interface CurrentCostComponent {
  component_type: number
  component_type_name: string
  amount_per_dozen: number | string
  valid_from: string
}

export interface CurrentCost {
  product: number
  as_of: string
  components: CurrentCostComponent[]
  total_per_dozen: number | string
  using_fallback_cop: boolean
}

export type ProfitUnit = 'dozen' | 'piece'
export type ProfitGroupBy = 'product' | 'month' | 'season' | 'year' | 'location'
export type ProfitMetric = 'revenue' | 'cost' | 'profit_amount' | 'profit_ratio' | 'profit_per_unit' | 'quantity'

export interface ProfitFilters {
  product?: number | string
  size_range?: number | string
  color?: number | string
  city?: string
  year?: number | string
  month?: number | string
  season?: string
  date_from?: string
  date_to?: string
}

export interface ProfitSummaryTotals {
  unit: ProfitUnit
  quantity: number | string
  revenue: number | string
  cost: number | string
  profit_amount: number | string
  profit_ratio: number | string
  profit_per_unit: number | string
}

export interface ProfitSummaryRow extends ProfitSummaryTotals {
  key: string | number
  label: string
}

export interface ProfitTrend {
  categories: string[]
  series: { name: string; data: number[] }[]
}
