<template>
  <input
    v-model="search"
    class="border px-2 py-1 rounded w-full mb-4"
    placeholder="Search..."
  />
</template>
<script setup lang="ts">
import { defineModel } from 'vue'
const search = defineModel<string>()
</script> 