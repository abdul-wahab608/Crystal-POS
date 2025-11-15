import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProductsStore } from '../products'
import api from '../../../../shared/api/axios'

// Mock the API
vi.mock('../../../../shared/api/axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

describe('Products Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetches products successfully', async () => {
    const mockProducts = [
      { id: 1, name: 'Product 1', unit: 'BAG', unit_price: 10, quantity: 5, available_stock: 5, created_at: '2023-01-01', last_updated: '2023-01-01' }
    ]
    
    vi.mocked(api.get).mockResolvedValue({ data: mockProducts })
    
    const store = useProductsStore()
    await store.fetchProducts()
    
    expect(store.products).toEqual(mockProducts)
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
  })

  it('handles fetch error', async () => {
    const errorMessage = 'Failed to fetch products'
    vi.mocked(api.get).mockRejectedValue({ response: { data: { message: errorMessage } } })
    
    const store = useProductsStore()
    await store.fetchProducts()
    
    expect(store.error).toBe(errorMessage)
    expect(store.loading).toBe(false)
  })

  it('creates product successfully', async () => {
    const newProduct = { name: 'New Product', unit: 'BAG' as const, cop: 15, quantity: 10 }
    const createdProduct = { id: 2, ...newProduct, available_stock: 10, created_at: '2023-01-01', last_updated: '2023-01-01' }
    
    const store = useProductsStore()
    store.products = [{ id: 1, name: 'Existing', unit: 'BAG', cop: 10, quantity: 5, available_stock: 5, created_at: '2023-01-01', last_updated: '2023-01-01' }]
    
    vi.mocked(api.post).mockResolvedValue({ data: createdProduct })
    
    await store.createProduct(newProduct)
    
    expect(store.products).toHaveLength(2)
    expect(store.products[1]).toEqual(createdProduct)
  })

  it('updates product successfully', async () => {
    const updatedProduct = { id: 1, name: 'Updated', unit: 'BAG', cop: 20, quantity: 10, available_stock: 10, created_at: '2023-01-01', last_updated: '2023-01-01' }
    
    const store = useProductsStore()
    store.products = [{ id: 1, name: 'Original', unit: 'BAG', cop: 10, quantity: 5, available_stock: 5, created_at: '2023-01-01', last_updated: '2023-01-01' }]
    
    vi.mocked(api.patch).mockResolvedValue({ data: updatedProduct })
    
    await store.updateProduct(1, { name: 'Updated', cop: 20 })
    
    expect(store.products[0]).toEqual(updatedProduct)
  })

  it('deletes product successfully', async () => {
    const store = useProductsStore()
    store.products = [
      { id: 1, name: 'Product 1', unit: 'BAG', cop: 10, quantity: 5, available_stock: 5, created_at: '2023-01-01', last_updated: '2023-01-01' },
      { id: 2, name: 'Product 2', unit: 'KILO', cop: 20, quantity: 10, available_stock: 10, created_at: '2023-01-01', last_updated: '2023-01-01' }
    ]
    
    vi.mocked(api.delete).mockResolvedValue({})
    
    await store.deleteProduct(1)
    
    expect(store.products).toHaveLength(1)
    expect(store.products[0].id).toBe(2)
  })
}) 