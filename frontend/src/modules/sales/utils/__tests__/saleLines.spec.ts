import { describe, it, expect } from 'vitest'
import { lineTotal, saleTotal, validateLine, lineErrors, type SaleLineDraft } from '../saleLines'

const line = (overrides: Partial<SaleLineDraft> = {}): SaleLineDraft => ({
  key: 1,
  productId: 10,
  sizeRangeId: 2,
  colorId: 3,
  quantity: 2,
  unitPrice: 100,
  ...overrides,
})

const stockFor = (available: number | null) => () => ({ label: 'Shirt (S, Red)', available })

describe('lineTotal and saleTotal', () => {
  it('multiplies quantity by unit price and rounds to paisa', () => {
    expect(lineTotal(line({ quantity: 1.5, unitPrice: 33.33 }))).toBe(50)
  })

  it('treats blank quantity or price as zero', () => {
    expect(lineTotal(line({ quantity: null }))).toBe(0)
    expect(lineTotal(line({ unitPrice: null }))).toBe(0)
  })

  it('sums every line into the sale total', () => {
    const lines = [line({ key: 1, quantity: 3, unitPrice: 100 }), line({ key: 2, quantity: 2, unitPrice: 250.5 })]
    expect(saleTotal(lines)).toBe(801)
  })

  it('returns zero for an empty sale', () => {
    expect(saleTotal([])).toBe(0)
  })
})

describe('validateLine', () => {
  it('accepts a complete line', () => {
    expect(validateLine(line())).toBeNull()
  })

  it('asks for each missing pick in order', () => {
    expect(validateLine(line({ productId: null }))).toBe('Choose a product.')
    expect(validateLine(line({ sizeRangeId: null }))).toBe('Choose a size range.')
    expect(validateLine(line({ colorId: null }))).toBe('Choose a color.')
  })

  it('requires a positive quantity', () => {
    expect(validateLine(line({ quantity: null }))).toBe('Enter a quantity greater than zero.')
    expect(validateLine(line({ quantity: 0 }))).toBe('Enter a quantity greater than zero.')
  })

  it('requires a typed unit price, so a blank price is not a valid zero', () => {
    expect(validateLine(line({ unitPrice: null }))).toBe('Enter the unit price.')
  })
})

describe('lineErrors', () => {
  it('returns no errors when every line fits the stock', () => {
    expect(lineErrors([line()], stockFor(5)).size).toBe(0)
  })

  it('flags a line that exceeds stock with the server message', () => {
    const errors = lineErrors([line({ quantity: 6 })], stockFor(5))
    expect(errors.get(1)).toBe('Insufficient stock for Shirt (S, Red): requested 6.00, available 5.00.')
  })

  it('adds duplicate lines of the same variant before comparing with stock', () => {
    const lines = [line({ key: 1, quantity: 3 }), line({ key: 2, quantity: 3 })]
    const errors = lineErrors(lines, stockFor(5))
    expect(errors.get(1)).toContain('requested 6.00')
    expect(errors.get(2)).toContain('requested 6.00')
  })

  it('does not count incomplete lines toward stock', () => {
    const lines = [line({ key: 1, quantity: 3 }), line({ key: 2, colorId: null, quantity: 9 })]
    const errors = lineErrors(lines, stockFor(5))
    expect(errors.has(1)).toBe(false)
    expect(errors.get(2)).toBe('Choose a color.')
  })

  it('refuses a variant that has no stock record', () => {
    const errors = lineErrors([line()], stockFor(null))
    expect(errors.get(1)).toBe('No stock recorded for Shirt (S, Red).')
  })
})
