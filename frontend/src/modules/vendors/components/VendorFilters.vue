<template>
  <input
    v-model="search"
    class="form-input w-full mb-4"
    placeholder="Search..."
  />
</template>
<script setup lang="ts">
import { defineModel } from 'vue'
const search = defineModel<string>()
</script> 