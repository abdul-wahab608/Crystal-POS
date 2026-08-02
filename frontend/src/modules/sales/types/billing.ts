export interface Payment {
  id: number;
  amount: number;
  date: string;
  method: 'CASH' | 'CHEQUE' | 'BANK_TRANSFER';
  reference?: string;
  invoice?: number;
  bill?: number;
}

export interface Invoice {
  id: number;
  number: string;
  date: string;
  amount: number;
  payment_status: 'PAID' | 'PARTIAL' | 'UNPAID';
  payment_method: 'CASH' | 'CHEQUE' | 'BANK_TRANSFER';
  sale: number;
  payments: Payment[];
}

export interface Bill {
  id: number;
  number: string;
  date: string;
  amount: number;
  payment_status: 'PAID' | 'PARTIAL' | 'UNPAID';
  payment_method: 'CASH' | 'CHEQUE' | 'BANK_TRANSFER';
  purchase: number;
  payments: Payment[];
}
