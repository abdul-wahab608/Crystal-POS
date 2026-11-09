const messagesOf = (value: unknown): string[] => {
  if (typeof value === 'string') return [value]
  if (Array.isArray(value)) return value.flatMap(messagesOf)
  if (value && typeof value === 'object') {
    return Object.entries(value).flatMap(([field, inner]) =>
      messagesOf(inner).map(message => (field === 'detail' || field === 'non_field_errors' || field === 'error' ? message : `${field}: ${message}`)),
    )
  }
  return []
}

export function errorMessageOf(error: any): string {
  const messages = messagesOf(error?.response?.data)
  if (messages.length) return messages.join('; ')
  return error?.message || 'Request failed.'
}
