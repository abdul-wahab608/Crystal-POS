import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../../../shared/api/axios'
import type { BankAccount, CreateBankAccount, UpdateBankAccount } from '../types'

export const useBankAccountsStore = defineStore('bankAccounts', () => {
  const bankAccounts = ref<BankAccount[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const activeAccounts = computed(() => {
    return bankAccounts.value.filter(account => account.is_active)
  })

  const inactiveAccounts = computed(() => {
    return bankAccounts.value.filter(account => !account.is_active)
  })

  async function fetchBankAccounts() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/bank-accounts/')
      bankAccounts.value = Array.isArray(response.data) ? response.data : []
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch bank accounts'
      console.error('Error fetching bank accounts:', err)
    } finally {
      loading.value = false
    }
  }

  async function createBankAccount(data: CreateBankAccount) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/bank-accounts/', data)
      bankAccounts.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create bank account'
      console.error('Error creating bank account:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateBankAccount(id: number, data: UpdateBankAccount) {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/bank-accounts/${id}/`, data)
      const index = bankAccounts.value.findIndex(account => account.id === id)
      if (index !== -1) {
        bankAccounts.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update bank account'
      console.error('Error updating bank account:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteBankAccount(id: number) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/bank-accounts/${id}/`)
      const index = bankAccounts.value.findIndex(account => account.id === id)
      if (index !== -1) {
        bankAccounts.value.splice(index, 1)
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete bank account'
      console.error('Error deleting bank account:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function toggleAccountStatus(id: number) {
    const account = bankAccounts.value.find(acc => acc.id === id)
    if (account) {
      try {
        await updateBankAccount(id, { is_active: !account.is_active })
      } catch (err) {
        console.error('Error toggling account status:', err)
      }
    }
  }

  return {
    bankAccounts,
    loading,
    error,
    activeAccounts,
    inactiveAccounts,
    fetchBankAccounts,
    createBankAccount,
    updateBankAccount,
    deleteBankAccount,
    toggleAccountStatus
  }
})