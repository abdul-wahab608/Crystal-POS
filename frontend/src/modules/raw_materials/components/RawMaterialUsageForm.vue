<template>
  <div class="modal-card">
    <h2 class="modal-title">Record Usage</h2>
    <form @submit.prevent="submit">
      <div class="form-group">
        <label for="usage-material">Raw material *</label>
        <SearchableSelect
          id="usage-material"
          :modelValue="form.raw_material"
          :options="materialOptions"
          required
          @update:modelValue="value => form.raw_material = value === null ? null : Number(value)"
        />
      </div>
      <div class="form-group">
        <label for="usage-qty">Quantity used{{ unitSuffix }} *</label>
        <input id="usage-qty" v-model.number="form.quantity_used" type="number" min="0.01" step="0.01" class="form-input" required />
      </div>
      <div class="form-group">
        <label for="usage-ref">Reference</label>
        <input id="usage-ref" v-model="form.reference" type="text" class="form-input" placeholder="e.g. Batch 12" />
      </div>
      <div class="form-group">
        <label for="usage-notes">Notes</label>
        <textarea id="usage-notes" v-model="form.notes" rows="2" class="form-input"></textarea>
      </div>
      <p v-if="error" class="form-error">{{ error }}</p>
      <div class="form-actions">
        <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Saving...' : 'Record usage' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import { useRawMaterialsStore } from '../stores/raw_materials'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { errorMessageOf } from '../utils/errorMessage'
import type { RawMaterial } from '../types'

const props = defineProps<{ materials: RawMaterial[]; initialMaterialId?: number | null }>()
const emit = defineEmits<{ success: []; cancel: [] }>()

const materialsStore = useRawMaterialsStore()

const form = reactive({
  raw_material: (props.initialMaterialId ?? null) as number | null,
  quantity_used: 0,
  reference: '',
  notes: '',
})
const saving = ref(false)
const error = ref('')

const materialOptions = computed(() => props.materials.map(material => ({
  value: material.id,
  label: `${material.name} (${material.unit}) - ${Number(material.quantity).toFixed(2)} on hand`,
})))

const unitSuffix = computed(() => {
  const material = props.materials.find(m => m.id === form.raw_material)
  return material ? ` (${material.unit})` : ''
})

async function submit() {
  error.value = ''
  if (form.raw_material === null) {
    error.value = 'Choose a raw material.'
    return
  }
  saving.value = true
  try {
    await acceptQueued(() => materialsStore.createUsage({
      raw_material: form.raw_material as number,
      quantity_used: form.quantity_used,
      reference: form.reference,
      notes: form.notes,
    }))
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
