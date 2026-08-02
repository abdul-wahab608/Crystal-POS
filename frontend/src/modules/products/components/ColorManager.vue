<template>
  <div class="color-manager">
    <h3 class="font-bold mb-2">Manage Colors</h3>
    <form @submit.prevent="addColor" class="flex gap-2 mb-2">
      <input v-model="newColor" placeholder="Add color" class="input" />
      <button type="submit" class="btn">Add</button>
    </form>
    <ul>
      <li v-for="c in colors" :key="c.id" class="flex items-center gap-2 mb-1">
        <span>{{ c.name }}</span>
        <button @click="deleteColor(c.id)" class="btn btn-danger">Delete</button>
      </li>
    </ul>
    <div v-if="error" class="text-red-500 mt-2">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useColorStore } from '../stores/color'

const store = useColorStore()
const { colors, error } = storeToRefs(store)
const newColor = ref('')

onMounted(() => {
  store.fetchColors()
})

const addColor = async () => {
  if (!newColor.value.trim()) return
  await store.addColor(newColor.value.trim())
  newColor.value = ''
}

const deleteColor = async (id: number) => {
  await store.deleteColor(id)
}
</script>

<style scoped>
.color-manager { margin-bottom: 2rem; }
.input { border: 1px solid #ccc; padding: 0.5rem; border-radius: 4px; }
.btn { background: #2563eb; color: #fff; padding: 0.3rem 0.7rem; border-radius: 4px; }
.btn-danger { background: #dc2626; }
</style>
