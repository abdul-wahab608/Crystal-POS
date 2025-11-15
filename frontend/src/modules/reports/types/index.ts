export interface Report {
  id: number
  type: string
  data: any
  generated_at: string
  period: string
}

export interface CreateReportRequest {
  type: string
  period: string
}

export interface UpdateReportRequest {
  type?: string
  period?: string
} 