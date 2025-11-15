export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
  date_joined: string
  last_login: string | null
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
}

export interface UpdateUserRequest {
  username?: string
  email?: string
  password?: string
  first_name?: string
  last_name?: string
  role?: string
  is_active?: boolean
}

export interface UserStats {
  total: number
  active: number
  inactive: number
} 