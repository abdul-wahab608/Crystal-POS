<template>
  <div class="modal-card">
    <h2 class="modal-title">{{ material ? 'Edit Raw Material' : 'Add Raw Material' }}</h2>
    <form @submit.prevent="submit">
      <div class="form-group">
        <label for="rm-name">Name *</label>
        <input id="rm-name" v-model="form.name" type="text" class="form-input" required />
      </div>
      <div class="form-group">
        <label for="rm-unit">Unit *</label>
        <SearchableSelect
          id="rm-unit"
          :modelValue="form.unit || null"
          :options="unitOptions"
          placeholder="Select a unit"
          required
          @update:modelValue="value => form.unit = value ? String(value) : ''"
        />
      </div>
      <div class="form-group">
        <label for="rm-reorder">Reorder level ({{ form.unit || 'unit' }})</label>
        <input id="rm-reorder" v-model.number="form.reorder_level" type="number" min="0" step="0.01" class="form-input" />
      </div>
      <div v-if="!material" class="form-group">
        <label for="rm-opening">Opening quantity ({{ form.unit || 'unit' }})</label>
        <input id="rm-opening" v-model.number="form.quantity" type="number" min="0" step="0.01" class="form-input" />
      </div>
      <p v-if="error" class="form-error">{{ error }}</p>
      <div class="form-actions">
        <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Saving...' : 'Save' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import { useUnitsStore } from '../../../shared/stores/units'
import { useRawMaterialsStore } from '../stores/raw_materials'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { errorMessageOf } from '../utils/errorMessage'
import type { RawMaterial } from '../types'

const props = defineProps<{ material?: RawMaterial | null }>()
const emit = defineEmits<{ success: []; cancel: [] }>()

const unitsStore = useUnitsStore()
const materialsStore = useRawMaterialsStore()

const form = reactive({
  name: props.material?.name ?? '',
  unit: props.material?.unit ?? '',
  reorder_level: Number(props.material?.reorder_level ?? 0),
  quantity: 0,
})
const saving = ref(false)
const error = ref('')

const unitOptions = computed(() => unitsStore.unitOptions)

onMounted(() => {
  unitsStore.fetchUnits().catch(() => {
    error.value = 'Could not load units.'
  })
})

async function submit() {
  error.value = ''
  if (!form.unit) {
    error.value = 'Choose a unit.'
    return
  }
  const payload = props.material
    ? { name: form.name, unit: form.unit, reorder_level: form.reorder_level }
    : { name: form.name, unit: form.unit, reorder_level: form.reorder_level, quantity: form.quantity }
  saving.value = true
  try {
    await acceptQueued(() => (
      props.material
        ? materialsStore.updateMaterial(props.material.id, payload)
        : materialsStore.createMaterial(payload)
    ))
    emit('success')
  } catch (e) {
    error.value = errorMessageOf(e)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.modal-card { background: white; border-radius: 0.5rem; padding: 1.5rem; width: min(440px, 92vw); }
.modal-title { font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; }
.form-group { margin-bottom: 0.875rem; }
.form-group label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
.form-input { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; }
.form-error { color: #b91c1c; font-size: 0.875rem; margin-bottom: 0.75rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
.btn-primary:disabled { opacity: 0.6; }
</style>
