import type { Product, ProductVariantLine } from '../types'

export interface OutputDraft {
  product: number | null
  size_range: number | null
  color: number | null
  quantity: number | null
}

export function sizeOptionsFor(product: Product | undefined): { value: number; label: string }[] {
  if (!product) return []
  const seen = new Map<number, string>()
  product.variants.forEach(variant => seen.set(variant.size_range, variant.size_range_name))
  return [...seen].map(([value, label]) => ({ value, label }))
}

export function colorOptionsFor(product: Product | undefined, sizeRange: number | null): { value: number; label: string }[] {
  if (!product || sizeRange === null) return []
  const seen = new Map<number, string>()
  product.variants
    .filter(variant => variant.size_range === sizeRange)
    .forEach(variant => seen.set(variant.color, variant.color_name))
  return [...seen].map(([value, label]) => ({ value, label }))
}

export function resolveVariant(product: Product | undefined, draft: OutputDraft): ProductVariantLine | undefined {
  if (!product || draft.size_range === null || draft.color === null) return undefined
  return product.variants.find(variant => variant.size_range === draft.size_range && variant.color === draft.color)
}

export function outputProblems(draft: OutputDraft, product: Product | undefined): string[] {
  const problems: string[] = []
  if (draft.product === null) problems.push('Choose a product.')
  if (draft.size_range === null) problems.push('Choose a size range.')
  if (draft.color === null) problems.push('Choose a color.')
  if (draft.product !== null && draft.size_range !== null && draft.color !== null && !resolveVariant(product, draft)) {
    problems.push('That size and color does not exist for this product. Add it on the Products page first.')
  }
  if (!(Number(draft.quantity) > 0)) problems.push('Quantity must be greater than zero.')
  return problems
}
