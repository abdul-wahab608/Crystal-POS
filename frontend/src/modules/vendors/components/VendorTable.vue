<template>
  <table class="min-w-full bg-white">
    <thead>
      <tr>
        <th class="py-2 px-4 border-b">Name</th>
        <th class="py-2 px-4 border-b">Contact</th>
        <th class="py-2 px-4 border-b">Email</th>
        <th class="py-2 px-4 border-b">Phone</th>
        <th class="py-2 px-4 border-b">Balance</th>
        <th class="py-2 px-4 border-b">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="vendor in vendors" :key="vendor.id">
        <td class="py-2 px-4 border-b">{{ vendor.name }}</td>
        <td class="py-2 px-4 border-b">{{ vendor.contact }}</td>
        <td class="py-2 px-4 border-b">{{ vendor.email }}</td>
        <td class="py-2 px-4 border-b">{{ vendor.phone }}</td>
        <td class="py-2 px-4 border-b">{{ vendor.balance }}</td>
        <td class="py-2 px-4 border-b">
          <button @click="$emit('edit', vendor)" class="text-blue-600 mr-2">Edit</button>
          <button @click="$emit('delete', vendor.id)" class="text-red-600">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
defineProps<{ vendors: any[] }>()
defineEmits(['edit', 'delete'])
</script> 