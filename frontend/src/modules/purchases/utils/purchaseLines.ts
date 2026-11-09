import type { Product, Color, SizeRange, PurchaseItemPayload } from '../types'

export type LineKind = 'raw' | 'product'

export interface PurchaseLineDraft {
  kind: LineKind
  raw_material: number | null
  product: number | null
  size_range: number | null
  color: number | null
  quantity: number | null
  unit_cost: number | null
}

export function emptyLine(kind: LineKind = 'raw'): PurchaseLineDraft {
  return { kind, raw_material: null, product: null, size_range: null, color: null, quantity: null, unit_cost: null }
}

export function lineSubtotal(line: Pick<PurchaseLineDraft, 'quantity' | 'unit_cost'>): number {
  return Math.round((Number(line.quantity) || 0) * (Number(line.unit_cost) || 0) * 100) / 100
}

export function purchaseTotal(lines: Pick<PurchaseLineDraft, 'quantity' | 'unit_cost'>[]): number {
  return lines.reduce((sum, line) => sum + Math.round(lineSubtotal(line) * 100), 0) / 100
}

export function lineProblems(line: PurchaseLineDraft): string[] {
  const problems: string[] = []
  if (line.kind === 'raw') {
    if (line.raw_material === null) problems.push('Choose a raw material.')
    if (line.product !== null || line.size_range !== null || line.color !== null) {
      problems.push('A raw material line cannot have a product, size range or color.')
    }
  } else {
    if (line.product === null) problems.push('Choose a product.')
    if (line.size_range === null) problems.push('Choose a size range.')
    if (line.color === null) problems.push('Choose a color.')
    if (line.raw_material !== null) problems.push('A product line cannot have a raw material.')
  }
  if (!(Number(line.quantity) > 0)) problems.push('Quantity must be greater than zero.')
  if (line.unit_cost === null || !(Number(line.unit_cost) >= 0)) problems.push('Unit cost is required.')
  return problems
}

export function toPurchaseItem(line: PurchaseLineDraft): PurchaseItemPayload {
  const amounts = { quantity: Number(line.quantity), unit_cost: Number(line.unit_cost) }
  if (line.kind === 'raw') {
    return { raw_material: line.raw_material as number, ...amounts }
  }
  return {
    product: line.product as number,
    size_range: line.size_range as number,
    color: line.color as number,
    ...amounts,
  }
}

export function sizeRangeOptionsFor(product: Product | undefined, sizeRanges: SizeRange[]): SizeRange[] {
  if (!product) return []
  return sizeRanges.filter(size => product.size_ranges.includes(size.id))
}

export function colorOptionsFor(product: Product | undefined, colors: Color[]): Color[] {
  if (!product) return []
  const used = new Set(product.variants.map(variant => variant.color))
  if (used.size === 0) return colors
  return colors.filter(color => used.has(color.id))
}
