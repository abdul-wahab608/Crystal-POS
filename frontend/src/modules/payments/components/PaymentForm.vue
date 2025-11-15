<template>
  <div class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
    <form @submit.prevent="onSubmit" class="bg-white p-6 rounded shadow w-96">
      <h2 class="text-lg font-bold mb-4">{{ payment?.id ? 'Edit' : 'Add' }} Payment</h2>
      <div class="mb-3">
        <label for="amount" class="block text-sm font-medium mb-1">Amount</label>
        <input v-model.number="form.amount" id="amount" type="number" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="payment_type" class="block text-sm font-medium mb-1">Payment Type</label>
        <select v-model="form.payment_type" id="payment_type" class="w-full border px-2 py-1 rounded" required>
          <option value="INCOMING">Incoming</option>
          <option value="OUTGOING">Outgoing</option>
          <option value="DIRECT">Direct</option>
        </select>
      </div>
      <div class="mb-3">
        <label for="payment_method" class="block text-sm font-medium mb-1">Payment Method</label>
        <select v-model="form.payment_method" id="payment_method" class="w-full border px-2 py-1 rounded" required>
          <option value="CASH">Cash</option>
          <option value="BANK">Bank Transfer</option>
          <option value="CHEQUE">Cheque</option>
          <option value="PARCHI">Parchi</option>
        </select>
      </div>
      <div class="mb-3">
        <label for="related_entity" class="block text-sm font-medium mb-1">Related Entity</label>
        <select v-model="form.related_entity" id="related_entity" class="w-full border px-2 py-1 rounded" required>
          <option value="CUSTOMER">Customer</option>
          <option value="VENDOR">Vendor</option>
          <option value="SALE">Sale</option>
          <option value="PURCHASE">Purchase</option>
        </select>
      </div>
      <div class="mb-3">
        <label for="payment_date" class="block text-sm font-medium mb-1">Payment Date</label>
        <input v-model="form.payment_date" id="payment_date" type="date" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="date" class="block text-sm font-medium mb-1">Transaction Date</label>
        <input v-model="form.date" id="date" type="date" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="status" class="block text-sm font-medium mb-1">Status</label>
        <select v-model="form.status" id="status" class="w-full border px-2 py-1 rounded" required>
          <option value="PENDING">Pending</option>
          <option value="COMPLETED">Completed</option>
          <option value="FAILED">Failed</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
      </div>
      <div class="mb-3">
        <label for="reference_number" class="block text-sm font-medium mb-1">Reference Number</label>
        <input v-model="form.reference_number" id="reference_number" class="w-full border px-2 py-1 rounded" />
      </div>
      <div class="mb-3">
        <label for="notes" class="block text-sm font-medium mb-1">Notes</label>
        <textarea v-model="form.notes" id="notes" class="w-full border px-2 py-1 rounded" rows="3"></textarea>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <button type="button" @click="$emit('close')" class="px-3 py-1 bg-gray-200 rounded">Cancel</button>
        <button type="submit" class="px-3 py-1 bg-blue-600 text-white rounded">Save</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'
import type { Payment, CreatePaymentRequest } from '../types'

interface Props {
  payment?: Payment | null
}

const props = defineProps<Props>()
const emit = defineEmits(['save', 'close'])

const form = ref<CreatePaymentRequest>({
  amount: 0,
  payment_type: 'INCOMING',
  payment_method: 'CASH',
  related_entity: 'CUSTOMER',
  payment_date: new Date().toISOString().split('T')[0],
  date: new Date().toISOString().split('T')[0],
  status: 'PENDING',
  reference_number: '',
  notes: ''
})

watch(() => props.payment, (val) => {
  if (val) {
    form.value = {
      amount: val.amount,
      payment_type: val.payment_type,
      payment_method: val.payment_method,
      related_entity: val.related_entity,
      payment_date: val.payment_date,
      date: val.date,
      status: val.status,
      reference_number: val.reference_number,
      notes: val.notes
    }
  } else {
    form.value = {
      amount: 0,
      payment_type: 'INCOMING',
      payment_method: 'CASH',
      related_entity: 'CUSTOMER',
      payment_date: new Date().toISOString().split('T')[0],
      date: new Date().toISOString().split('T')[0],
      status: 'PENDING',
      reference_number: '',
      notes: ''
    }
  }
}, { immediate: true })

function onSubmit() {
  emit('save', { ...form.value })
}
</script> 