<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ product ? 'Edit Product' : 'Add Product' }}</h2>
        <button type="button" class="close-btn" aria-label="Close" @click="emit('close')">&times;</button>
      </div>

      <form class="modal-form" @submit.prevent="save">
        <div class="modal-body">
          <div class="form-grid">
            <label class="field">
              <span>Name</span>
              <input v-model="name" class="form-input" required maxlength="255" />
            </label>
            <div class="field">
              <span>Unit</span>
              <SearchableSelect
                id="product-unit"
                :modelValue="unit || null"
                :options="unitsStore.unitOptions"
                placeholder="Select a unit"
                required
                @update:modelValue="v => (unit = v ? String(v) : '')"
              />
            </div>
            <label v-if="authStore.isManager" class="field">
              <span>Cost per unit (manual, optional)</span>
              <input v-model.number="cop" type="number" min="0" step="0.01" class="form-input" />
              <small class="hint">Leave empty to use the cost derived from production runs. A value here overrides it.</small>
            </label>
            <label class="field">
              <span>Product type</span>
              <select v-model="productType" class="form-input">
                <option value="MANUFACTURED">Manufactured</option>
                <option value="PURCHASED">Purchased</option>
              </select>
            </label>
          </div>

          <section class="section">
            <div class="section-title">Size ranges <span class="muted">(up to {{ MAX_SIZE_RANGES }})</span></div>
            <div class="chips">
              <span v-for="sr in selectedSizeRanges" :key="sr.id" class="chip">
                {{ sr.name }}
                <button type="button" class="chip-remove" :aria-label="`Remove ${sr.name}`" @click="removeSizeRange(sr.id)">&times;</button>
              </span>
              <span v-if="!selectedSizeRanges.length" class="muted">None selected</span>
            </div>
            <SearchableSelect
              id="size-range-picker"
              :modelValue="null"
              :options="sizeRangeOptions"
              :disabled="sizeRangeIds.length >= MAX_SIZE_RANGES"
              placeholder="Add a size range"
              @change="addSizeRange"
            />
            <p class="hint">Need a new size range? Create it on the Catalog page.</p>
          </section>

          <section class="section">
            <div class="section-title">Colors and quantities <span class="muted">({{ unit || 'unit' }})</span></div>
            <p v-if="!sizeRangeIds.length" class="muted">Select at least one size range to enter quantities.</p>

            <div v-for="block in blocks" :key="block.key" class="color-block">
              <div class="block-header">
                <SearchableSelect
                  :id="`block-color-${block.key}`"
                  :modelValue="block.colorId"
                  :options="colorOptions(block)"
                  placeholder="Pick a color"
                  @update:modelValue="v => (block.colorId = v === null ? null : Number(v))"
                />
                <SearchableSelect
                  v-if="copyOptions(block).length"
                  :id="`block-copy-${block.key}`"
                  :modelValue="null"
                  :options="copyOptions(block)"
                  placeholder="Copy from another color"
                  @change="v => copyFrom(block, v)"
                />
                <span class="block-total">{{ blockTotal(block, sizeRangeIds) }} {{ unit }}</span>
                <button type="button" class="action-btn delete" @click="removeBlock(block.key)">Remove color</button>
              </div>
              <div v-if="selectedSizeRanges.length" class="qty-grid">
                <label v-for="sr in selectedSizeRanges" :key="sr.id" class="field">
                  <span>{{ sr.name }} ({{ unit || 'unit' }})</span>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    class="form-input"
                    :value="block.quantities[sr.id] ?? ''"
                    @input="setQuantity(block, sr.id, ($event.target as HTMLInputElement).value)"
                  />
                </label>
              </div>
            </div>

            <button type="button" class="btn-secondary add-color" @click="addBlock">+ Add color</button>
          </section>

          <div class="total-bar">
            <span>Total quantity</span>
            <strong>{{ total }} {{ unit }}</strong>
          </div>

          <p v-if="error" class="form-error">{{ error }}</p>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn-secondary" @click="emit('close')">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Saving...' : 'Save Product' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useProductsStore } from '../stores/products'
import { useSizeRangeStore } from '../stores/sizeRange'
import { useColorStore } from '../stores/color'
import { useUnitsStore } from '../../../shared/stores/units'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { useAuthStore } from '../../../shared/stores/auth'
import {
  blockProblem,
  blockTotal,
  blocksFromVariants,
  copyBlockQuantities,
  dropSizeRange,
  grandTotal,
  takenColorIds,
  toVariantInputs,
  type ColorBlock,
  type Quantity,
} from '../utils/colorBlocks'
import type { Product } from '../types'

const props = defineProps<{ product: Product | null }>()
const emit = defineEmits<{ close: [] }>()

const MAX_SIZE_RANGES = 3

const productsStore = useProductsStore()
const sizeRangeStore = useSizeRangeStore()
const colorStore = useColorStore()
const unitsStore = useUnitsStore()

let keySeq = 0
const nextKey = () => ++keySeq

const name = ref(props.product?.name ?? '')
const unit = ref(props.product?.unit ?? '')
const authStore = useAuthStore()
const cop = ref<number | string>(props.product ? Number(props.product.cop) : '')
const productType = ref<'MANUFACTURED' | 'PURCHASED'>(props.product?.product_type ?? 'MANUFACTURED')
const sizeRangeIds = ref<number[]>(props.product ? [...props.product.size_ranges] : [])
const blocks = ref<ColorBlock[]>(props.product ? blocksFromVariants(props.product.variants, nextKey) : [])
const saving = ref(false)
const error = ref('')

const selectedSizeRanges = computed(() =>
  sizeRangeIds.value.map(id => ({
    id,
    name: sizeRangeStore.sizeRanges.find(sr => sr.id === id)?.name ?? `#${id}`,
  }))
)

const sizeRangeOptions = computed(() =>
  sizeRangeStore.sizeRanges
    .filter(sr => !sizeRangeIds.value.includes(sr.id))
    .map(sr => ({ value: sr.id, label: sr.name }))
)

const total = computed(() => grandTotal(blocks.value, sizeRangeIds.value))

function colorName(id: number | null): string {
  return colorStore.colors.find(c => c.id === id)?.name ?? ''
}

function colorOptions(block: ColorBlock) {
  const taken = takenColorIds(blocks.value, block.key)
  return colorStore.colors
    .filter(c => !taken.includes(c.id))
    .map(c => ({ value: c.id, label: c.name }))
}

function copyOptions(block: ColorBlock) {
  return blocks.value
    .filter(b => b.key !== block.key && b.colorId !== null)
    .map(b => ({ value: b.key, label: colorName(b.colorId) }))
}

function addSizeRange(value: string | number | null) {
  if (value === null || sizeRangeIds.value.length >= MAX_SIZE_RANGES) return
  const id = Number(value)
  if (sizeRangeIds.value.includes(id)) return
  sizeRangeIds.value = [...sizeRangeIds.value, id]
}

function removeSizeRange(id: number) {
  sizeRangeIds.value = sizeRangeIds.value.filter(x => x !== id)
  blocks.value = dropSizeRange(blocks.value, id)
}

function addBlock() {
  blocks.value.push({ key: nextKey(), colorId: null, quantities: {} })
}

function removeBlock(key: number) {
  blocks.value = blocks.value.filter(b => b.key !== key)
}

function copyFrom(target: ColorBlock, sourceKey: string | number | null) {
  const source = blocks.value.find(b => b.key === Number(sourceKey))
  const index = blocks.value.findIndex(b => b.key === target.key)
  if (!source || index === -1) return
  blocks.value[index] = copyBlockQuantities(source, target, sizeRangeIds.value)
}

function setQuantity(block: ColorBlock, sizeRangeId: number, raw: string) {
  const value: Quantity = raw === '' ? '' : Number(raw)
  block.quantities[sizeRangeId] = value
}

function errorMessageOf(e: any): string {
  const data = e?.response?.data
  if (typeof data === 'string') return data
  if (data?.error) return data.error
  if (data?.detail) return data.detail
  if (data && typeof data === 'object') return flatten(data).join(' ')
  return e?.message || 'Could not save the product.'
}

function flatten(value: unknown, prefix = ''): string[] {
  if (Array.isArray(value)) return value.flatMap(v => flatten(v, prefix))
  if (value && typeof value === 'object') {
    return Object.entries(value).flatMap(([field, inner]) => {
      const label = field === 'non_field_errors' ? prefix : prefix ? `${prefix} ${field}` : field
      return flatten(inner, label)
    })
  }
  return [prefix ? `${prefix}: ${String(value)}` : String(value)]
}

async function save() {
  error.value = ''
  if (!unit.value) {
    error.value = 'Pick a unit for this product.'
    return
  }
  const problem = blockProblem(blocks.value)
  if (problem) {
    error.value = problem
    return
  }

  const payload = {
    name: name.value.trim(),
    unit: unit.value,
    cop: Number(cop.value),
    product_type: productType.value,
    size_ranges: [...sizeRangeIds.value],
    variants: toVariantInputs(blocks.value, sizeRangeIds.value),
  }

  saving.value = true
  try {
    if (props.product) {
      await acceptQueued(() => productsStore.updateProduct(props.product!.id, payload))
    } else {
      await acceptQueued(() => productsStore.createProduct(payload))
    }
    emit('close')
  } catch (e) {
    error.value = errorMessageOf(e)
  } finally {
    saving.value = false
  }
}

</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px 16px;
  overflow-y: auto;
  z-index: 50;
}
.modal {
  background: #fff;
  border-radius: 10px;
  width: 100%;
  max-width: 760px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}
.modal-header h2 { font-size: 1.125rem; font-weight: 700; }
.close-btn { font-size: 1.5rem; line-height: 1; color: #6b7280; background: none; border: none; cursor: pointer; }
.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 20px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 14px 20px; border-top: 1px solid #e5e7eb; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }
.field { display: flex; flex-direction: column; gap: 4px; font-size: 0.875rem; }
.section { display: flex; flex-direction: column; gap: 10px; }
.section-title { font-weight: 600; }
.muted { color: #6b7280; font-weight: 400; font-size: 0.8125rem; }
.hint { color: #6b7280; font-size: 0.8125rem; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.chip { display: inline-flex; align-items: center; gap: 4px; background: #eef2ff; color: #3730a3; padding: 3px 4px 3px 10px; border-radius: 999px; font-size: 0.8125rem; }
.chip-remove { background: none; border: none; color: #3730a3; cursor: pointer; font-size: 1rem; line-height: 1; padding: 0 4px; }
.color-block { border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
.block-header { display: grid; grid-template-columns: minmax(160px, 1fr) minmax(160px, 1fr) auto auto; gap: 10px; align-items: center; }
.block-total { font-weight: 600; font-size: 0.875rem; white-space: nowrap; }
.qty-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
.add-color { align-self: flex-start; }
.action-btn.delete { color: #b91c1c; background: none; border: none; cursor: pointer; font-size: 0.8125rem; }
.total-bar { display: flex; justify-content: space-between; align-items: center; background: #f9fafb; border-radius: 8px; padding: 10px 14px; }
.form-error { color: #b91c1c; font-size: 0.875rem; }
@media (max-width: 640px) {
  .block-header { grid-template-columns: 1fr; }
}
</style>
