export interface BankAccount {
  id: number
  name: string
  account_number: string
  bank_name: string
  branch?: string
  ifsc_code?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateBankAccount {
  name: string
  account_number: string
  bank_name: string
  branch?: string
  ifsc_code?: string
  is_active?: boolean
}

export interface UpdateBankAccount extends Partial<CreateBankAccount> {
  id?: number
} 