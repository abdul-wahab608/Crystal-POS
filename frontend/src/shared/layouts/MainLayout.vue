<template>
  <div class="app-container">
    <nav class="navbar" ref="navbar">
      <div class="nav-container">
        <div class="nav-content">
          <div class="nav-left">
            <div class="logo">
              <h1>Crystal POS</h1>
            </div>
            <div class="nav-links">
              <router-link
                :to="NAV_DASHBOARD.href"
                :class="['nav-link', $route.path === NAV_DASHBOARD.href ? 'active' : '']"
              >
                {{ NAV_DASHBOARD.name }}
              </router-link>
              <div
                v-for="section in sections"
                :key="section.name"
                class="nav-section"
                :class="{ open: openSection === section.name }"
              >
                <button
                  type="button"
                  :class="['nav-link', 'nav-section-btn', { active: activeSection === section.name }]"
                  :aria-expanded="openSection === section.name"
                  @click.stop="toggleSection(section.name)"
                >
                  {{ section.name }}
                  <span class="caret" aria-hidden="true">▾</span>
                </button>
                <div v-if="openSection === section.name" class="nav-dropdown" role="menu">
                  <router-link
                    v-for="item in section.items"
                    :key="item.href"
                    :to="item.href"
                    role="menuitem"
                    :class="['nav-dropdown-link', $route.path === item.href ? 'active' : '']"
                    @click="openSection = null"
                  >
                    {{ item.name }}
                  </router-link>
                </div>
              </div>
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

    <main class="main-content">
      <div class="content-container">
        <router-view />
      </div>
    </main>

    <LoginForm
      v-if="showLoginForm"
      @close="showLoginForm = false"
      @success="handleLoginSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginForm from '../components/LoginForm.vue'
import { NAV_DASHBOARD, NAV_SECTIONS, sectionForPath, visibleSections } from './navGroups'

const authStore = useAuthStore()
const route = useRoute()
const navbar = ref<HTMLElement | null>(null)
const showLoginForm = ref(false)
const openSection = ref<string | null>(null)

const sections = computed(() => visibleSections(NAV_SECTIONS, authStore.user))
const activeSection = computed(() => sectionForPath(sections.value, route.path))

function toggleSection(name: string) {
  openSection.value = openSection.value === name ? null : name
}

function onDocumentClick(event: MouseEvent) {
  if (navbar.value && !navbar.value.contains(event.target as Node)) openSection.value = null
}

watch(() => route.path, () => { openSection.value = null })

onMounted(() => document.addEventListener('click', onDocumentClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocumentClick))

const handleLoginSuccess = () => {
  showLoginForm.value = false
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
  position: relative;
  z-index: 20;
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
  min-height: 64px;
  gap: 1rem;
}

.nav-left {
  display: flex;
  align-items: center;
  min-width: 0;
}

.logo h1 {
  font-size: 1.25rem;
  font-weight: bold;
  color: #111827;
  margin: 0;
  white-space: nowrap;
}

.nav-links {
  display: flex;
  align-items: center;
  margin-left: 1.5rem;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.nav-link,
.nav-section-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0;
  border: none;
  border-bottom: 2px solid transparent;
  background: none;
  font: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-link:hover,
.nav-section-btn:hover {
  color: #374151;
  border-color: #d1d5db;
}

.nav-link.active,
.nav-section-btn.active {
  color: #111827;
  border-color: #2563eb;
}

.nav-section {
  position: relative;
}

.caret {
  font-size: 0.7rem;
}

.nav-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
  padding: 0.375rem;
}

.nav-dropdown-link {
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #374151;
  text-decoration: none;
}

.nav-dropdown-link:hover {
  background: #f3f4f6;
}

.nav-dropdown-link.active {
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 600;
}

.nav-right {
  display: flex;
  align-items: center;
  flex-shrink: 0;
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

@media (max-width: 900px) {
  .nav-content {
    flex-direction: column;
    align-items: stretch;
    padding: 0.5rem 0;
  }

  .nav-left {
    flex-direction: column;
    align-items: flex-start;
  }

  .nav-links {
    margin-left: 0;
  }

  .nav-right {
    justify-content: flex-end;
  }
}
</style>
