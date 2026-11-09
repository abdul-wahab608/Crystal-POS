import { describe, expect, it } from 'vitest'
import type { Product } from '../../types'
import { buildStockGrid, cellKey } from '../stockGrid'

const product: Product = {
  id: 1,
  name: 'Oxford',
  unit: 'DOZEN',
  cop: '100.00',
  quantity: 7,
  product_type: 'MANUFACTURED',
  size_ranges: [10, 11],
  variants: [
    { id: 1, size_range: 10, size_range_name: 'Men', color: 5, color_name: 'Black', quantity: '4' },
    { id: 2, size_range: 10, size_range_name: 'Men', color: 6, color_name: 'Brown', quantity: '2' },
    { id: 3, size_range: 12, size_range_name: 'Kids', color: 5, color_name: 'Black', quantity: '1' },
  ],
  created_at: '',
  last_updated: '',
}

describe('buildStockGrid', () => {
  const names: Record<number, string> = { 10: 'Men', 11: 'Women', 12: 'Kids' }
  const grid = buildStockGrid(product, id => names[id])

  it('lists linked size ranges first, then variant-only sizes', () => {
    expect(grid.sizes.map(s => s.name)).toEqual(['Men', 'Women', 'Kids'])
  })

  it('lists colors in first-seen order', () => {
    expect(grid.colors.map(c => c.name)).toEqual(['Black', 'Brown'])
  })

  it('maps each size and color pair to its quantity', () => {
    expect(grid.cells[cellKey(10, 5)]).toBe(4)
    expect(grid.cells[cellKey(10, 6)]).toBe(2)
    expect(grid.cells[cellKey(12, 5)]).toBe(1)
    expect(grid.cells[cellKey(11, 5)]).toBeUndefined()
  })
})
