<template>
  <div class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
    <form @submit.prevent="onSubmit" class="bg-white p-6 rounded shadow w-96">
      <h2 class="text-lg font-bold mb-4">{{ asset?.id ? 'Edit' : 'Add' }} Asset</h2>
      <div class="mb-3">
        <label for="name" class="block text-sm font-medium mb-1">Name</label>
        <input v-model="form.name" id="name" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="description" class="block text-sm font-medium mb-1">Description</label>
        <textarea v-model="form.description" id="description" class="w-full border px-2 py-1 rounded" rows="3"></textarea>
      </div>
      <div class="mb-3">
        <label for="category" class="block text-sm font-medium mb-1">Category</label>
        <input v-model="form.category" id="category" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="type" class="block text-sm font-medium mb-1">Type</label>
        <select v-model="form.type" id="type" class="w-full border px-2 py-1 rounded" required>
          <option value="EQUIPMENT">Equipment</option>
          <option value="VEHICLE">Vehicle</option>
          <option value="BUILDING">Building</option>
          <option value="LAND">Land</option>
          <option value="SOFTWARE">Software</option>
          <option value="OTHER">Other</option>
        </select>
      </div>
      <div class="mb-3">
        <label for="purchase_value" class="block text-sm font-medium mb-1">Purchase Value</label>
        <input v-model.number="form.purchase_value" id="purchase_value" type="number" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="current_value" class="block text-sm font-medium mb-1">Current Value</label>
        <input v-model.number="form.current_value" id="current_value" type="number" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="purchase_date" class="block text-sm font-medium mb-1">Purchase Date</label>
        <input v-model="form.purchase_date" id="purchase_date" type="date" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="location" class="block text-sm font-medium mb-1">Location</label>
        <input v-model="form.location" id="location" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="status" class="block text-sm font-medium mb-1">Status</label>
        <select v-model="form.status" id="status" class="w-full border px-2 py-1 rounded" required>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
          <option value="MAINTENANCE">Maintenance</option>
          <option value="RETIRED">Retired</option>
        </select>
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
import type { Asset, CreateAssetRequest } from '../types'

interface Props {
  asset?: Asset | null
}

const props = defineProps<Props>()
const emit = defineEmits(['save', 'close'])

const form = ref<CreateAssetRequest>({
  name: '',
  description: '',
  category: '',
  type: 'EQUIPMENT',
  value: 0,
  current_value: 0,
  purchase_value: 0,
  purchase_date: new Date().toISOString().split('T')[0],
  location: '',
  status: 'ACTIVE'
})

watch(() => props.asset, (val) => {
  if (val) {
    form.value = {
      name: val.name,
      description: val.description,
      category: val.category,
      type: val.type,
      value: val.value,
      current_value: val.current_value,
      purchase_value: val.purchase_value,
      purchase_date: val.purchase_date,
      location: val.location,
      status: val.status
    }
  } else {
    form.value = {
      name: '',
      description: '',
      category: '',
      type: 'EQUIPMENT',
      value: 0,
      current_value: 0,
      purchase_value: 0,
      purchase_date: new Date().toISOString().split('T')[0],
      location: '',
      status: 'ACTIVE'
    }
  }
}, { immediate: true })

function onSubmit() {
  emit('save', { ...form.value })
}
</script> 