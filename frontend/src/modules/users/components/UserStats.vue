<template>
  <div class="mb-4">
    <div class="text-lg font-bold">User Stats</div>
    <div class="flex gap-8 mt-2">
      <div>
        <div class="text-2xl font-semibold">{{ users.length }}</div>
        <div class="text-gray-500">Total Users</div>
      </div>
      <div>
        <div class="text-2xl font-semibold">{{ adminCount }}</div>
        <div class="text-gray-500">Admins</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { User } from '../types'
const props = defineProps<{ users: User[] }>()
const adminCount = computed(() => props.users.filter(u => u.role === 'ADMIN').length)
</script> 