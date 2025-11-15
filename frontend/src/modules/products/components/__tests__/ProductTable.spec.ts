import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach } from 'vitest'
import ProductTable from '../ProductTable.vue'
import type { Product } from '../../types'

const mockProducts: Product[] = [
  {
    id: 1,
    name: 'Test Product 1',
    unit: 'BAG',
    cop: 10.99,
    quantity: 100,
    available_stock: 95,
    created_at: '2023-01-01T00:00:00Z',
    last_updated: '2023-01-01T00:00:00Z'
  },
  {
    id: 2,
    name: 'Test Product 2',
    unit: 'KILO',
    cop: 25.50,
    quantity: 50,
    available_stock: 45,
    created_at: '2023-01-02T00:00:00Z',
    last_updated: '2023-01-02T00:00:00Z'
  }
]

describe('ProductTable', () => {
  it('renders products correctly', () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: mockProducts,
        loading: false,
        error: null,
        onView: () => {},
        onRetry: () => {},
        onAdd: () => {},
        onEdit: () => {},
        onDelete: () => {}
      }
    })

    expect(wrapper.find('table').exists()).toBe(true)
    expect(wrapper.findAll('tr')).toHaveLength(3) // Header + 2 products
  })

  it('shows loading state', () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: [],
        loading: true,
        error: null,
        onView: () => {},
        onRetry: () => {},
        onAdd: () => {},
        onEdit: () => {},
        onDelete: () => {}
      }
    })

    expect(wrapper.text()).toContain('Loading')
  })

  it('shows empty state when no products', () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: [],
        loading: false,
        error: null,
        onView: () => {},
        onRetry: () => {},
        onAdd: () => {},
        onEdit: () => {},
        onDelete: () => {}
      }
    })

    expect(wrapper.text()).toContain('No products found')
  })

  it('emits events when buttons are clicked', async () => {
    const wrapper = mount(ProductTable, {
      props: {
        products: mockProducts,
        loading: false,
        error: null,
        onView: () => {},
        onRetry: () => {},
        onAdd: () => {},
        onEdit: () => {},
        onDelete: () => {}
      }
    })

    // Test view button
    await wrapper.find('.view-btn').trigger('click')
    expect(wrapper.emitted('view')).toBeTruthy()

    // Test edit button
    await wrapper.find('.edit-btn').trigger('click')
    expect(wrapper.emitted('edit')).toBeTruthy()

    // Test delete button
    await wrapper.find('.delete-btn').trigger('click')
    expect(wrapper.emitted('delete')).toBeTruthy()
  })
}) 