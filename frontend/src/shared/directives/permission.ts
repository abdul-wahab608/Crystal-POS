import type { Directive } from 'vue'
import { useAuthStore } from '../stores/auth'

export const permission: Directive = {
  mounted(el, binding) {
    const authStore = useAuthStore()
    const { value } = binding
    
    if (typeof value === 'string') {
      if (!authStore.hasPermission(value)) {
        el.style.display = 'none'
      }
    } else if (Array.isArray(value)) {
      const hasAnyPermission = value.some(permission => authStore.hasPermission(permission))
      if (!hasAnyPermission) {
        el.style.display = 'none'
      }
    }
  },
  
  updated(el, binding) {
    const authStore = useAuthStore()
    const { value } = binding
    
    if (typeof value === 'string') {
      if (authStore.hasPermission(value)) {
        el.style.display = ''
      } else {
        el.style.display = 'none'
      }
    } else if (Array.isArray(value)) {
      const hasAnyPermission = value.some(permission => authStore.hasPermission(permission))
      if (hasAnyPermission) {
        el.style.display = ''
      } else {
        el.style.display = 'none'
      }
    }
  }
} 