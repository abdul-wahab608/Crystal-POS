<template>
  <div class="modal-card">
    <div class="modal-header">
      <h2 class="modal-title">New Purchase</h2>
      <span class="muted">Date: {{ today }}</span>
    </div>

    <form @submit.prevent="submit">
      <div class="top-grid">
        <div class="form-group">
          <label for="purchase-vendor">Vendor *</label>
          <SearchableSelect
            id="purchase-vendor"
            :modelValue="vendorId"
            :options="vendorOptions"
            placeholder="Select a vendor"
            required
            @update:modelValue="value => vendorId = value === null ? null : Number(value)"
          />
        </div>
        <div class="form-group">
          <label for="purchase-invoice">Vendor invoice number</label>
          <input id="purchase-invoice" v-model="invoiceNumber" type="text" class="form-input" />
        </div>
      </div>

      <div class="lines-header">
        <h3>Lines</h3>
        <button type="button" class="btn-secondary small" @click="lines.push(emptyLine())">Add line</button>
      </div>

      <div v-for="(line, index) in lines" :key="index" class="line-card">
        <div class="line-top">
          <span class="line-number">Line {{ index + 1 }}</span>
          <div class="kind-toggle" role="group" aria-label="Line type">
            <button type="button" :class="{ active: line.kind === 'raw' }" @click="setKind(line, 'raw')">Raw material</button>
            <button type="button" :class="{ active: line.kind === 'product' }" @click="setKind(line, 'product')">Product</button>
          </div>
          <button type="button" class="link-btn danger" :disabled="lines.length === 1" @click="lines.splice(index, 1)">Remove</button>
        </div>

        <div class="line-fields">
          <template v-if="line.kind === 'raw'">
            <div class="field wide">
              <label>Raw material *</label>
              <SearchableSelect
                :modelValue="line.raw_material"
                :options="rawOptions"
                placeholder="Select a raw material"
                @update:modelValue="value => line.raw_material = value === null ? null : Number(value)"
              />
            </div>
          </template>
          <template v-else>
            <div class="field wide">
              <label>Product *</label>
              <SearchableSelect
                :modelValue="line.product"
                :options="productOptions"
                placeholder="Select a product"
                @update:modelValue="value => setProduct(line, value)"
              />
            </div>
            <div class="field">
              <label>Size range *</label>
              <SearchableSelect
                :modelValue="line.size_range"
                :options="sizeOptions(line)"
                placeholder="Size"
                @update:modelValue="value => line.size_range = value === null ? null : Number(value)"
              />
            </div>
            <div class="field">
              <label>Color *</label>
              <SearchableSelect
                :modelValue="line.color"
                :options="colorOptions(line)"
                placeholder="Color"
                @update:modelValue="value => line.color = value === null ? null : Number(value)"
              />
            </div>
          </template>

          <div class="field">
            <label>Quantity{{ unitSuffix(line) }} *</label>
            <input v-model.number="line.quantity" type="number" min="0.01" step="0.01" class="form-input" />
          </div>
          <div class="field">
            <label>Unit cost *</label>
            <input v-model.number="line.unit_cost" type="number" min="0" step="0.01" class="form-input" />
          </div>
          <div class="field">
            <label>Subtotal</label>
            <div class="subtotal">{{ lineSubtotal(line).toFixed(2) }}</div>
          </div>
        </div>
      </div>

      <div class="total-row">
        <span>Total</span>
        <strong>{{ purchaseTotal(lines).toFixed(2) }}</strong>
      </div>

      <ul v-if="problems.length" class="problem-list">
        <li v-for="problem in problems" :key="problem">{{ problem }}</li>
      </ul>
      <p v-if="serverError" class="form-error">{{ serverError }}</p>

      <div class="form-actions">
        <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Saving...' : 'Save purchase' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import { useVendorsStore } from '../../vendors/stores/vendors'
import { usePurchasesStore } from '../stores/purchases'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { errorMessageOf } from '../../raw_materials/utils/errorMessage'
import {
  emptyLine,
  lineProblems,
  lineSubtotal,
  purchaseTotal,
  toPurchaseItem,
  sizeRangeOptionsFor,
  colorOptionsFor,
  type LineKind,
  type PurchaseLineDraft,
} from '../utils/purchaseLines'
import type { Product } from '../types'

const emit = defineEmits<{ saved: []; cancel: [] }>()

const vendorsStore = useVendorsStore()
const purchasesStore = usePurchasesStore()

const vendorId = ref<number | null>(null)
const invoiceNumber = ref('')
const lines = ref<PurchaseLineDraft[]>([emptyLine('raw')])
const saving = ref(false)
const serverError = ref('')
const problems = ref<string[]>([])
const today = new Date().toLocaleDateString()

const vendorOptions = computed(() => vendorsStore.vendors.map(vendor => ({ value: vendor.id, label: vendor.name })))
const rawOptions = computed(() => purchasesStore.rawMaterials.map(material => ({
  value: material.id,
  label: `${material.name} (${material.unit})`,
})))
const productOptions = computed(() => purchasesStore.products.map(product => ({
  value: product.id,
  label: `${product.name} (${product.unit})`,
})))

function productById(id: number | null): Product | undefined {
  return purchasesStore.products.find(product => product.id === id)
}

function sizeOptions(line: PurchaseLineDraft) {
  return sizeRangeOptionsFor(productById(line.product), purchasesStore.sizeRanges)
    .map(size => ({ value: size.id, label: size.name }))
}

function colorOptions(line: PurchaseLineDraft) {
  return colorOptionsFor(productById(line.product), purchasesStore.colors)
    .map(color => ({ value: color.id, label: color.name }))
}

function unitSuffix(line: PurchaseLineDraft) {
  const unit = line.kind === 'raw'
    ? purchasesStore.rawMaterials.find(material => material.id === line.raw_material)?.unit
    : productById(line.product)?.unit
  return unit ? ` (${unit})` : ''
}

function setKind(line: PurchaseLineDraft, kind: LineKind) {
  line.kind = kind
  line.raw_material = null
  line.product = null
  line.size_range = null
  line.color = null
}

function setProduct(line: PurchaseLineDraft, value: string | number | null) {
  line.product = value === null ? null : Number(value)
  line.size_range = null
  line.color = null
}

function validate(): boolean {
  problems.value = []
  if (vendorId.value === null) problems.value.push('Choose a vendor.')
  if (!lines.value.length) problems.value.push('Add at least one line.')
  lines.value.forEach((line, index) => {
    lineProblems(line).forEach(problem => problems.value.push(`Line ${index + 1}: ${problem}`))
  })
  return problems.value.length === 0
}

async function submit() {
  serverError.value = ''
  if (!validate()) return
  saving.value = true
  try {
    await acceptQueued(() => purchasesStore.createPurchase({
      vendor: vendorId.value as number,
      invoice_number: invoiceNumber.value.trim(),
      items: lines.value.map(toPurchaseItem),
    }))
    emit('saved')
  } catch (e) {
    serverError.value = errorMessageOf(e)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    await Promise.all([vendorsStore.fetchVendors(), purchasesStore.fetchLookups()])
  } catch (e) {
    serverError.value = errorMessageOf(e)
  }
})
</script>

<style scoped>
.modal-card { background: white; border-radius: 0.5rem; padding: 1.5rem; width: min(900px, 96vw); max-height: 90vh; overflow: auto; }
.modal-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1rem; }
.modal-title { font-size: 1.25rem; font-weight: 600; }
.muted { color: #6b7280; font-size: 0.875rem; }
.top-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-group label, .field label { display: block; font-size: 0.8125rem; font-weight: 500; margin-bottom: 0.25rem; color: #374151; }
.form-input { width: 100%; padding: 0.5rem 0.625rem; border: 1px solid #d1d5db; border-radius: 0.375rem; }
.lines-header { display: flex; justify-content: space-between; align-items: center; margin: 1rem 0 0.5rem; }
.lines-header h3 { font-size: 1rem; font-weight: 600; }
.line-card { border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 0.75rem; }
.line-top { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
.line-number { font-weight: 600; font-size: 0.875rem; }
.kind-toggle { display: inline-flex; border: 1px solid #d1d5db; border-radius: 0.375rem; overflow: hidden; }
.kind-toggle button { padding: 0.25rem 0.75rem; background: white; border: none; cursor: pointer; font-size: 0.8125rem; }
.kind-toggle button.active { background: #2563eb; color: white; }
.line-top .link-btn { margin-left: auto; }
.line-fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.5rem; align-items: end; }
.field.wide { grid-column: span 2; }
.subtotal { padding: 0.5rem 0; font-weight: 600; }
.total-row { display: flex; justify-content: flex-end; gap: 1rem; font-size: 1.125rem; margin-top: 0.5rem; }
.problem-list { color: #b91c1c; font-size: 0.875rem; margin-top: 0.75rem; padding-left: 1.25rem; }
.form-error { color: #b91c1c; font-size: 0.875rem; margin-top: 0.75rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
.link-btn { background: none; border: none; cursor: pointer; font-size: 0.8125rem; color: #2563eb; }
.link-btn.danger { color: #b91c1c; }
.link-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-secondary.small { padding: 0.25rem 0.75rem; font-size: 0.875rem; }
.btn-primary:disabled { opacity: 0.6; }
@media (max-width: 640px) { .top-grid { grid-template-columns: 1fr; } .field.wide { grid-column: auto; } }
</style>
