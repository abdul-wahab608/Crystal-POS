<template>
  <div class="users-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Users Management</h1>
      <button v-if="authStore.canManageUsers" @click="showAddForm = true" class="btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Add User
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading users...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="!authStore.canManageUsers || store.error" class="error-state">
      <p class="error-message">{{ authStore.canManageUsers ? store.error : 'You do not have access to user management. Ask an administrator.' }}</p>
      <button v-if="authStore.canManageUsers" @click="store.fetchUsers()" class="btn-secondary">Try Again</button>
    </div>

    <!-- Content -->
    <div v-else class="content">
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ users.length }}</div>
          <div class="stat-label">Total Users</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ activeUsers }}</div>
          <div class="stat-label">Active Users</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ adminUsers }}</div>
          <div class="stat-label">Administrators</div>
        </div>
      </div>

      <!-- Search -->
      <div class="filters-section">
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Search users..." 
          class="search-input"
        />
      </div>

      <!-- Users Table -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Last Login</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in pageItems" :key="user.id" class="table-row">
              <td>
                <div class="user-info">
                  <div class="user-avatar">
                    {{ user.first_name.charAt(0).toUpperCase() }}{{ user.last_name.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="user-name">{{ user.first_name }} {{ user.last_name }}</div>
                    <div class="user-username">@{{ user.username }}</div>
                  </div>
                </div>
              </td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="getRoleClass(user.role)">
                  {{ ROLE_LABELS[user.role] ?? user.role }}
                </span>
              </td>
              <td>
                <span :class="user.is_active ? 'status-active' : 'status-inactive'">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>{{ formatDate(user.last_login) }}</td>
              <td>
                <div class="actions">
                  <button v-if="authStore.canManageUsers" @click="editUser(user)" class="action-btn edit">Edit</button>
                  <button v-if="authStore.canManageUsers && user.id !== authStore.user?.id" @click="deleteUser(user.id)" class="action-btn delete">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredUsers.length === 0" class="empty-state">
          <p>No users found.</p>
          <button v-if="authStore.canManageUsers" @click="showAddForm = true" class="btn-primary">Add Your First User</button>
        </div>
        <PaginationBar
          :page="page"
          :totalPages="totalPages"
          :total="total"
          :pageSize="pageSize"
          @update:page="goTo"
          @update:pageSize="setPageSize"
        />
      </div>
    </div>

    <!-- Add/Edit User Modal -->
    <div v-if="showAddForm || showEditForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ showEditForm ? 'Edit User' : 'Add New User' }}</h2>
          <button @click="closeForm" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveUser" class="modal-form">
          <div class="form-row">
            <div class="form-group">
              <label for="first_name">First Name</label>
              <input 
                id="first_name"
                v-model="form.first_name" 
                type="text" 
                required 
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label for="last_name">Last Name</label>
              <input 
                id="last_name"
                v-model="form.last_name" 
                type="text" 
                required 
                class="form-input"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label for="username">Username</label>
            <input 
              id="username"
              v-model="form.username" 
              type="text" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="password">{{ showEditForm ? 'New Password' : 'Password' }}</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              :required="!showEditForm"
              :placeholder="showEditForm ? 'Leave blank to keep current password' : ''"
              minlength="6"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="role">Role</label>
            <select id="role" v-model="form.role" required class="form-input">
              <option value="ADMIN">Administrator</option>
              <option value="MANAGER">Manager</option>
              <option value="CASHIER">Cashier</option>
              <option value="STAFF">Staff</option>
            </select>
          </div>

          <p v-if="formError" class="error-message">{{ formError }}</p>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="form.is_active" 
                type="checkbox" 
                class="checkbox"
              />
              Active User
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">
              {{ showEditForm ? 'Update' : 'Create' }} User
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useUsersStore } from '../stores/users'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import type { User, CreateUserRequest } from '../types'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { useAuthStore } from '../../../shared/stores/auth'

const store = useUsersStore()
const authStore = useAuthStore()
const searchTerm = ref('')
const showAddForm = ref(false)
const showEditForm = ref(false)
const editingUser = ref<User | null>(null)
const formError = ref('')

const ROLE_LABELS: Record<string, string> = {
  ADMIN: 'Administrator', MANAGER: 'Manager', CASHIER: 'Cashier', STAFF: 'Staff',
}

function emptyForm(): CreateUserRequest {
  return {
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    role: 'STAFF',
    is_active: true
  }
}

const form = ref<CreateUserRequest>(emptyForm())

function errorMessage(error: any): string {
  const data = error?.response?.data
  if (!data) return error?.message || 'Request failed'
  if (typeof data === 'string') return data
  if (data.detail) return String(data.detail)
  return Object.entries(data)
    .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(' ') : msgs}`)
    .join('\n')
}

onMounted(() => {
  if (authStore.canManageUsers) store.fetchUsers()
})

const users = computed(() => store.users || [])

const filteredUsers = computed(() => {
  if (!searchTerm.value) return users.value
  return users.value.filter(user => 
    user.first_name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    user.last_name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    user.username.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(filteredUsers)
watch(searchTerm, reset)

const activeUsers = computed(() => 
  users.value.filter(u => u.is_active).length
)

const adminUsers = computed(() =>
  users.value.filter(u => u.role === 'ADMIN').length
)

function editUser(user: User) {
  editingUser.value = user
  form.value = {
    first_name: user.first_name,
    last_name: user.last_name,
    username: user.username,
    email: user.email,
    password: '',
    role: user.role,
    is_active: user.is_active
  }
  formError.value = ''
  showEditForm.value = true
}

async function deleteUser(id: number) {
  if (!confirm('Are you sure you want to delete this user?')) return
  try {
    await acceptQueued(() => store.deleteUser(id))
  } catch (error) {
    alert(errorMessage(error))
  }
}

async function saveUser() {
  formError.value = ''
  try {
    if (showEditForm.value) {
      await acceptQueued(() => store.updateUser(editingUser.value!.id, { ...form.value }))
    } else {
      await acceptQueued(() => store.createUser({ ...form.value }))
    }
    closeForm()
  } catch (error) {
    formError.value = errorMessage(error)
  }
}

function closeForm() {
  showAddForm.value = false
  showEditForm.value = false
  editingUser.value = null
  formError.value = ''
  form.value = emptyForm()
}

function formatDate(dateString: string | null) {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

function getRoleClass(role: string) {
  switch (role) {
    case 'ADMIN':
      return 'role-admin'
    case 'MANAGER':
      return 'role-manager'
    case 'STAFF':
      return 'role-staff'
    default:
      return 'role-user'
  }
}
</script>

<style scoped>
.users-page {
  padding: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.875rem;
  font-weight: bold;
  color: #111827;
}

.loading-state, .error-state {
  text-align: center;
  padding: 3rem;
}

.spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #dc2626;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #2563eb;
}

.stat-label {
  color: #6b7280;
  margin-top: 0.5rem;
}

.filters-section {
  margin-bottom: 1.5rem;
}

.search-input {
  width: 100%;
  max-width: 400px;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.table-container {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.users-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.table-row:hover {
  background: #f9fafb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  background: #2563eb;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.user-name {
  font-weight: 500;
  color: #111827;
}

.user-username {
  font-size: 0.875rem;
  color: #6b7280;
}

.role-admin {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-manager {
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-staff {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-user {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-inactive {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
}

.action-btn.edit {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.delete {
  background: #fee2e2;
  color: #dc2626;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 500px;
  margin: 1rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
}

.modal-form {
  padding: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox {
  width: 1rem;
  height: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-primary {
  background: #2563eb;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #d1d5db;
}
</style> 