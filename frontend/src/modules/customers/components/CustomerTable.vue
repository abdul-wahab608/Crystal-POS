<template>
  <table class="min-w-full bg-white">
    <thead>
      <tr>
        <th class="py-2 px-4 border-b">Name</th>
        <th class="py-2 px-4 border-b">Email</th>
        <th class="py-2 px-4 border-b">Phone</th>
        <th class="py-2 px-4 border-b">Balance</th>
        <th class="py-2 px-4 border-b">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="customer in customers" :key="customer.id">
        <td class="py-2 px-4 border-b">{{ customer.name }}</td>
        <td class="py-2 px-4 border-b">{{ customer.email }}</td>
        <td class="py-2 px-4 border-b">{{ customer.phone }}</td>
        <td class="py-2 px-4 border-b">{{ customer.balance }}</td>
        <td class="py-2 px-4 border-b">
          <button @click="$emit('edit', customer)" class="text-blue-600 mr-2">Edit</button>
          <button @click="$emit('delete', customer.id)" class="text-red-600">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
defineProps<{ customers: any[] }>()
defineEmits(['edit', 'delete'])
</script> 