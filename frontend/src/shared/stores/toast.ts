import { defineStore } from 'pinia'

interface Toast {
  id: string
  title: string
  message?: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: [] as Toast[]
  }),

  actions: {
    add(toast: Omit<Toast, 'id'>) {
      const id = Math.random().toString(36).substr(2, 9)
      this.toasts.push({ ...toast, id })
    },

    remove(id: string) {
      this.toasts = this.toasts.filter(toast => toast.id !== id)
    },

    success(title: string, message?: string, duration?: number) {
      this.add({ title, message, type: 'success', duration })
    },

    error(title: string, message?: string, duration?: number) {
      this.add({ title, message, type: 'error', duration })
    },

    warning(title: string, message?: string, duration?: number) {
      this.add({ title, message, type: 'warning', duration })
    },

    info(title: string, message?: string, duration?: number) {
      this.add({ title, message, type: 'info', duration })
    }
  }
}) 