<template>
  <div class="app-container">
    <!-- Navigation -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-content">
          <div class="nav-left">
            <div class="logo">
              <h1>Crystal POS</h1>
            </div>
            <div class="nav-links">
              <router-link
                v-for="item in navigationItems"
                :key="item.name"
                :to="item.href"
                :class="['nav-link', $route.path === item.href ? 'active' : '']"
              >
                {{ item.name }}
              </router-link>
            </div>
          </div>
          
          <div class="nav-right">
            <div v-if="authStore.user" class="user-info">
              <span class="username">{{ authStore.user.username }}</span>
              <span class="role">{{ authStore.user.role }}</span>
              <button @click="authStore.logout" class="logout-btn">Logout</button>
            </div>
            <div v-else class="login-section">
              <button @click="showLoginForm = true" class="login-btn">Login</button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
      <div class="content-container">
        <router-view />
      </div>
    </main>

    <!-- Login Form Modal -->
    <LoginForm 
      v-if="showLoginForm" 
      @close="showLoginForm = false"
      @success="handleLoginSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import LoginForm from '../components/LoginForm.vue'

const authStore = useAuthStore()
const showLoginForm = ref(false)

const navigationItems = [
  { name: 'Dashboard', href: '/', permission: null },
  { name: 'Products', href: '/products', permission: null },
  { name: 'Raw Materials', href: '/raw-materials', permission: null },
  { name: 'Customers', href: '/customers', permission: null },
  { name: 'Vendors', href: '/vendors', permission: null },
  { name: 'Sales', href: '/sales', permission: null },
  { name: 'Purchases', href: '/purchases', permission: null },
  { name: 'Payments', href: '/payments', permission: null },
  { name: 'Reports', href: '/reports', permission: null },
  { name: 'Assets', href: '/assets', permission: null },
  { name: 'Users', href: '/users', permission: null },
]

const handleLoginSuccess = () => {
  showLoginForm.value = false
  // You can add any additional logic here after successful login
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.navbar {
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e5e7eb;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.nav-left {
  display: flex;
  align-items: center;
}

.logo h1 {
  font-size: 1.25rem;
  font-weight: bold;
  color: #111827;
  margin: 0;
}

.nav-links {
  display: none;
}

@media (min-width: 768px) {
  .nav-links {
    display: flex;
    margin-left: 1.5rem;
    gap: 2rem;
  }
}

.nav-link {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0;
  border-bottom: 2px solid transparent;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #374151;
  border-color: #d1d5db;
}

.nav-link.active {
  color: #111827;
  border-color: #2563eb;
}

.nav-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  font-size: 0.875rem;
  color: #374151;
}

.role {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  background-color: #dbeafe;
  color: #1e40af;
}

.logout-btn {
  color: #6b7280;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
}

.logout-btn:hover {
  color: #374151;
}

.login-btn {
  color: #2563eb;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.875rem;
}

.login-btn:hover {
  color: #1d4ed8;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}

.content-container {
  padding: 1.5rem 0;
}
</style> 