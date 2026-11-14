import type { CostSource } from '../types'

export const COST_MISSING_MESSAGE = 'Cost missing: add production or a manual cost'

const LABELS: Record<CostSource, string> = {
  MANUAL: 'Manual cost',
  PRODUCTION: 'From production',
  PURCHASE: 'From purchase price',
  COP: 'Cost of production (fallback)',
  MISSING: 'Cost missing',
}

export function costSourceLabel(source: CostSource | null | undefined): string {
  return source ? LABELS[source] : '—'
}
