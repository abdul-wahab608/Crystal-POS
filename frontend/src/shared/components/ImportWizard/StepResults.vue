<template>
  <div class="step-results">
    <!-- Success State -->
    <div v-if="!store.error" class="results-success">
      <div class="success-icon-wrapper">
        <svg class="success-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      
      <h2 class="success-title">Import Complete!</h2>
      <p class="success-subtitle">
        Successfully imported {{ store.importResult?.success_count || 0 }} records
      </p>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card success">
          <span class="stat-value">{{ store.importResult?.success_count || 0 }}</span>
          <span class="stat-label">Created</span>
        </div>
        <div class="stat-card" v-if="store.importResult?.duplicate_count">
          <span class="stat-value">{{ store.importResult.duplicate_count }}</span>
          <span class="stat-label">Skipped (Duplicates)</span>
        </div>
        <div class="stat-card error" v-if="store.importResult?.error_count">
          <span class="stat-value">{{ store.importResult.error_count }}</span>
          <span class="stat-label">Failed</span>
        </div>
      </div>

      <!-- Session Info -->
      <div class="session-info" v-if="store.importResult?.session_id">
        <div class="session-header">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Import Session Saved</span>
        </div>
        <p class="session-text">
          You can undo this import within 7 days from the Import History page.
        </p>
      </div>

      <!-- Errors List -->
      <div v-if="store.importResult?.errors?.length" class="errors-section">
        <h3 class="errors-title">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Some rows had errors
        </h3>
        <div class="errors-list">
          <div v-for="(err, idx) in displayedErrors" :key="idx" class="error-item">
            <span class="error-row">Row {{ err.row }}</span>
            <span class="error-message">{{ err.message }}</span>
          </div>
          <p v-if="remainingErrors > 0" class="errors-more">
            + {{ remainingErrors }} more errors
          </p>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="results-error">
      <div class="error-icon-wrapper">
        <svg class="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      
      <h2 class="error-title">Import Failed</h2>
      <p class="error-subtitle">{{ store.error }}</p>
      
      <button @click="$emit('back')" class="btn-retry">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Try Again
      </button>
    </div>

    <!-- Footer -->
    <div class="step-footer">
      <button @click="goToHistory" class="btn-secondary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        View Import History
      </button>
      <div class="footer-right">
        <button @click="startNew" class="btn-outline">
          Import More
        </button>
        <button @click="finish" class="btn-primary">
          Done
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useImportStore } from '../../stores/import'

const emit = defineEmits<{
  close: []
  restart: []
  back: []
}>()

const router = useRouter()
const store = useImportStore()

const displayedErrors = computed(() => {
  return store.importResult?.errors?.slice(0, 5) || []
})

const remainingErrors = computed(() => {
  const total = store.importResult?.errors?.length || 0
  return Math.max(0, total - 5)
})

function goToHistory() {
  router.push('/import-history')
  emit('close')
}

function startNew() {
  store.resetWizard()
  emit('restart')
}

function finish() {
  emit('close')
}
</script>

<style scoped>
.step-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem 0;
}

.results-success,
.results-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 100%;
}

.success-icon-wrapper {
  width: 80px;
  height: 80px;
  background: #dcfce7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.success-icon {
  width: 48px;
  height: 48px;
  color: #22c55e;
}

.error-icon-wrapper {
  width: 80px;
  height: 80px;
  background: #fef2f2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.error-icon {
  width: 48px;
  height: 48px;
  color: #ef4444;
}

.success-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.success-subtitle {
  color: #6b7280;
  margin: 0.5rem 0 0;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ef4444;
  margin: 0;
}

.error-subtitle {
  color: #6b7280;
  margin: 0.5rem 0 1.5rem;
}

.stats-grid {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 2rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  min-width: 100px;
}

.stat-card.success {
  background: #f0fdf4;
  border-color: #22c55e;
}

.stat-card.error {
  background: #fef2f2;
  border-color: #ef4444;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.session-info {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  max-width: 400px;
}

.session-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #1e40af;
}

.session-text {
  font-size: 0.875rem;
  color: #3b82f6;
  margin: 0.5rem 0 0;
}

.errors-section {
  margin-top: 1.5rem;
  width: 100%;
  max-width: 500px;
  text-align: left;
}

.errors-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #b45309;
  margin: 0 0 0.75rem;
}

.errors-list {
  background: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  padding: 0.75rem;
}

.error-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #fde68a;
  font-size: 0.875rem;
}

.error-item:last-child {
  border-bottom: none;
}

.error-row {
  font-weight: 500;
  color: #92400e;
  flex-shrink: 0;
}

.error-message {
  color: #b45309;
}

.errors-more {
  font-size: 0.75rem;
  color: #92400e;
  margin: 0.5rem 0 0;
  font-style: italic;
}

.btn-retry {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: white;
  color: #ef4444;
  font-weight: 500;
  border: 1px solid #ef4444;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-retry:hover {
  background: #fef2f2;
}

.step-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
  margin-top: auto;
}

.footer-right {
  display: flex;
  gap: 0.75rem;
}

.btn-primary {
  padding: 0.75rem 1.25rem;
  background: #3b82f6;
  color: white;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.25rem;
  background: white;
  color: #374151;
  font-weight: 500;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.btn-outline {
  padding: 0.75rem 1.25rem;
  background: white;
  color: #3b82f6;
  font-weight: 500;
  border: 1px solid #3b82f6;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: #eff6ff;
}
</style>
