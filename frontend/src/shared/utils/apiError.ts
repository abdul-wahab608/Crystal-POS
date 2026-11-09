const describe = (value: unknown): string => {
  if (Array.isArray(value)) return value.map(describe).join(' ')
  if (value && typeof value === 'object') return Object.values(value).map(describe).join(' ')
  return String(value)
}

export const apiErrorMessage = (e: any): string => {
  const data = e?.response?.data
  if (!data) return e?.message || 'Request failed.'
  if (typeof data === 'string') return data
  if (data.detail) return describe(data.detail)
  return Object.entries(data)
    .map(([field, value]) => (field === 'non_field_errors' ? describe(value) : `${field}: ${describe(value)}`))
    .join(' ')
}
