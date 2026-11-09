<template>
  <div class="modal-card">
    <h2 class="modal-title">{{ vendor ? 'Edit Vendor' : 'Add Vendor' }}</h2>
    <form @submit.prevent="submit">
      <div class="form-group">
        <label for="vendor-name">Name *</label>
        <input id="vendor-name" v-model="form.name" type="text" class="form-input" required />
      </div>
      <div class="form-group">
        <label for="vendor-contact">Contact person</label>
        <input id="vendor-contact" v-model="form.contact_person" type="text" class="form-input" />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="vendor-phone">Phone</label>
          <input id="vendor-phone" v-model="form.phone" type="text" class="form-input" />
        </div>
        <div class="form-group">
          <label for="vendor-city">City</label>
          <input id="vendor-city" v-model="form.city" type="text" class="form-input" />
        </div>
      </div>
      <div class="form-group">
        <label for="vendor-address">Address</label>
        <textarea id="vendor-address" v-model="form.address" rows="2" class="form-input"></textarea>
      </div>
      <label class="checkbox">
        <input v-model="form.is_active" type="checkbox" />
        Active
      </label>
      <p v-if="error" class="form-error">{{ error }}</p>
      <div class="form-actions">
        <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Saving...' : 'Save' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useVendorsStore } from '../stores/vendors'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { errorMessageOf } from '../../raw_materials/utils/errorMessage'
import type { Vendor } from '../types'

const props = defineProps<{ vendor?: Vendor | null }>()
const emit = defineEmits<{ success: []; cancel: [] }>()

const vendorsStore = useVendorsStore()

const form = reactive({
  name: props.vendor?.name ?? '',
  contact_person: props.vendor?.contact_person ?? '',
  phone: props.vendor?.phone ?? '',
  city: props.vendor?.city ?? '',
  address: props.vendor?.address ?? '',
  is_active: props.vendor?.is_active ?? true,
})
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  saving.value = true
  try {
    await acceptQueued(() => (
      props.vendor
        ? vendorsStore.updateVendor(props.vendor.id, { ...form })
        : vendorsStore.createVendor({ ...form })
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
.modal-card { background: white; border-radius: 0.5rem; padding: 1.5rem; width: min(480px, 94vw); }
.modal-title { font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; }
.form-group { margin-bottom: 0.875rem; flex: 1; }
.form-row { display: flex; gap: 0.75rem; }
.form-group label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
.form-input { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; }
.checkbox { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; }
.form-error { color: #b91c1c; font-size: 0.875rem; margin-top: 0.75rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
.btn-primary:disabled { opacity: 0.6; }
</style>
