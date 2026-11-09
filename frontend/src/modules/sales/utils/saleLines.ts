export interface SaleLineDraft {
  key: number
  productId: number | null
  sizeRangeId: number | null
  colorId: number | null
  quantity: number | null
  unitPrice: number | null
}

export interface LineStock {
  label: string
  available: number | null
}

export const roundMoney = (value: number): number => Math.round(value * 100) / 100

export const lineTotal = (line: SaleLineDraft): number => {
  const quantity = Number(line.quantity) || 0
  const unitPrice = Number(line.unitPrice) || 0
  return roundMoney(quantity * unitPrice)
}

export const saleTotal = (lines: SaleLineDraft[]): number =>
  roundMoney(lines.reduce((sum, line) => sum + lineTotal(line), 0))

export const validateLine = (line: SaleLineDraft): string | null => {
  if (!line.productId) return 'Choose a product.'
  if (!line.sizeRangeId) return 'Choose a size range.'
  if (!line.colorId) return 'Choose a color.'
  if (!line.quantity || line.quantity <= 0) return 'Enter a quantity greater than zero.'
  if (line.unitPrice === null || Number.isNaN(line.unitPrice) || line.unitPrice < 0) return 'Enter the unit price.'
  return null
}

const variantKey = (line: SaleLineDraft): string => `${line.productId}:${line.sizeRangeId}:${line.colorId}`

const formatQuantity = (value: number): string => value.toFixed(2)

export const lineErrors = (
  lines: SaleLineDraft[],
  stockOf: (line: SaleLineDraft) => LineStock,
): Map<number, string> => {
  const errors = new Map<number, string>()
  const groups = new Map<string, { lines: SaleLineDraft[]; requested: number; stock: LineStock }>()

  for (const line of lines) {
    const incomplete = validateLine(line)
    if (incomplete) {
      errors.set(line.key, incomplete)
      continue
    }
    const key = variantKey(line)
    const group = groups.get(key) ?? { lines: [], requested: 0, stock: stockOf(line) }
    group.lines.push(line)
    group.requested += line.quantity as number
    groups.set(key, group)
  }

  for (const group of groups.values()) {
    const { label, available } = group.stock
    let message: string | null = null
    if (available === null) {
      message = `No stock recorded for ${label}.`
    } else if (group.requested > available) {
      message = `Insufficient stock for ${label}: requested ${formatQuantity(group.requested)}, available ${formatQuantity(available)}.`
    }
    if (message) {
      for (const line of group.lines) errors.set(line.key, message)
    }
  }

  return errors
}
