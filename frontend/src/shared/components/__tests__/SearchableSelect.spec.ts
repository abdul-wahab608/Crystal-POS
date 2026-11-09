import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchableSelect from '../SearchableSelect.vue'

const options = [
  { value: 1, label: 'Black' },
  { value: 2, label: 'Brown' },
  { value: 3, label: 'Navy' },
]

describe('SearchableSelect', () => {
  it('shows the label of the selected option', () => {
    const wrapper = mount(SearchableSelect, { props: { modelValue: 2, options } })
    expect((wrapper.find('input').element as HTMLInputElement).value).toBe('Brown')
  })

  it('filters options by typed text, case-insensitively', async () => {
    const wrapper = mount(SearchableSelect, { props: { modelValue: null, options }, attachTo: document.body })
    const input = wrapper.find('input')
    await input.trigger('focus')
    await input.setValue('BR')
    const labels = wrapper.findAll('li[role="option"]').map(li => li.text())
    expect(labels).toEqual(['Brown'])
    wrapper.unmount()
  })

  it('emits update:modelValue when an option is picked', async () => {
    const wrapper = mount(SearchableSelect, { props: { modelValue: null, options }, attachTo: document.body })
    const input = wrapper.find('input')
    await input.trigger('focus')
    await wrapper.findAll('li[role="option"]')[2].trigger('mousedown')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([3])
    wrapper.unmount()
  })

  it('shows an empty-state row when nothing matches', async () => {
    const wrapper = mount(SearchableSelect, { props: { modelValue: null, options }, attachTo: document.body })
    const input = wrapper.find('input')
    await input.trigger('focus')
    await input.setValue('zzz')
    expect(wrapper.find('.searchable-select-empty').text()).toBe('No matches')
    wrapper.unmount()
  })
})
