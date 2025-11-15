<template>
  <table class="min-w-full bg-white">
    <thead>
      <tr>
        <th class="py-2 px-4 border-b">Customer</th>
        <th class="py-2 px-4 border-b">Total</th>
        <th class="py-2 px-4 border-b">Date</th>
        <th class="py-2 px-4 border-b">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="sale in sales" :key="sale.id">
        <td class="py-2 px-4 border-b">{{ sale.customer_name }}</td>
        <td class="py-2 px-4 border-b">{{ sale.total }}</td>
        <td class="py-2 px-4 border-b">{{ sale.date }}</td>
        <td class="py-2 px-4 border-b">
          <button @click="$emit('edit', sale)" class="text-blue-600 mr-2">Edit</button>
          <button @click="$emit('delete', sale.id)" class="text-red-600">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
defineProps<{ sales: any[] }>()
defineEmits(['edit', 'delete'])
</script> 