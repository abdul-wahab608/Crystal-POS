<template>
  <div class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
    <form @submit.prevent="onSubmit" class="bg-white p-6 rounded shadow w-96">
      <h2 class="text-lg font-bold mb-4">{{ user?.id ? 'Edit' : 'Add' }} User</h2>
      <div class="mb-3">
        <label for="username" class="block text-sm font-medium mb-1">Username</label>
        <input v-model="form.username" id="username" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="email" class="block text-sm font-medium mb-1">Email</label>
        <input v-model="form.email" id="email" type="email" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="password" class="block text-sm font-medium mb-1">Password</label>
        <input v-model="form.password" id="password" type="password" class="w-full border px-2 py-1 rounded" :required="!user?.id" />
      </div>
      <div class="mb-3">
        <label for="first_name" class="block text-sm font-medium mb-1">First Name</label>
        <input v-model="form.first_name" id="first_name" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="last_name" class="block text-sm font-medium mb-1">Last Name</label>
        <input v-model="form.last_name" id="last_name" class="w-full border px-2 py-1 rounded" required />
      </div>
      <div class="mb-3">
        <label for="role" class="block text-sm font-medium mb-1">Role</label>
        <select v-model="form.role" id="role" class="w-full border px-2 py-1 rounded" required>
          <option value="ADMIN">Admin</option>
          <option value="MANAGER">Manager</option>
          <option value="STAFF">Staff</option>
          <option value="VIEWER">Viewer</option>
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
import { ref, watch, defineProps, defineEmits } from 'vue'
import type { User, CreateUserRequest, UpdateUserRequest } from '../types'

interface Props {
  user?: User | null
}

const props = defineProps<Props>()
const emit = defineEmits(['save', 'close'])

const form = ref<CreateUserRequest | UpdateUserRequest>({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  role: 'STAFF',
  is_active: true
})

watch(() => props.user, (val) => {
  if (val) {
    form.value = {
      username: val.username,
      email: val.email,
      first_name: val.first_name,
      last_name: val.last_name,
      role: val.role,
      is_active: val.is_active
    }
  } else {
    form.value = {
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: 'STAFF',
      is_active: true
    }
  }
}, { immediate: true })

function onSubmit() {
  emit('save', { ...form.value })
}
</script> 