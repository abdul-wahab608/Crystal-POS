<template>
  <div class="import-wizard-overlay" @click.self="handleClose">
    <div class="import-wizard">
      <!-- Header -->
      <div class="wizard-header">
        <h2 class="wizard-title">
          <svg class="w-6 h-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Import {{ entityLabel }}
        </h2>
        <button @click="handleClose" class="close-btn">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Steps Indicator -->
      <div class="wizard-steps">
        <div 
          v-for="step in steps" 
          :key="step.number"
          :class="['step', { active: store.currentStep === step.number, completed: store.currentStep > step.number }]"
        >
          <div class="step-number">
            <svg v-if="store.currentStep > step.number" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span v-else>{{ step.number }}</span>
          </div>
          <div class="step-info">
            <div class="step-title">{{ step.title }}</div>
            <div class="step-desc">{{ step.description }}</div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="wizard-content">
        <StepUpload 
          v-if="store.currentStep === 1" 
          :entity-type="entityType"
          @next="store.currentStep = 2"
        />
        <StepMapping 
          v-else-if="store.currentStep === 2"
          @back="store.currentStep = 1"
          @next="goToPreview"
        />
        <StepPreview 
          v-else-if="store.currentStep === 3"
          @back="store.currentStep = 2"
          @import="runImport"
        />
        <StepResults 
          v-else-if="store.currentStep === 4"
          @close="handleClose"
          @undo="handleUndo"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useImportStore } from '../../stores/import'
import { useUnitsStore } from '../../stores/units'
import { useToastStore } from '../../stores/toast'
import { IMPORT_CONFIGS } from '../../constants/importFields'
import { WIZARD_STEPS } from './types'
import StepUpload from './StepUpload.vue'
import StepMapping from './StepMapping.vue'
import StepPreview from './StepPreview.vue'
import StepResults from './StepResults.vue'

const props = defineProps<{
  entityType?: string
}>()

const emit = defineEmits<{
  close: []
  imported: []
}>()

const store = useImportStore()
const unitsStore = useUnitsStore()
const toast = useToastStore()

const steps = WIZARD_STEPS

const entityLabel = computed(() => {
  if (store.entityType) {
    return IMPORT_CONFIGS[store.entityType]?.displayName || store.entityType
  }
  return props.entityType ? IMPORT_CONFIGS[props.entityType]?.displayName || '' : 'Data'
})

onMounted(async () => {
  store.resetWizard()
  if (props.entityType) {
    store.setEntityType(props.entityType)
  }
  
  // Load units for mapping
  try {
    await unitsStore.fetchUnits()
  } catch (e) {
    // Silent fail - units will be created on import if needed
  }
})

onUnmounted(() => {
  store.resetWizard()
})

function handleClose() {
  if (store.importing) {
    if (!confirm('Import is in progress. Are you sure you want to cancel?')) {
      return
    }
  }
  store.resetWizard()
  emit('close')
}

function goToPreview() {
  store.validatePreviewData()
  store.currentStep = 3
}

async function runImport() {
  await store.runImport()
  if (store.importResult && store.importResult.success_count > 0) {
    emit('imported')
  }
}

async function handleUndo() {
  if (!store.lastSessionId) return
  
  try {
    await store.undoImport(store.lastSessionId)
    toast.success('Import Undone', 'All imported records have been deleted.')
    emit('imported') // Refresh parent data
  } catch (e: any) {
    toast.error('Undo Failed', e.message)
  }
}
</script>

<style scoped>
.import-wizard-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.import-wizard {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.wizard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.wizard-title {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  padding: 0.5rem;
  border-radius: 8px;
  color: #6b7280;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.wizard-steps {
  display: flex;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  gap: 0.5rem;
}

.step {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: #f9fafb;
  transition: all 0.2s;
}

.step.active {
  background: #eff6ff;
  border: 1px solid #3b82f6;
}

.step.completed {
  background: #f0fdf4;
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  background: #e5e7eb;
  color: #6b7280;
  flex-shrink: 0;
}

.step.active .step-number {
  background: #3b82f6;
  color: white;
}

.step.completed .step-number {
  background: #22c55e;
  color: white;
}

.step-info {
  min-width: 0;
}

.step-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.step-desc {
  font-size: 0.75rem;
  color: #9ca3af;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.wizard-content {
  flex: 1;
  overflow: auto;
  padding: 1.5rem;
}

@media (max-width: 768px) {
  .wizard-steps {
    flex-wrap: wrap;
  }
  
  .step {
    flex: 1 1 45%;
  }
  
  .step-desc {
    display: none;
  }
}
</style>
