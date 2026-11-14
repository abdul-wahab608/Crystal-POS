import { describe, it, expect } from 'vitest'
import { errorMessageOf } from '../errorMessage'

const fail = (data: unknown) => ({ response: { data } })

describe('errorMessageOf', () => {
  it('shows a non-field error without a field prefix', () => {
    expect(errorMessageOf(fail({ non_field_errors: ['This product already has a cost.'] })))
      .toBe('This product already has a cost.')
  })

  it('shows detail and error messages as they are', () => {
    expect(errorMessageOf(fail({ detail: 'Not allowed.' }))).toBe('Not allowed.')
    expect(errorMessageOf(fail({ error: 'Cannot delete.' }))).toBe('Cannot delete.')
  })

  it('prefixes field errors with the field name', () => {
    expect(errorMessageOf(fail({ amount: ['Too large.'] }))).toBe('amount: Too large.')
  })

  it('falls back to the error message when there is no response', () => {
    expect(errorMessageOf(new Error('Network down'))).toBe('Network down')
  })
})
