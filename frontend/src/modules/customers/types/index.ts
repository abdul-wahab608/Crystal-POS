export interface Customer {
  id: number
  name: string
  email: string
  phone: string
  address: string
  balance: number
  is_active: boolean
  created_at: string
}

export interface CreateCustomerRequest {
  name: string
  email: string
  phone: string
  address: string
  is_active: boolean
}

export interface UpdateCustomerRequest {
  name?: string
  email?: string
  phone?: string
  address?: string
  is_active?: boolean
} 