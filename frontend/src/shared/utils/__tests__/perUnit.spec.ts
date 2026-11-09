import { describe, it, expect } from 'vitest'
import { groupByUnit, formatQuantityLines, sumField } from '../perUnit'

describe('groupByUnit', () => {
  it('groups rows by unit without adding quantities across units', () => {
    const rows = [
      { unit: 'PCS', name: 'Sock', quantity: 10 },
      { unit: 'DOZEN', name: 'Box', quantity: 3 },
      { unit: 'PCS', name: 'Glove', quantity: 4 },
    ]
    const groups = groupByUnit(rows)
    expect(groups.map((g) => g.unit)).toEqual(['DOZEN', 'PCS'])
    expect(groups[1].rows.map((r) => r.name)).toEqual(['Sock', 'Glove'])
    expect(sumField(groups[1].rows, 'quantity')).toBe(14)
    expect(sumField(groups[0].rows, 'quantity')).toBe(3)
  })

  it('returns no groups for no rows', () => {
    expect(groupByUnit([])).toEqual([])
  })
})

describe('formatQuantityLines', () => {
  it('renders one line per unit with the unit label', () => {
    expect(formatQuantityLines([
      { unit: 'PCS', quantity: '15.00' },
      { unit: 'DOZEN', quantity: 2 },
    ])).toEqual(['2 DOZEN', '15 PCS'])
  })
})
