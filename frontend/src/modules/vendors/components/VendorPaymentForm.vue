<template>
  <form class="payment-form" @submit.prevent="submit">
    <h3 class="form-title">Record payment to {{ vendor.name }}</h3>
    <div class="fields">
      <div class="field">
        <label :for="`pay-amount-${vendor.id}`">Amount *</label>
        <input :id="`pay-amount-${vendor.id}`" v-model.number="form.amount" type="number" min="0.01" step="0.01" class="form-input" required />
      </div>
      <div class="field">
        <label :for="`pay-method-${vendor.id}`">Method</label>
        <select :id="`pay-method-${vendor.id}`" v-model="form.payment_method" class="form-input">
          <option value="CASH">Cash</option>
          <option value="BANK">Bank transfer</option>
          <option value="CHEQUE">Cheque</option>
          <option value="PARCHI">Parchi (promissory)</option>
        </select>
      </div>
      <div class="field wide">
        <label :for="`pay-bill-${vendor.id}`">Pays which purchase bill (optional)</label>
        <SearchableSelect :id="`pay-bill-${vendor.id}`" :model-value="billId" :options="billOptions" placeholder="Not tied to a bill" @update:model-value="onBillChange" />
        <small v-if="!billOptions.length" class="muted">This vendor has no bills with a balance.</small>
        <small v-if="selectedBill" class="muted">Unpaid on this bill: {{ formatMoney(Number(selectedBill.unpaid_amount)) }}</small>
      </div>
      <div v-if="form.payment_method === 'BANK'" class="field">
        <label :for="`pay-bank-${vendor.id}`">Bank name *</label>
        <input :id="`pay-bank-${vendor.id}`" v-model="form.bank_name" type="text" class="form-input" required />
      </div>
      <div class="field">
        <label :for="`pay-ref-${vendor.id}`">Reference</label>
        <input :id="`pay-ref-${vendor.id}`" v-model="form.reference" type="text" class="form-input" />
      </div>
      <div class="field wide">
        <label :for="`pay-notes-${vendor.id}`">Notes</label>
        <input :id="`pay-notes-${vendor.id}`" v-model="form.notes" type="text" class="form-input" />
      </div>
    </div>
    <p v-if="error" class="form-error">{{ error }}</p>
    <div class="form-actions">
      <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
      <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Saving...' : 'Record payment' }}</button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import { useVendorsStore } from '../stores/vendors'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { errorMessageOf } from '../../raw_materials/utils/errorMessage'
import { useVendorBill } from '../../payments/composables/useVendorBill'
import { formatMoney } from '../../../shared/utils/perUnit'
import type { Vendor, VendorPaymentPayload } from '../types'

const props = defineProps<{ vendor: Vendor }>()
const emit = defineEmits<{ success: []; cancel: [] }>()

const vendorsStore = useVendorsStore()
const { billId, options: billOptions, selectedBill, loadBills, billError } = useVendorBill()

onMounted(() => loadBills(props.vendor.id))

function onBillChange(value: string | number | null) {
  billId.value = value === null ? null : Number(value)
}

const form = reactive<{
  amount: number | null
  payment_method: VendorPaymentPayload['payment_method']
  bank_name: string
  reference: string
  notes: string
}>({
  amount: null,
  payment_method: 'CASH',
  bank_name: '',
  reference: '',
  notes: '',
})
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  if (!(Number(form.amount) > 0)) {
    error.value = 'Amount must be greater than zero.'
    return
  }
  const billMessage = billError(form.amount)
  if (billMessage) {
    error.value = billMessage
    return
  }
  saving.value = true
  try {
    await acceptQueued(() => vendorsStore.recordPayment({
      vendor: props.vendor.id,
      purchase: billId.value ?? undefined,
      payment_method: form.payment_method,
      amount: Number(form.amount),
      bank_name: form.payment_method === 'BANK' ? form.bank_name : undefined,
      reference: form.reference,
      notes: form.notes,
    }))
    emit('success')
  } catch (e) {
    error.value = errorMessageOf(e)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.payment-form { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 1rem; margin: 0.75rem 0; }
.form-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 0.75rem; }
.fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; }
.field.wide { grid-column: 1 / -1; }
.field label { display: block; font-size: 0.8125rem; font-weight: 500; margin-bottom: 0.25rem; }
.form-input { width: 100%; padding: 0.5rem 0.625rem; border: 1px solid #d1d5db; border-radius: 0.375rem; background: white; }
.form-error { color: #b91c1c; font-size: 0.875rem; margin-top: 0.5rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.75rem; }
.btn-primary:disabled { opacity: 0.6; }
</style>
