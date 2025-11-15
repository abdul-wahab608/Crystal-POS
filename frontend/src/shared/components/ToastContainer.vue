<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <Toast
      v-for="toast in toasts"
      :key="toast.id"
      :title="toast.title"
      :message="toast.message"
      :type="toast.type"
      :duration="toast.duration"
      @close="removeToast(toast.id)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useToastStore } from '../stores/toast'
import Toast from './Toast.vue'

const toastStore = useToastStore()

const toasts = computed(() => toastStore.toasts)

const removeToast = (id: string) => {
  toastStore.remove(id)
}
</script> 