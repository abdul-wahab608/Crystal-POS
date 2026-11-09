export type UserRole = 'ADMIN' | 'MANAGER' | 'CASHIER' | 'STAFF'

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  phone: string | null
  is_active: boolean
  last_login: string | null
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  first_name: string
  last_name: string
  role: UserRole
  is_active: boolean
}

export interface UpdateUserRequest {
  username?: string
  email?: string
  password?: string
  first_name?: string
  last_name?: string
  role?: UserRole
  is_active?: boolean
}
