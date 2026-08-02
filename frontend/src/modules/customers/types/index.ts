export interface Customer {
  id: number
  name: string
  phone: string
  address: string
  city?: string
  customer_type: 'REGULAR' | 'WALK_IN'
  balance: number
  is_active: boolean
  created_at: string
}

export interface CreateCustomerRequest {
  name: string
  phone: string
  address: string
  city?: string
  customer_type?: 'REGULAR' | 'WALK_IN'
  is_active: boolean
}

export interface UpdateCustomerRequest {
  name?: string
  phone?: string
  address?: string
  city?: string
  customer_type?: 'REGULAR' | 'WALK_IN'
  is_active?: boolean
}
