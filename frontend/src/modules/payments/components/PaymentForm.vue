<template>
  <form class="payment-form" @submit.prevent="submit">
    <div class="field-row">
      <div class="field">
        <label for="pay-direction">Direction</label>
        <select id="pay-direction" v-model="direction" class="form-input" @change="onDirectionChange">
          <option value="INCOMING">Money in from customer</option>
          <option v-if="auth.isManager" value="OUTGOING">Money out to vendor</option>
        </select>
      </div>
      <div class="field">
        <label for="pay-party">{{ direction === 'INCOMING' ? 'Customer' : 'Vendor' }}</label>
        <SearchableSelect
          id="pay-party"
          :model-value="partyId"
          :options="partyOptions"
          :placeholder="direction === 'INCOMING' ? 'Search customer' : 'Search vendor'"
          required
          @update:model-value="onPartyChange"
        />
      </div>
    </div>

    <div v-if="direction === 'OUTGOING'" class="field">
      <label for="pay-bill">Pays which purchase bill (optional)</label>
      <SearchableSelect
        id="pay-bill"
        :model-value="billId"
        :options="billOptions"
        :disabled="!partyId"
        placeholder="Not tied to a bill"
        @update:model-value="onBillChange"
      />
      <small v-if="partyId && !billOptions.length" class="muted">This vendor has no bills with a balance.</small>
      <small v-if="selectedBill" class="muted">Unpaid on this bill: {{ formatMoney(Number(selectedBill.unpaid_amount)) }}</small>
    </div>

    <div v-if="direction === 'INCOMING'" class="field">
      <label for="pay-sale">Against a sale (optional)</label>
      <SearchableSelect
        id="pay-sale"
        :model-value="saleId"
        :options="saleOptions"
        :disabled="!partyId"
        placeholder="On account (no sale)"
        @update:model-value="onSaleChange"
      />
      <small v-if="partyId && !saleOptions.length" class="muted">This customer has no unpaid or partly paid sales.</small>
    </div>

    <div class="field-row">
      <div class="field">
        <label for="pay-amount">Amount</label>
        <input
          id="pay-amount"
          type="number"
          min="0.01"
          step="0.01"
          class="form-input"
          :value="amount ?? ''"
          required
          @input="amount = toNumber(($event.target as HTMLInputElement).value)"
        />
        <small v-if="selectedSale" class="muted">Sale balance: {{ formatMoney(Number(selectedSale.balance)) }}</small>
      </div>
      <div class="field">
        <label for="pay-method">Method</label>
        <select id="pay-method" v-model="method" class="form-input">
          <option value="CASH">Cash</option>
          <option value="BANK">Bank transfer</option>
          <option value="CHEQUE">Cheque</option>
          <option value="PARCHI">Parchi (promissory)</option>
        </select>
      </div>
    </div>

    <div class="field-row">
      <div v-if="method === 'BANK'" class="field">
        <label for="pay-bank">Bank account</label>
        <SearchableSelect
          v-if="bankOptions.length"
          id="pay-bank"
          v-model="bankAccountId"
          :options="bankOptions"
          placeholder="Search bank account"
          required
        />
        <p v-else class="form-error">
          No bank account yet. <template v-if="auth.isManager">Add one on the <router-link to="/bank-accounts">Bank Accounts page</router-link>.</template><template v-else>Ask a manager to add one on the Bank Accounts page.</template>
        </p>
      </div>
      <div class="field">
        <label for="pay-date">Payment date</label>
        <input id="pay-date" v-model="paymentDate" type="date" class="form-input" required />
      </div>
    </div>

    <div class="field">
      <label for="pay-reference">Reference</label>
      <input id="pay-reference" v-model="reference" type="text" class="form-input" maxlength="255" placeholder="Cheque no., transfer id" />
    </div>

    <p v-if="validation" class="form-error">{{ validation }}</p>
    <p v-if="submitError" class="form-error">{{ submitError }}</p>

    <div class="actions">
      <button type="button" class="secondary-btn" @click="emit('cancel')">Cancel</button>
      <button type="submit" class="primary-btn" :disabled="!!validation || submitting">
        {{ submitting ? 'Saving...' : 'Record payment' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import { useAuthStore } from '../../../shared/stores/auth'
import { useToastStore } from '../../../shared/stores/toast'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { useCustomersStore } from '../../customers/stores/customers'
import { useSalesStore } from '../../sales/stores/sales'
import { apiErrorMessage } from '../../../shared/utils/apiError'
import { usePaymentsStore } from '../stores/payments'
import type { PaymentDirection, PaymentMethod, PaymentRequest } from '../types'
import type { Sale } from '../../sales/types'
import { useVendorBill } from '../composables/useVendorBill'

const props = withDefaults(defineProps<{ presetCustomerId?: number | null }>(), { presetCustomerId: null })

const emit = defineEmits<{
  saved: []
  cancel: []
}>()

const auth = useAuthStore()
const toast = useToastStore()
const customersStore = useCustomersStore()
const salesStore = useSalesStore()
const paymentsStore = usePaymentsStore()
const { billId, options: billOptions, selectedBill, loadBills, billError } = useVendorBill()

const today = () => {
  const now = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}

const direction = ref<PaymentDirection>('INCOMING')
const partyId = ref<number | null>(props.presetCustomerId)
const saleId = ref<number | null>(null)
const customerSales = ref<Sale[]>([])
const amount = ref<number | null>(null)
const method = ref<PaymentMethod>('CASH')
const bankAccountId = ref<number | null>(null)
const paymentDate = ref(today())
const reference = ref('')
const submitting = ref(false)
const submitError = ref('')

const toNumber = (raw: string): number | null => (raw === '' ? null : Number(raw))

const formatMoney = (value: number) => `₨${value.toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

const partyOptions = computed(() => direction.value === 'INCOMING'
  ? customersStore.customers.filter(c => c.is_active).map(c => ({ value: c.id, label: c.name }))
  : paymentsStore.vendors.map(v => ({ value: v.id, label: v.name })))

const saleOptions = computed(() => customerSales.value
  .filter(s => Number(s.balance) > 0)
  .map(s => ({ value: s.id, label: `${s.bill_no} · balance ${formatMoney(Number(s.balance))}` })))

const bankOptions = computed(() => paymentsStore.bankAccounts.map(b => ({ value: b.id, label: `${b.name} (${b.bank_name})` })))

const selectedSale = computed(() => customerSales.value.find(s => s.id === saleId.value) ?? null)

const validation = computed(() => {
  if (direction.value === 'INCOMING' && partyId.value === null) return 'Choose the customer.'
  if (direction.value === 'OUTGOING' && partyId.value === null) return 'Choose the vendor.'
  if (amount.value === null || amount.value <= 0) return 'Enter an amount greater than zero.'
  if (selectedSale.value && amount.value > Number(selectedSale.value.balance)) {
    return `Amount exceeds the sale balance of ${formatMoney(Number(selectedSale.value.balance))}.`
  }
  const billMessage = billError(amount.value)
  if (billMessage) return billMessage
  if (method.value === 'BANK' && bankAccountId.value === null) return 'Choose the bank account for a bank transfer.'
  if (!paymentDate.value) return 'Choose the payment date.'
  return ''
})

const loadCustomerSales = async (customerId: number | null) => {
  customerSales.value = customerId === null || direction.value !== 'INCOMING'
    ? []
    : await salesStore.fetchCustomerSales(customerId)
}

const onPartyChange = (value: string | number | null) => {
  partyId.value = value === null ? null : Number(value)
  saleId.value = null
  loadCustomerSales(partyId.value)
  if (direction.value === 'OUTGOING') loadBills(partyId.value)
}

const onBillChange = (value: string | number | null) => {
  billId.value = value === null ? null : Number(value)
}

const onSaleChange = (value: string | number | null) => {
  saleId.value = value === null ? null : Number(value)
}

const onDirectionChange = () => {
  partyId.value = null
  saleId.value = null
  customerSales.value = []
  loadBills(null)
}

watch(method, (value) => {
  if (value !== 'BANK') bankAccountId.value = null
})

const submit = async () => {
  if (validation.value) return
  submitting.value = true
  submitError.value = ''

  const payload: PaymentRequest = {
    payment_type: direction.value,
    payment_method: method.value,
    amount: (amount.value as number).toFixed(2),
    payment_date: paymentDate.value,
  }
  if (direction.value === 'INCOMING') {
    payload.customer = partyId.value as number
    if (saleId.value !== null) payload.sale = saleId.value
  } else {
    payload.vendor = partyId.value as number
    if (billId.value !== null) payload.purchase = billId.value
  }
  if (method.value === 'BANK') payload.bank_account = bankAccountId.value as number
  if (reference.value.trim()) payload.reference = reference.value.trim()

  try {
    const saved = await acceptQueued(() => paymentsStore.createPayment(payload))
    if (saved === undefined) {
      toast.info('Payment queued', 'It will be saved when the server is reachable.')
    } else {
      toast.success('Payment recorded', formatMoney(Number(payload.amount)))
    }
    emit('saved')
  } catch (e) {
    submitError.value = apiErrorMessage(e)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const loads: Promise<unknown>[] = [paymentsStore.fetchFormOptions()]
    if (!customersStore.customers.length) loads.push(customersStore.fetchCustomers())
    await Promise.all(loads)
    await loadCustomerSales(partyId.value)
  } catch (e) {
    submitError.value = apiErrorMessage(e)
  }
})
</script>

<style scoped>
.payment-form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.field-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); gap: 1rem; }
.muted { opacity: 0.7; }
.form-error { color: #b42318; margin: 0; }
.actions { display: flex; justify-content: flex-end; gap: 0.5rem; }
</style>
