import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import ProductTable from '../ProductTable.vue'
import type { Product } from '../../types'

vi.mock('../../../../shared/utils/export', () => ({
  exportToCSV: vi.fn(),
  exportToJSON: vi.fn(),
}))

const mockProducts: Product[] = [
  {
    id: 1,
    name: 'Test Product 1',
    unit: 'BAG',
    cop: 10.99,
    quantity: 100,
    size_range: null,
    variants: [],
    created_at: '2023-01-01T00:00:00Z',
    last_updated: '2023-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Test Product 2',
    unit: 'KILO',
    cop: 25.5,
    quantity: 50,
    size_range: null,
    variants: [],
    created_at: '2023-01-02T00:00:00Z',
    last_updated: '2023-01-02T00:00:00Z',
  },
]

describe('ProductTable', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders products correctly', () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: mockProducts,
        loading: false,
        error: null,
      },
    })

    expect(wrapper.find('table').exists()).toBe(true)
    const rows = wrapper.findAll('tbody tr')
    expect(rows).toHaveLength(2)
    expect(wrapper.text()).toContain('Test Product 1')
    expect(wrapper.text()).toContain('Test Product 2')
  })

  it('shows loading state', () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: [],
        loading: true,
        error: null,
      },
    })

    expect(wrapper.text()).toContain('Loading')
  })

  it('shows empty state when no products', () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: [],
        loading: false,
        error: null,
      },
    })

    expect(wrapper.text()).toContain('No products')
  })

  it('emits view, edit, delete events from action buttons', async () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: mockProducts,
        loading: false,
        error: null,
      },
    })

    const actionButtons = wrapper.findAll('tbody tr:first-child td:last-child button')
    expect(actionButtons.length).toBe(3)

    await actionButtons[0].trigger('click')
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')![0]).toEqual([mockProducts[0]])

    await actionButtons[1].trigger('click')
    expect(wrapper.emitted('view')).toBeTruthy()
    expect(wrapper.emitted('view')![0]).toEqual([mockProducts[0]])
  })

  it('shows error state', () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: [],
        loading: false,
        error: 'Failed to load',
      },
    })

    expect(wrapper.text()).toContain('Failed to load')
    const retryBtn = wrapper.findAll('button').find((b) => b.text().includes('Try Again'))
    expect(retryBtn).toBeTruthy()
  })

  it('emits retry from error state', async () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: [],
        loading: false,
        error: 'Network error',
      },
    })

    const retryBtn = wrapper.findAll('button').find((b) => b.text().includes('Try Again'))
    await retryBtn!.trigger('click')
    expect(wrapper.emitted('retry')).toBeTruthy()
  })

  it('emits add from empty state', async () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: [],
        loading: false,
        error: null,
      },
    })

    const addBtn = wrapper.findAll('button').find((b) => b.text().includes('Add Product'))
    expect(addBtn).toBeTruthy()
    await addBtn!.trigger('click')
    expect(wrapper.emitted('add')).toBeTruthy()
  })

  it('sorts products by name', async () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: mockProducts,
        loading: false,
        error: null,
      },
    })

    const nameHeader = wrapper.find('thead th')
    await nameHeader.trigger('click')

    const rows = wrapper.findAll('tbody tr')
    expect(rows[0].text()).toContain('Test Product 2')
  })

  it('displays cop and stock value formatted', () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: [mockProducts[0]],
        loading: false,
        error: null,
      },
    })

    expect(wrapper.text()).toContain('10.99')
    expect(wrapper.text()).toContain('1099.00')
  })

  it('shows low stock badge when quantity < 10', () => {
    const lowStockProduct: Product = {
      ...mockProducts[0],
      quantity: 5,
    }

    const wrapper = mount(ProductTable, {
      props: {
        products: [lowStockProduct],
        loading: false,
        error: null,
      },
    })

    expect(wrapper.text()).toContain('Low Stock')
  })
})
