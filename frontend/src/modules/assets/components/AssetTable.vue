<template>
  <table class="min-w-full bg-white">
    <thead>
      <tr>
        <th class="py-2 px-4 border-b">Name</th>
        <th class="py-2 px-4 border-b">Type</th>
        <th class="py-2 px-4 border-b">Value</th>
        <th class="py-2 px-4 border-b">Status</th>
        <th class="py-2 px-4 border-b">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="asset in assets" :key="asset.id">
        <td class="py-2 px-4 border-b">{{ asset.name }}</td>
        <td class="py-2 px-4 border-b">{{ asset.type }}</td>
        <td class="py-2 px-4 border-b">{{ asset.value }}</td>
        <td class="py-2 px-4 border-b">{{ asset.status }}</td>
        <td class="py-2 px-4 border-b">
          <button @click="$emit('edit', asset)" class="text-blue-600 mr-2">Edit</button>
          <button @click="$emit('delete', asset.id)" class="text-red-600">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
defineProps<{ assets: any[] }>()
defineEmits(['edit', 'delete'])
</script> 