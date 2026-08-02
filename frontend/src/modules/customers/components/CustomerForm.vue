<template>
  <div class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
    <form @submit.prevent="onSubmit" class="bg-white p-6 rounded shadow w-96">
      <h2 class="text-lg font-bold mb-4">{{ customer?.id ? 'Edit' : 'Add' }} Customer</h2>
      <div class="mb-3">
        <label for="name" class="block text-sm font-medium mb-1">Name</label>
        <input v-model="form.name" id="name" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="phone" class="block text-sm font-medium mb-1">Phone</label>
        <input v-model="form.phone" id="phone" class="w-full border px-2 py-1 rounded" />
      </div>
      <div class="mb-3">
        <label for="city" class="block text-sm font-medium mb-1">City</label>
        <input v-model="form.city" id="city" class="w-full border px-2 py-1 rounded" placeholder="e.g. Karachi" />
      </div>
      <div class="mb-3">
        <label for="address" class="block text-sm font-medium mb-1">Address</label>
        <textarea v-model="form.address" id="address" class="w-full border px-2 py-1 rounded" rows="2"></textarea>
      </div>
      <div class="mb-3">
        <label for="customer_type" class="block text-sm font-medium mb-1">Customer Type</label>
        <select v-model="form.customer_type" id="customer_type" class="w-full border px-2 py-1 rounded">
          <option value="REGULAR">Regular</option>
          <option value="WALK_IN">Walk-in</option>
        </select>
      </div>
      <div class="mb-3">
        <label class="flex items-center">
          <input v-model="form.is_active" type="checkbox" class="mr-2" />
          <span class="text-sm font-medium">Active</span>
        </label>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <button type="button" @click="$emit('close')" class="px-3 py-1 bg-gray-200 rounded">Cancel</button>
        <button type="submit" class="px-3 py-1 bg-blue-600 text-white rounded">Save</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Customer, CreateCustomerRequest } from '../types'

interface Props {
  customer?: Customer | null
}

const props = defineProps<Props>()
const emit = defineEmits(['save', 'close'])

const form = ref<CreateCustomerRequest>({
  name: '',
  phone: '',
  address: '',
  city: '',
  customer_type: 'REGULAR',
  is_active: true
})

watch(() => props.customer, (val) => {
  if (val) {
    form.value = {
      name: val.name,
      phone: val.phone || '',
      address: val.address || '',
      city: val.city || '',
      customer_type: val.customer_type || 'REGULAR',
      is_active: val.is_active
    }
  } else {
    form.value = {
      name: '',
      phone: '',
      address: '',
      city: '',
      customer_type: 'REGULAR',
      is_active: true
    }
  }
}, { immediate: true })

function onSubmit() {
  emit('save', { ...form.value })
}
</script>
