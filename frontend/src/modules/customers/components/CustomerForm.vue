<template>
  <form class="customer-form" @submit.prevent="submit">
    <div class="field-row">
      <div class="field">
        <label for="cust-name">Name</label>
        <input id="cust-name" v-model.trim="form.name" type="text" class="form-input" maxlength="255" required />
      </div>
      <div class="field">
        <label for="cust-phone">Phone</label>
        <input id="cust-phone" v-model.trim="form.phone" type="tel" class="form-input" maxlength="20" />
      </div>
    </div>
    <div class="field">
      <label for="cust-address">Address</label>
      <textarea id="cust-address" v-model.trim="form.address" class="form-input" rows="2" />
    </div>
    <div class="field-row">
      <div class="field">
        <label for="cust-city">City</label>
        <input id="cust-city" v-model.trim="form.city" type="text" class="form-input" maxlength="255" />
      </div>
      <div class="field">
        <label for="cust-type">Customer type</label>
        <select id="cust-type" v-model="form.customer_type" class="form-input">
          <option value="REGULAR">Regular</option>
          <option value="WALK_IN">Walk-in</option>
        </select>
      </div>
    </div>
    <label class="check">
      <input v-model="form.is_active" type="checkbox" />
      Active
    </label>

    <p v-if="submitError" class="form-error">{{ submitError }}</p>

    <div class="actions">
      <button type="button" class="secondary-btn" @click="emit('cancel')">Cancel</button>
      <button type="submit" class="primary-btn" :disabled="submitting">
        {{ submitting ? 'Saving...' : isEdit ? 'Save changes' : 'Add customer' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useCustomersStore } from '../stores/customers'
import { useToastStore } from '../../../shared/stores/toast'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { apiErrorMessage } from '../../../shared/utils/apiError'
import type { Customer, CustomerRequest } from '../types'

const props = defineProps<{ customer?: Customer | null }>()
const emit = defineEmits<{
  saved: [customer: Customer | undefined]
  cancel: []
}>()

const customersStore = useCustomersStore()
const toast = useToastStore()

const isEdit = computed(() => !!props.customer)
const submitting = ref(false)
const submitError = ref('')

const form = reactive<CustomerRequest>({
  name: props.customer?.name ?? '',
  phone: props.customer?.phone ?? '',
  address: props.customer?.address ?? '',
  city: props.customer?.city ?? '',
  customer_type: props.customer?.customer_type ?? 'REGULAR',
  is_active: props.customer?.is_active ?? true,
})

const submit = async () => {
  submitting.value = true
  submitError.value = ''
  try {
    const saved = await acceptQueued(() => (props.customer
      ? customersStore.updateCustomer(props.customer.id, form)
      : customersStore.createCustomer(form)))
    toast.success(isEdit.value ? 'Customer updated' : 'Customer added', form.name)
    emit('saved', saved)
  } catch (e) {
    submitError.value = apiErrorMessage(e)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.customer-form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.field-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); gap: 1rem; }
.check { display: flex; align-items: center; gap: 0.5rem; }
.form-error { color: #b42318; margin: 0; }
.actions { display: flex; justify-content: flex-end; gap: 0.5rem; }
</style>
