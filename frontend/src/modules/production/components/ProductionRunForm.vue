<template>
  <div class="modal-card">
    <h2 class="modal-title">New Production Run</h2>
    <p class="muted">Raw materials are consumed and finished variants are added to stock on save. Only existing size and color variants can be produced; add new ones on the Products page.</p>

    <form @submit.prevent="submit">
      <div class="top-grid">
        <div class="form-group">
          <label for="run-ref">Reference</label>
          <input id="run-ref" v-model="reference" type="text" class="form-input" placeholder="e.g. Batch 14" />
        </div>
        <div class="form-group">
          <label for="run-notes">Notes</label>
          <input id="run-notes" v-model="notes" type="text" class="form-input" />
        </div>
      </div>

      <div class="section-header">
        <h3>Outputs (finished product)</h3>
        <button type="button" class="btn-secondary small" @click="outputs.push(emptyOutput())">Add output</button>
      </div>
      <div v-for="(output, index) in outputs" :key="index" class="line-card">
        <div class="line-fields">
          <div class="field wide">
            <label>Product *</label>
            <SearchableSelect
              :modelValue="output.product"
              :options="productOptions"
              placeholder="Select a product"
              @update:modelValue="value => setProduct(output, value)"
            />
          </div>
          <div class="field">
            <label>Size range *</label>
            <SearchableSelect
              :modelValue="output.size_range"
              :options="sizeOptions(output)"
              placeholder="Size"
              @update:modelValue="value => setSize(output, value)"
            />
          </div>
          <div class="field">
            <label>Color *</label>
            <SearchableSelect
              :modelValue="output.color"
              :options="colorOptions(output)"
              placeholder="Color"
              @update:modelValue="value => output.color = value === null ? null : Number(value)"
            />
          </div>
          <div class="field">
            <label>Quantity{{ unitSuffix(output.product) }} *</label>
            <input v-model.number="output.quantity" type="number" min="0.01" step="0.01" class="form-input" />
          </div>
          <button type="button" class="link-btn danger" :disabled="outputs.length === 1" @click="outputs.splice(index, 1)">Remove</button>
        </div>
      </div>

      <div class="section-header">
        <h3>Inputs (raw materials used)</h3>
        <button type="button" class="btn-secondary small" @click="inputs.push(emptyInput())">Add input</button>
      </div>
      <p v-if="!inputs.length" class="form-error">A production run must consume at least one raw material. Add an input.</p>
      <div v-for="(input, index) in inputs" :key="index" class="line-card">
        <div class="line-fields">
          <div class="field wide">
            <label>Raw material *</label>
            <SearchableSelect
              :modelValue="input.raw_material"
              :options="rawOptions"
              placeholder="Select a raw material"
              @update:modelValue="value => input.raw_material = value === null ? null : Number(value)"
            />
          </div>
          <div class="field">
            <label>Quantity{{ rawUnitSuffix(input.raw_material) }} *</label>
            <input v-model.number="input.quantity" type="number" min="0.01" step="0.01" class="form-input" />
          </div>
          <button type="button" class="link-btn danger" @click="inputs.splice(index, 1)">Remove</button>
        </div>
      </div>

      <ul v-if="problems.length" class="problem-list">
        <li v-for="problem in problems" :key="problem">{{ problem }}</li>
      </ul>
      <p v-if="serverError" class="form-error">{{ serverError }}</p>

      <div class="form-actions">
        <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="saving || !inputs.length">{{ saving ? 'Saving...' : 'Save run' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import { useProductionStore } from '../stores/production'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { errorMessageOf } from '../../raw_materials/utils/errorMessage'
import { colorOptionsFor, outputProblems, resolveVariant, sizeOptionsFor, type OutputDraft } from '../utils/outputLines'
import type { Product } from '../types'

const emit = defineEmits<{ saved: []; cancel: [] }>()

const productionStore = useProductionStore()

interface InputDraft {
  raw_material: number | null
  quantity: number | null
}

function emptyOutput(): OutputDraft {
  return { product: null, size_range: null, color: null, quantity: null }
}

function emptyInput(): InputDraft {
  return { raw_material: null, quantity: null }
}

const reference = ref('')
const notes = ref('')
const outputs = ref<OutputDraft[]>([emptyOutput()])
const inputs = ref<InputDraft[]>([])
const saving = ref(false)
const serverError = ref('')
const problems = ref<string[]>([])

const productOptions = computed(() => productionStore.products
  .filter(product => product.variants.length > 0)
  .map(product => ({ value: product.id, label: `${product.name} (${product.unit})` })))
const rawOptions = computed(() => productionStore.rawMaterials.map(material => ({
  value: material.id,
  label: `${material.name} (${material.unit}) - ${Number(material.quantity).toFixed(2)} on hand`,
})))

function productById(id: number | null): Product | undefined {
  return productionStore.products.find(product => product.id === id)
}

function sizeOptions(output: OutputDraft) {
  return sizeOptionsFor(productById(output.product))
}

function colorOptions(output: OutputDraft) {
  return colorOptionsFor(productById(output.product), output.size_range)
}

function unitSuffix(productId: number | null) {
  const unit = productById(productId)?.unit
  return unit ? ` (${unit})` : ''
}

function rawUnitSuffix(materialId: number | null) {
  const unit = productionStore.rawMaterials.find(material => material.id === materialId)?.unit
  return unit ? ` (${unit})` : ''
}

function setProduct(output: OutputDraft, value: string | number | null) {
  output.product = value === null ? null : Number(value)
  output.size_range = null
  output.color = null
}

function setSize(output: OutputDraft, value: string | number | null) {
  output.size_range = value === null ? null : Number(value)
  output.color = null
}

function validate(): boolean {
  problems.value = []
  if (!outputs.value.length) problems.value.push('Add at least one output.')
  if (!inputs.value.length) problems.value.push('Add at least one raw material input.')
  outputs.value.forEach((output, index) => {
    outputProblems(output, productById(output.product)).forEach(problem => problems.value.push(`Output ${index + 1}: ${problem}`))
  })
  inputs.value.forEach((input, index) => {
    if (input.raw_material === null) problems.value.push(`Input ${index + 1}: Choose a raw material.`)
    if (!(Number(input.quantity) > 0)) problems.value.push(`Input ${index + 1}: Quantity must be greater than zero.`)
  })
  return problems.value.length === 0
}

async function submit() {
  serverError.value = ''
  if (!validate()) return
  saving.value = true
  try {
    await acceptQueued(() => productionStore.createRun({
      reference: reference.value.trim(),
      notes: notes.value.trim(),
      items: outputs.value.map(output => ({
        variant: resolveVariant(productById(output.product), output)!.id,
        quantity: Number(output.quantity),
      })),
      inputs: inputs.value.map(input => ({
        raw_material: input.raw_material as number,
        quantity: Number(input.quantity),
      })),
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
    await productionStore.fetchLookups()
  } catch (e) {
    serverError.value = errorMessageOf(e)
  }
})
</script>

<style scoped>
.modal-card { background: white; border-radius: 0.5rem; padding: 1.5rem; width: min(860px, 96vw); max-height: 90vh; overflow: auto; }
.modal-title { font-size: 1.25rem; font-weight: 600; }
.muted { color: #6b7280; font-size: 0.875rem; margin-bottom: 0.75rem; }
.top-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 0.75rem 0; }
.form-group label, .field label { display: block; font-size: 0.8125rem; font-weight: 500; margin-bottom: 0.25rem; color: #374151; }
.form-input { width: 100%; padding: 0.5rem 0.625rem; border: 1px solid #d1d5db; border-radius: 0.375rem; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin: 1rem 0 0.5rem; }
.section-header h3 { font-size: 1rem; font-weight: 600; }
.line-card { border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 0.5rem; }
.line-fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.5rem; align-items: end; }
.field.wide { grid-column: span 2; }
.link-btn { background: none; border: none; cursor: pointer; font-size: 0.8125rem; color: #2563eb; justify-self: start; }
.link-btn.danger { color: #b91c1c; }
.link-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-secondary.small { padding: 0.25rem 0.75rem; font-size: 0.875rem; }
.problem-list { color: #b91c1c; font-size: 0.875rem; margin-top: 0.75rem; padding-left: 1.25rem; }
.form-error { color: #b91c1c; font-size: 0.875rem; margin-top: 0.75rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
.btn-primary:disabled { opacity: 0.6; }
@media (max-width: 640px) { .top-grid { grid-template-columns: 1fr; } .field.wide { grid-column: auto; } }
</style>
