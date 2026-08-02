<template>
  <div class="import-history-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Import History</h1>
        <p class="page-subtitle">View and manage your past imports. You can undo imports within 7 days.</p>
      </div>
      <button @click="refresh" class="btn-refresh" :disabled="loading">
        <svg :class="['w-5 h-5', { spinning: loading }]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <label class="filter-label">Entity Type</label>
        <select v-model="filters.entityType" class="filter-select">
          <option value="">All Types</option>
          <option v-for="entity in importableEntities" :key="entity.value" :value="entity.value">
            {{ entity.label }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <label class="filter-label">Status</label>
        <select v-model="filters.status" class="filter-select">
          <option value="">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="undone">Undone</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="filter-label">Date Range</label>
        <select v-model="filters.dateRange" class="filter-select">
          <option value="all">All Time</option>
          <option value="7days">Last 7 Days</option>
          <option value="30days">Last 30 Days</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading import history...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="sessions.length === 0" class="empty-state">
      <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3>No imports found</h3>
      <p>You haven't imported any data yet, or no imports match your filters.</p>
    </div>

    <!-- Sessions Table -->
    <div v-else class="table-container">
      <table class="sessions-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Entity Type</th>
            <th>File</th>
            <th>Records</th>
            <th>Status</th>
            <th>Imported By</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="session in filteredSessions" :key="session.id">
            <td>
              <span class="date-main">{{ formatDate(session.created_at) }}</span>
              <span class="date-time">{{ formatTime(session.created_at) }}</span>
            </td>
            <td>
              <span class="entity-badge">{{ getEntityLabel(session.entity_type) }}</span>
            </td>
            <td class="file-cell">
              {{ session.file_name || '-' }}
            </td>
            <td>
              <span class="records-count">{{ session.success_count }}</span>
              <span v-if="session.error_count > 0" class="error-count">({{ session.error_count }} errors)</span>
            </td>
            <td>
              <span :class="['status-badge', session.status]">
                {{ session.status_display || session.status }}
              </span>
            </td>
            <td>
              {{ session.user_name || '-' }}
            </td>
            <td>
              <button 
                v-if="canUndo(session)"
                @click="undoImport(session)"
                class="btn-undo"
                :disabled="undoing === session.id"
              >
                <svg v-if="undoing === session.id" class="w-4 h-4 spinning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span v-else>Undo</span>
              </button>
              <span v-else-if="session.status === 'undone'" class="text-muted">
                Already undone
              </span>
              <span v-else class="text-muted">
                Expired
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-message">
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../shared/api/axios'
import { useToastStore } from '../shared/stores/toast'
import { getImportableEntities, IMPORT_CONFIGS } from '../shared/constants/importFields'

interface ImportSession {
  id: number
  entity_type: string
  entity_type_display: string
  file_name?: string
  total_rows: number
  success_count: number
  error_count: number
  duplicate_count: number
  status: 'completed' | 'undone' | 'failed'
  status_display: string
  created_at: string
  undone_at: string | null
  undo_expires_at: string
  can_undo: boolean
  undo_time_remaining: string | null
  user: number
  user_name: string
  imported_ids?: number[]
  errors?: any[]
}

const toast = useToastStore()

const loading = ref(false)
const undoing = ref<number | null>(null)
const error = ref('')
const sessions = ref<ImportSession[]>([])

const filters = ref({
  entityType: '',
  status: '',
  dateRange: 'all'
})

const importableEntities = getImportableEntities()

const filteredSessions = computed(() => {
  let result = [...sessions.value]
  
  if (filters.value.entityType) {
    result = result.filter(s => s.entity_type === filters.value.entityType)
  }
  
  if (filters.value.status) {
    result = result.filter(s => s.status === filters.value.status)
  }
  
  if (filters.value.dateRange !== 'all') {
    const now = new Date()
    const days = filters.value.dateRange === '7days' ? 7 : 30
    const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
    result = result.filter(s => new Date(s.created_at) >= cutoff)
  }
  
  return result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

function getEntityLabel(entityType: string): string {
  return IMPORT_CONFIGS[entityType]?.displayName || entityType
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

function canUndo(session: ImportSession): boolean {
  return session.can_undo
}

async function fetchSessions() {
  loading.value = true
  error.value = ''
  
  try {
    const response = await api.get('/api/import-sessions/')
    sessions.value = response.data.results || response.data || []
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to load import history'
    console.error('Failed to fetch import sessions:', e)
  } finally {
    loading.value = false
  }
}

async function undoImport(session: ImportSession) {
  if (!confirm(`Are you sure you want to undo this import? This will delete ${session.success_count} records.`)) {
    return
  }

  undoing.value = session.id
  
  try {
    await api.post(`/api/import-sessions/${session.id}/undo/`)
    toast.success('Import Undone', 'The imported records have been deleted.')
    await fetchSessions()
  } catch (e: any) {
    toast.error('Undo Failed', e.response?.data?.error || 'Failed to undo import')
  } finally {
    undoing.value = null
  }
}

function refresh() {
  fetchSessions()
}

onMounted(() => {
  fetchSessions()
})
</script>

<style scoped>
.import-history-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.page-subtitle {
  color: #6b7280;
  margin: 0.25rem 0 0;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  min-width: 150px;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 4rem 0;
  color: #6b7280;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 2rem;
  text-align: center;
  background: #f9fafb;
  border-radius: 12px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.empty-state p {
  color: #6b7280;
  margin: 0.5rem 0 0;
}

.table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.sessions-table {
  width: 100%;
  border-collapse: collapse;
}

.sessions-table th {
  background: #f9fafb;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #6b7280;
  border-bottom: 1px solid #e5e7eb;
}

.sessions-table td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.sessions-table tr:last-child td {
  border-bottom: none;
}

.sessions-table tr:hover {
  background: #f9fafb;
}

.date-main {
  display: block;
  font-weight: 500;
  color: #111827;
}

.date-time {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
}

.entity-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
}

.file-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.records-count {
  font-weight: 600;
  color: #111827;
}

.error-count {
  font-size: 0.75rem;
  color: #dc2626;
  margin-left: 0.25rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
  text-transform: capitalize;
}

.status-badge.completed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.undone {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.failed {
  background: #fef3c7;
  color: #92400e;
}

.btn-undo {
  padding: 0.375rem 0.75rem;
  background: white;
  color: #dc2626;
  border: 1px solid #dc2626;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-undo:hover:not(:disabled) {
  background: #fef2f2;
}

.btn-undo:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.text-muted {
  font-size: 0.875rem;
  color: #9ca3af;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 1rem;
}
</style>
