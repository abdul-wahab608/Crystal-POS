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

export type CostSource = 'MANUAL' | 'PRODUCTION' | 'PURCHASE' | 'COP' | 'MISSING'

export interface ProductionRunCost {
  run_id: number
  date: string
  output_quantity: number | string
  input_cost: number | string | null
  unit_cost: number | string | null
}

export interface CurrentCost {
  product: number
  as_of: string
  components: CurrentCostComponent[]
  unit_cost: number | string | null
  cost_source: CostSource
  production_run_id: number | null
  production_runs: ProductionRunCost[]
}

export type ProfitGroupBy = 'product' | 'month' | 'season' | 'year' | 'location' | 'unit'
export type ProfitMetric = 'revenue' | 'profit_amount' | 'quantity'

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

export interface ProfitUnitQuantity {
  unit: string
  quantity: number | string
}

export interface ProfitSummaryTotals {
  revenue: number | string
  cost: number | string | null
  profit_amount: number | string | null
  profit_ratio: number | string | null
  quantities: ProfitUnitQuantity[]
  unit: string | null
  quantity: number | string | null
  profit_per_unit: number | string | null
  cost_source: CostSource | null
  cost_sources: CostSource[]
  cost_missing: boolean
}

export interface ProfitSummaryRow extends ProfitSummaryTotals {
  key: string | number
  label: string
}

export interface ProfitTrendSeries {
  name: string
  data: (number | null)[]
  cost_source: (CostSource | null)[]
  cost_missing: boolean[]
}

export interface ProfitTrend {
  categories: string[]
  series: ProfitTrendSeries[]
}
