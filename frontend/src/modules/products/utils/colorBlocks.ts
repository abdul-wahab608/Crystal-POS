import type { ProductVariant, VariantInput } from '../types'

export type Quantity = number | string

export interface ColorBlock {
  key: number
  colorId: number | null
  quantities: Record<number, Quantity>
}

export function blocksFromVariants(variants: ProductVariant[], nextKey: () => number): ColorBlock[] {
  const blocks: ColorBlock[] = []
  for (const variant of variants) {
    let block = blocks.find(b => b.colorId === variant.color)
    if (!block) {
      block = { key: nextKey(), colorId: variant.color, quantities: {} }
      blocks.push(block)
    }
    block.quantities[variant.size_range] = variant.quantity
  }
  return blocks
}

export function blockTotal(block: ColorBlock, sizeRangeIds: number[]): number {
  return sizeRangeIds.reduce((sum, id) => sum + (Number(block.quantities[id]) || 0), 0)
}

export function grandTotal(blocks: ColorBlock[], sizeRangeIds: number[]): number {
  return blocks.reduce((sum, block) => sum + blockTotal(block, sizeRangeIds), 0)
}

export function copyBlockQuantities(source: ColorBlock, target: ColorBlock, sizeRangeIds: number[]): ColorBlock {
  const quantities: Record<number, Quantity> = {}
  for (const id of sizeRangeIds) {
    quantities[id] = source.quantities[id] ?? ''
  }
  return { ...target, quantities }
}

export function dropSizeRange(blocks: ColorBlock[], sizeRangeId: number): ColorBlock[] {
  return blocks.map(block => {
    const { [sizeRangeId]: _removed, ...quantities } = block.quantities
    return { ...block, quantities }
  })
}

export function takenColorIds(blocks: ColorBlock[], exceptKey: number): number[] {
  return blocks
    .filter(b => b.key !== exceptKey && b.colorId !== null)
    .map(b => b.colorId as number)
}

export function blockProblem(blocks: ColorBlock[]): string | null {
  if (blocks.some(b => b.colorId === null)) return 'Pick a color for every color block.'
  const ids = blocks.map(b => b.colorId)
  if (new Set(ids).size !== ids.length) return 'Each color can appear only once.'
  return null
}

export function toVariantInputs(blocks: ColorBlock[], sizeRangeIds: number[]): VariantInput[] {
  const inputs: VariantInput[] = []
  for (const block of blocks) {
    if (block.colorId === null) continue
    for (const id of sizeRangeIds) {
      inputs.push({ size_range: id, color: block.colorId, quantity: Number(block.quantities[id]) || 0 })
    }
  }
  return inputs
}
