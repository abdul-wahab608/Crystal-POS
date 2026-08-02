<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    leave-active-class="transition-all duration-200 ease-in"
    enter-from-class="opacity-0 -translate-y-2"
    enter-to-class="opacity-100 translate-y-0"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 -translate-y-2"
  >
    <div 
      v-if="selectedCount > 0" 
      class="bg-primary-50 border border-primary-200 rounded-lg px-4 py-3 mb-4 flex items-center justify-between shadow-sm"
    >
      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-2">
          <CheckCircleIcon class="h-5 w-5 text-primary-600" />
          <span class="text-sm font-medium text-primary-800">
            {{ selectedCount }} item{{ selectedCount !== 1 ? 's' : '' }} selected
          </span>
        </div>
        <button
          @click="clearSelection"
          class="text-sm text-primary-600 hover:text-primary-800 underline"
        >
          Clear selection
        </button>
      </div>

      <div class="flex items-center space-x-2">
        <!-- Activate Button -->
        <button
          v-if="showActivate"
          @click="handleActivate"
          :disabled="loading"
          class="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <CheckIcon class="h-4 w-4 mr-1.5" />
          Activate
        </button>

        <!-- Deactivate Button -->
        <button
          v-if="showDeactivate"
          @click="handleDeactivate"
          :disabled="loading"
          class="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-yellow-700 bg-yellow-100 hover:bg-yellow-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <XMarkIcon class="h-4 w-4 mr-1.5" />
          Deactivate
        </button>

        <!-- Custom Actions Slot -->
        <slot name="actions" :selected-ids="selectedIds" :loading="loading" />

        <!-- Delete Button -->
        <button
          v-if="showDelete"
          @click="handleDelete"
          :disabled="loading"
          class="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <TrashIcon class="h-4 w-4 mr-1.5" />
          Delete
        </button>
      </div>
    </div>
  </Transition>

  <!-- Delete Confirmation Modal -->
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showDeleteModal" 
        class="fixed inset-0 z-50 overflow-y-auto"
        aria-labelledby="modal-title"
        role="dialog"
        aria-modal="true"
      >
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="showDeleteModal = false"></div>
          
          <div class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:w-full sm:max-w-lg">
            <div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                  <ExclamationTriangleIcon class="h-6 w-6 text-red-600" />
                </div>
                <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                  <h3 class="text-lg font-semibold leading-6 text-gray-900" id="modal-title">
                    Delete {{ selectedCount }} {{ entityLabel }}{{ selectedCount !== 1 ? 's' : '' }}?
                  </h3>
                  <div class="mt-2">
                    <p class="text-sm text-gray-500">
                      Are you sure you want to delete the selected items? This action cannot be undone.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
              <button
                type="button"
                @click="confirmDelete"
                :disabled="loading"
                class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed sm:ml-3 sm:w-auto"
              >
                <span v-if="loading" class="flex items-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Deleting...
                </span>
                <span v-else>Delete</span>
              </button>
              <button
                type="button"
                @click="showDeleteModal = false"
                :disabled="loading"
                class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed sm:mt-0 sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CheckCircleIcon from '@heroicons/vue/24/outline/CheckCircleIcon'
import CheckIcon from '@heroicons/vue/24/outline/CheckIcon'
import XMarkIcon from '@heroicons/vue/24/outline/XMarkIcon'
import TrashIcon from '@heroicons/vue/24/outline/TrashIcon'
import ExclamationTriangleIcon from '@heroicons/vue/24/outline/ExclamationTriangleIcon'
import { useBatchActionsStore } from '../stores/batchActions'

const props = withDefaults(defineProps<{
  entityType: string
  entityLabel?: string
  showActivate?: boolean
  showDeactivate?: boolean
  showDelete?: boolean
}>(), {
  entityLabel: 'item',
  showActivate: true,
  showDeactivate: true,
  showDelete: true,
})

const emit = defineEmits<{
  (e: 'action-complete', action: string, result: any): void
}>()

const batchStore = useBatchActionsStore()

const showDeleteModal = ref(false)

const selectedIds = computed(() => batchStore.getSelectedIds(props.entityType))
const selectedCount = computed(() => batchStore.selectedCount(props.entityType))
const loading = computed(() => batchStore.loading)

function clearSelection() {
  batchStore.clearSelection(props.entityType)
}

function handleDelete() {
  showDeleteModal.value = true
}

async function confirmDelete() {
  const result = await batchStore.bulkDelete(props.entityType)
  showDeleteModal.value = false
  emit('action-complete', 'delete', result)
}

async function handleActivate() {
  const result = await batchStore.bulkActivate(props.entityType)
  emit('action-complete', 'activate', result)
}

async function handleDeactivate() {
  const result = await batchStore.bulkDeactivate(props.entityType)
  emit('action-complete', 'deactivate', result)
}
</script>
