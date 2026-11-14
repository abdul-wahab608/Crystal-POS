export function vendorBalanceLabel(balance: string | number): string {
  const value = Number(balance)
  if (value < 0) return `Vendor owes you ${(-value).toFixed(2)}`
  return value.toFixed(2)
}
