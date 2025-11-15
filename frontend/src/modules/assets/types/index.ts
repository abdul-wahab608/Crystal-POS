export interface Asset {
  id: number
  name: string
  description: string
  category: string
  type: string
  value: number
  current_value: number
  purchase_value: number
  purchase_date: string
  location: string
  status: string
  created_at: string
}

export interface CreateAssetRequest {
  name: string
  description: string
  category: string
  type: string
  value: number
  current_value: number
  purchase_value: number
  purchase_date: string
  location: string
  status: string
}

export interface UpdateAssetRequest {
  name?: string
  description?: string
  category?: string
  type?: string
  value?: number
  current_value?: number
  purchase_value?: number
  purchase_date?: string
  location?: string
  status?: string
} 