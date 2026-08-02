<template>
  <div class="size-range-manager">
    <h3 class="font-bold mb-2">Manage Size Ranges</h3>
    <form @submit.prevent="addSizeRange" class="flex gap-2 mb-2">
      <input v-model="newSizeRange" placeholder="Add size range" class="input" />
      <button type="submit" class="btn">Add</button>
    </form>
    <ul>
      <li v-for="sr in sizeRanges" :key="sr.id" class="flex items-center gap-2 mb-1">
        <span>{{ sr.name }}</span>
        <button @click="deleteSizeRange(sr.id)" class="btn btn-danger">Delete</button>
      </li>
    </ul>
    <div v-if="error" class="text-red-500 mt-2">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSizeRangeStore } from '../stores/sizeRange'

const store = useSizeRangeStore()
const { sizeRanges, error } = storeToRefs(store)
const newSizeRange = ref('')

onMounted(() => {
  store.fetchSizeRanges()
})

const addSizeRange = async () => {
  if (!newSizeRange.value.trim()) return
  await store.addSizeRange(newSizeRange.value.trim())
  newSizeRange.value = ''
}

const deleteSizeRange = async (id: number) => {
  await store.deleteSizeRange(id)
}
</script>

<style scoped>
.size-range-manager { margin-bottom: 2rem; }
.input { border: 1px solid #ccc; padding: 0.5rem; border-radius: 4px; }
.btn { background: #2563eb; color: #fff; padding: 0.3rem 0.7rem; border-radius: 4px; }
.btn-danger { background: #dc2626; }
</style>
