<template>
  <table class="min-w-full bg-white">
    <thead>
      <tr>
        <th class="py-2 px-4 border-b">Amount</th>
        <th class="py-2 px-4 border-b">Type</th>
        <th class="py-2 px-4 border-b">Related Entity</th>
        <th class="py-2 px-4 border-b">Date</th>
        <th class="py-2 px-4 border-b">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="payment in payments" :key="payment.id">
        <td class="py-2 px-4 border-b">{{ payment.amount }}</td>
        <td class="py-2 px-4 border-b">{{ payment.payment_type }}</td>
        <td class="py-2 px-4 border-b">{{ payment.related_entity_name }}</td>
        <td class="py-2 px-4 border-b">{{ payment.date }}</td>
        <td class="py-2 px-4 border-b">
          <button @click="$emit('edit', payment)" class="text-blue-600 mr-2">Edit</button>
          <button @click="$emit('delete', payment.id)" class="text-red-600">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
defineProps<{ payments: any[] }>()
defineEmits(['edit', 'delete'])
</script> 