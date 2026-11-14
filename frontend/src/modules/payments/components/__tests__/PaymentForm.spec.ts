import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PaymentForm from '../PaymentForm.vue'
import { useAuthStore } from '../../../../shared/stores/auth'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))

vi.mock('../../../../shared/api/axios', () => ({
  default: { get, post: vi.fn(), delete: vi.fn(), patch: vi.fn(), put: vi.fn() },
}))

const purchases = [
  { id: 25, vendor: 1, date: '2026-11-14T10:00:00Z', invoice_number: 'UI-INV-1', total_amount: '500.00', unpaid_amount: '500.00', payment_status: 'UNPAID' },
]

describe('PaymentForm bill selector for outgoing vendor payments', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const auth = useAuthStore()
    auth.user = { id: 1, username: 'admin', role: 'ADMIN', is_superuser: true } as never
    get.mockReset()
    get.mockImplementation(async (url: string) => {
      if (url === '/customers/') return { data: [] }
      if (url === '/vendors/') return { data: [{ id: 1, name: 'Fabric House', is_active: true }] }
      if (url === '/bank-accounts/') return { data: [] }
      if (url === '/purchases/') return { data: purchases }
      return { data: [] }
    })
  })

  it('shows the open bills after choosing a vendor for money out', async () => {
    const wrapper = mount(PaymentForm)
    await flushPromises()
    await wrapper.find('#pay-direction').setValue('OUTGOING')
    await wrapper.find('#pay-direction').trigger('change')
    await flushPromises()
    const party = wrapper.find('#pay-party')
    await party.trigger('focus')
    await wrapper.findAll('li[role="option"]')[0]?.trigger('mousedown')
    await flushPromises()
    expect(wrapper.find('#pay-bill').exists()).toBe(true)
    await wrapper.find('#pay-bill').trigger('focus')
    await flushPromises()
    const labels = wrapper.findAll('li[role="option"]').map(li => li.text())
    expect(labels.some(label => label.includes('Purchase #25'))).toBe(true)
  })
})
