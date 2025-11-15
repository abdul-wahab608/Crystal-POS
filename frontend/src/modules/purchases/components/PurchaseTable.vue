<template>
  <table class="min-w-full bg-white">
    <thead>
      <tr>
        <th class="py-2 px-4 border-b">Vendor</th>
        <th class="py-2 px-4 border-b">Total</th>
        <th class="py-2 px-4 border-b">Date</th>
        <th class="py-2 px-4 border-b">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="purchase in purchases" :key="purchase.id">
        <td class="py-2 px-4 border-b">{{ purchase.vendor_name }}</td>
        <td class="py-2 px-4 border-b">{{ purchase.total }}</td>
        <td class="py-2 px-4 border-b">{{ purchase.date }}</td>
        <td class="py-2 px-4 border-b">
          <button @click="$emit('edit', purchase)" class="text-blue-600 mr-2">Edit</button>
          <button @click="$emit('delete', purchase.id)" class="text-red-600">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
defineProps<{ purchases: any[] }>()
defineEmits(['edit', 'delete'])
</script> 