import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { permission } from './shared/directives/permission'
import { useAuthStore } from './shared/stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.directive('permission', permission)

const authStore = useAuthStore()
authStore.initializeAuth()

app.mount('#app')
