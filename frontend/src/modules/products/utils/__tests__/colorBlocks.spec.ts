import { describe, it, expect } from 'vitest'
import {
  blocksFromVariants,
  blockProblem,
  blockTotal,
  copyBlockQuantities,
  dropSizeRange,
  grandTotal,
  toVariantInputs,
  type ColorBlock,
} from '../colorBlocks'

const sequence = () => {
  let key = 0
  return () => ++key
}

describe('copyBlockQuantities', () => {
  it('copies quantities for the selected size ranges and keeps the target color', () => {
    const source: ColorBlock = { key: 1, colorId: 10, quantities: { 1: 4, 2: 6, 3: 9 } }
    const target: ColorBlock = { key: 2, colorId: 20, quantities: { 1: 0, 2: 0 } }

    const copied = copyBlockQuantities(source, target, [1, 2])

    expect(copied.colorId).toBe(20)
    expect(copied.key).toBe(2)
    expect(copied.quantities).toEqual({ 1: 4, 2: 6 })
  })

  it('does not mutate the source or the target block', () => {
    const source: ColorBlock = { key: 1, colorId: 10, quantities: { 1: 4 } }
    const target: ColorBlock = { key: 2, colorId: 20, quantities: { 1: 0 } }

    copyBlockQuantities(source, target, [1])
    copyBlockQuantities(source, target, [1])

    expect(source.quantities).toEqual({ 1: 4 })
    expect(target.quantities).toEqual({ 1: 0 })
  })

  it('leaves a blank quantity for a size range the source never had', () => {
    const source: ColorBlock = { key: 1, colorId: 10, quantities: { 1: 4 } }
    const target: ColorBlock = { key: 2, colorId: null, quantities: {} }

    expect(copyBlockQuantities(source, target, [1, 2]).quantities).toEqual({ 1: 4, 2: '' })
  })
})

describe('blocksFromVariants', () => {
  it('groups variants into one block per color', () => {
    const blocks = blocksFromVariants([
      { id: 1, size_range: 1, size_range_name: 'Men', color: 10, color_name: 'Black', quantity: 4 },
      { id: 2, size_range: 2, size_range_name: 'Women', color: 10, color_name: 'Black', quantity: '2.5' },
      { id: 3, size_range: 1, size_range_name: 'Men', color: 20, color_name: 'Brown', quantity: 7 },
    ], sequence())

    expect(blocks.map(b => b.colorId)).toEqual([10, 20])
    expect(blocks[0].quantities).toEqual({ 1: 4, 2: '2.5' })
    expect(blocks[1].quantities).toEqual({ 1: 7 })
  })
})

describe('totals and payload', () => {
  const blocks: ColorBlock[] = [
    { key: 1, colorId: 10, quantities: { 1: 4, 2: '2.5' } },
    { key: 2, colorId: 20, quantities: { 1: 3, 2: '' } },
  ]

  it('sums only the selected size ranges', () => {
    expect(blockTotal(blocks[0], [1, 2])).toBe(6.5)
    expect(blockTotal(blocks[0], [1])).toBe(4)
    expect(grandTotal(blocks, [1, 2])).toBe(9.5)
  })

  it('builds one variant per color and selected size range, skipping blocks without a color', () => {
    const withBlank: ColorBlock[] = [...blocks, { key: 3, colorId: null, quantities: { 1: 99 } }]

    expect(toVariantInputs(withBlank, [1, 2])).toEqual([
      { size_range: 1, color: 10, quantity: 4 },
      { size_range: 2, color: 10, quantity: 2.5 },
      { size_range: 1, color: 20, quantity: 3 },
      { size_range: 2, color: 20, quantity: 0 },
    ])
  })

  it('drops a removed size range from every block', () => {
    const dropped = dropSizeRange(blocks, 2)
    expect(dropped[0].quantities).toEqual({ 1: 4 })
    expect(dropped[1].quantities).toEqual({ 1: 3 })
  })

  it('reports a missing color or a duplicate color', () => {
    expect(blockProblem([{ key: 1, colorId: null, quantities: {} }])).toMatch(/Pick a color/)
    expect(blockProblem([
      { key: 1, colorId: 10, quantities: {} },
      { key: 2, colorId: 10, quantities: {} },
    ])).toMatch(/only once/)
    expect(blockProblem(blocks)).toBeNull()
  })
})
