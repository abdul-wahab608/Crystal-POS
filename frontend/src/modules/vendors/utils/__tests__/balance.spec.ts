import { describe, it, expect } from 'vitest'
import { vendorBalanceLabel } from '../balance'

describe('vendorBalanceLabel', () => {
  it('shows a positive balance as the amount we owe', () => {
    expect(vendorBalanceLabel('499.00')).toBe('499.00')
  })

  it('labels a negative balance as the vendor owing us', () => {
    expect(vendorBalanceLabel('-50')).toBe('Vendor owes you 50.00')
  })

  it('shows zero plainly', () => {
    expect(vendorBalanceLabel('0.00')).toBe('0.00')
  })
})
