export interface Asset {
  id: number
  name: string
  description: string | null
  category: string | null
  type: string
  current_value: string | null
  purchase_value: string | null
  purchase_date: string | null
  location: string | null
  status: string
  created_at: string
}

export interface CreateAssetRequest {
  name: string
  description: string
  category: string
  type: string
  current_value: number
  purchase_value: number
  purchase_date: string
  location: string
  status: string
}

export interface UpdateAssetRequest extends Partial<CreateAssetRequest> {}
