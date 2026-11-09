const PAYMENT_STATUS_LABELS: Record<string, string> = {
  PAID: 'Paid',
  PARTIAL: 'Part paid',
  UNPAID: 'Unpaid',
}

export function paymentStatusLabel(status: string): string {
  return PAYMENT_STATUS_LABELS[status] ?? status
}

export function customerBalanceLabel(balance: number | string): string {
  const value = Number(balance)
  if (value < 0) return `Credit: ${Math.abs(value).toFixed(2)}`
  if (value > 0) return `Owes: ${value.toFixed(2)}`
  return 'Settled: 0.00'
}
