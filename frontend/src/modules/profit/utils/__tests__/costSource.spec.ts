import { describe, it, expect } from 'vitest'
import { costSourceLabel, COST_MISSING_MESSAGE } from '../costSource'

describe('costSourceLabel', () => {
  it('labels each cost source', () => {
    expect(costSourceLabel('MANUAL')).toBe('Manual cost')
    expect(costSourceLabel('PRODUCTION')).toBe('From production')
    expect(costSourceLabel('COP')).toBe('Cost of production (fallback)')
    expect(costSourceLabel('MISSING')).toBe('Cost missing')
  })

  it('shows a dash when there is no source', () => {
    expect(costSourceLabel(null)).toBe('—')
    expect(costSourceLabel(undefined)).toBe('—')
  })

  it('exposes the message shown in place of a margin', () => {
    expect(COST_MISSING_MESSAGE).toBe('Cost missing: add production or a manual cost')
  })
})
