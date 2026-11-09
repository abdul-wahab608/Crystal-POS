import { computed, ref } from 'vue'
import { usePurchasesStore } from '../../purchases/stores/purchases'
import type { Purchase } from '../../purchases/types'
import { formatMoney } from '../../../shared/utils/perUnit'

export function useVendorBill() {
  const purchasesStore = usePurchasesStore()
  const bills = ref<Purchase[]>([])
  const billId = ref<number | null>(null)

  const options = computed(() => bills.value.map(bill => ({
    value: bill.id,
    label: `Purchase #${bill.id} · ${new Date(bill.date).toLocaleDateString()} · unpaid ${formatMoney(bill.unpaid_amount)}`,
  })))

  const selectedBill = computed(() => bills.value.find(bill => bill.id === billId.value) ?? null)

  async function loadBills(vendorId: number | null) {
    billId.value = null
    bills.value = vendorId === null ? [] : await purchasesStore.fetchOpenBills(vendorId)
  }

  function billError(amount: number | null): string {
    const bill = selectedBill.value
    if (!bill || amount === null) return ''
    const unpaid = Number(bill.unpaid_amount)
    return amount > unpaid ? `Amount exceeds the unpaid balance of ${formatMoney(unpaid)} on Purchase #${bill.id}.` : ''
  }

  return { billId, options, selectedBill, loadBills, billError }
}
