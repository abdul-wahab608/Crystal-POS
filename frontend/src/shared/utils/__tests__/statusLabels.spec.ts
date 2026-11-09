import { describe, expect, it } from 'vitest'
import { customerBalanceLabel, paymentStatusLabel } from '../statusLabels'

describe('paymentStatusLabel', () => {
  it('humanizes the sale payment statuses', () => {
    expect(paymentStatusLabel('PAID')).toBe('Paid')
    expect(paymentStatusLabel('PARTIAL')).toBe('Part paid')
    expect(paymentStatusLabel('UNPAID')).toBe('Unpaid')
  })

  it('passes unknown statuses through', () => {
    expect(paymentStatusLabel('PENDING')).toBe('PENDING')
  })
})

describe('customerBalanceLabel', () => {
  it('shows a negative balance as credit the customer holds', () => {
    expect(customerBalanceLabel('-500')).toBe('Credit: 500.00')
    expect(customerBalanceLabel(-500)).toBe('Credit: 500.00')
  })

  it('shows a positive balance as what the customer owes', () => {
    expect(customerBalanceLabel('3000')).toBe('Owes: 3000.00')
    expect(customerBalanceLabel('0.5')).toBe('Owes: 0.50')
  })

  it('shows zero as settled', () => {
    expect(customerBalanceLabel('0.00')).toBe('Settled: 0.00')
  })
})
