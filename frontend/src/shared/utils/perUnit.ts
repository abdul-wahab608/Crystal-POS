export interface UnitQuantity {
  unit: string
  quantity: number | string
}

export function formatMoney(value: number | string | null | undefined): string {
  return Number(value ?? 0).toLocaleString('en-PK', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

export function formatQuantity(value: number | string | null | undefined): string {
  return Number(value ?? 0).toLocaleString('en-PK', { maximumFractionDigits: 2 })
}

export function formatQuantityLines(quantities: UnitQuantity[]): string[] {
  return [...quantities]
    .sort((a, b) => a.unit.localeCompare(b.unit))
    .map((q) => `${formatQuantity(q.quantity)} ${q.unit}`)
}

export function groupByUnit<T extends Record<string, any>>(rows: T[]): { unit: string; rows: T[] }[] {
  const groups = new Map<string, T[]>()
  for (const row of rows) {
    const unit = String(row.unit)
    const bucket = groups.get(unit)
    if (bucket) bucket.push(row)
    else groups.set(unit, [row])
  }
  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([unit, groupRows]) => ({ unit, rows: groupRows }))
}

export function sumField<T>(rows: T[], field: keyof T): number {
  return rows.reduce((total, row) => total + Number(row[field] ?? 0), 0)
}
