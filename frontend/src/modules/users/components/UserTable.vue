<template>
  <table class="min-w-full bg-white">
    <thead>
      <tr>
        <th class="py-2 px-4 border-b">Username</th>
        <th class="py-2 px-4 border-b">Email</th>
        <th class="py-2 px-4 border-b">Role</th>
        <th class="py-2 px-4 border-b">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="user in users" :key="user.id">
        <td class="py-2 px-4 border-b">{{ user.username }}</td>
        <td class="py-2 px-4 border-b">{{ user.email }}</td>
        <td class="py-2 px-4 border-b">{{ user.role }}</td>
        <td class="py-2 px-4 border-b">
          <button @click="$emit('edit', user)" class="text-blue-600 mr-2">Edit</button>
          <button @click="$emit('delete', user.id)" class="text-red-600">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
defineProps<{ users: any[] }>()
defineEmits(['edit', 'delete'])
</script> 