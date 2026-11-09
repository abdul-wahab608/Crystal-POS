import { describe, it, expect } from 'vitest'
import {
  emptyLine,
  lineProblems,
  lineSubtotal,
  purchaseTotal,
  toPurchaseItem,
  colorOptionsFor,
  sizeRangeOptionsFor,
  type PurchaseLineDraft,
} from '../purchaseLines'
import type { Color, Product, SizeRange } from '../../types'

const rawLine = (overrides: Partial<PurchaseLineDraft> = {}): PurchaseLineDraft => ({
  ...emptyLine('raw'),
  raw_material: 3,
  quantity: 10,
  unit_cost: 4.5,
  ...overrides,
})

const productLine = (overrides: Partial<PurchaseLineDraft> = {}): PurchaseLineDraft => ({
  ...emptyLine('product'),
  product: 7,
  size_range: 1,
  color: 2,
  quantity: 3,
  unit_cost: 12.5,
  ...overrides,
})

describe('purchase line totals', () => {
  it('computes a line subtotal from quantity and unit cost', () => {
    expect(lineSubtotal(rawLine())).toBe(45)
    expect(lineSubtotal(productLine({ quantity: 2.5, unit_cost: 3.34 }))).toBe(8.35)
  })

  it('treats an empty quantity or cost as zero', () => {
    expect(lineSubtotal({ quantity: null, unit_cost: 5 })).toBe(0)
    expect(lineSubtotal({ quantity: 4, unit_cost: null })).toBe(0)
  })

  it('sums the document total across raw and product lines without float drift', () => {
    const lines = [
      rawLine({ quantity: 0.1, unit_cost: 0.3 }),
      productLine({ quantity: 3, unit_cost: 12.5 }),
      rawLine({ quantity: 7, unit_cost: 0.1 }),
    ]
    expect(purchaseTotal(lines)).toBe(38.23)
  })

  it('is zero for an empty document', () => {
    expect(purchaseTotal([])).toBe(0)
  })
})

describe('mixed-line validation', () => {
  it('accepts a complete raw material line', () => {
    expect(lineProblems(rawLine())).toEqual([])
  })

  it('accepts a complete product line', () => {
    expect(lineProblems(productLine())).toEqual([])
  })

  it('rejects a raw line that still carries a product or variant', () => {
    const problems = lineProblems(rawLine({ product: 7, size_range: 1, color: 2 }))
    expect(problems).toContain('A raw material line cannot have a product, size range or color.')
  })

  it('rejects a product line that still carries a raw material', () => {
    const problems = lineProblems(productLine({ raw_material: 3 }))
    expect(problems).toContain('A product line cannot have a raw material.')
  })

  it('rejects a raw line with no raw material', () => {
    expect(lineProblems(rawLine({ raw_material: null }))).toContain('Choose a raw material.')
  })

  it('requires product, size range and color on a product line', () => {
    const problems = lineProblems(productLine({ product: null, size_range: null, color: null }))
    expect(problems).toEqual(expect.arrayContaining([
      'Choose a product.',
      'Choose a size range.',
      'Choose a color.',
    ]))
  })

  it('rejects zero or missing quantity and missing unit cost', () => {
    expect(lineProblems(rawLine({ quantity: 0 }))).toEqual(['Quantity must be greater than zero.'])
    expect(lineProblems(rawLine({ quantity: null, unit_cost: null }))).toEqual([
      'Quantity must be greater than zero.',
      'Unit cost is required.',
    ])
  })

  it('allows a zero unit cost but not a negative one', () => {
    expect(lineProblems(rawLine({ unit_cost: 0 }))).toEqual([])
    expect(lineProblems(rawLine({ unit_cost: -1 }))).toEqual(['Unit cost is required.'])
  })
})

describe('payload for a purchase line', () => {
  it('sends only the raw material for a raw line', () => {
    expect(toPurchaseItem(rawLine())).toEqual({ raw_material: 3, quantity: 10, unit_cost: 4.5 })
  })

  it('sends product, size range and color for a product line', () => {
    expect(toPurchaseItem(productLine())).toEqual({
      product: 7, size_range: 1, color: 2, quantity: 3, unit_cost: 12.5,
    })
  })
})

describe('line option limits', () => {
  const sizes: SizeRange[] = [{ id: 1, name: 'S' }, { id: 2, name: 'M' }, { id: 3, name: 'L' }]
  const colors: Color[] = [{ id: 2, name: 'Black' }, { id: 5, name: 'Tan' }]
  const product: Product = {
    id: 7,
    name: 'Shoe',
    unit: 'PCS',
    size_ranges: [1, 2],
    variants: [{ id: 1, size_range: 1, size_range_name: 'S', color: 2, color_name: 'Black', quantity: '0' }],
  }

  it('limits size ranges to the product size ranges', () => {
    expect(sizeRangeOptionsFor(product, sizes).map(s => s.id)).toEqual([1, 2])
  })

  it('limits colors to those existing on the product variants', () => {
    expect(colorOptionsFor(product, colors).map(c => c.id)).toEqual([2])
  })

  it('offers every color when the product has no variants yet', () => {
    expect(colorOptionsFor({ ...product, variants: [] }, colors)).toEqual(colors)
  })
})
