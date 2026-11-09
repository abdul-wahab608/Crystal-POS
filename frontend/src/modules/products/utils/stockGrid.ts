import type { Product } from '../types'

export interface StockGrid {
  sizes: { id: number; name: string }[]
  colors: { id: number; name: string }[]
  cells: Record<string, number>
}

export function cellKey(sizeId: number, colorId: number): string {
  return `${sizeId}-${colorId}`
}

export function buildStockGrid(product: Product, sizeNameOf: (id: number) => string): StockGrid {
  const sizeIds = [...product.size_ranges]
  const colors: StockGrid['colors'] = []
  const cells: Record<string, number> = {}

  for (const variant of product.variants) {
    if (!sizeIds.includes(variant.size_range)) sizeIds.push(variant.size_range)
    if (!colors.some(c => c.id === variant.color)) colors.push({ id: variant.color, name: variant.color_name })
    cells[cellKey(variant.size_range, variant.color)] = Number(variant.quantity)
  }

  return {
    sizes: sizeIds.map(id => ({ id, name: sizeNameOf(id) })),
    colors,
    cells,
  }
}
