<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <form @submit.prevent="onSubmit" class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <h2 class="modal-title">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            {{ sale?.id ? `Edit Sale — ${sale.bill_no}` : 'New Sale' }}
          </h2>
          <button type="button" @click="$emit('close')" class="close-button">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="modal-body">
          <!-- Sale Information -->
          <div class="section">
            <h3 class="section-title">Sale Information</h3>

            <!-- Bill No badge (read-only on edit) -->
            <div v-if="sale?.bill_no" class="bill-badge">
              Bill No: <strong>{{ sale.bill_no }}</strong>
              <span class="text-xs text-gray-400 ml-2">(auto-assigned)</span>
            </div>
            <div v-else class="bill-badge text-gray-400">Bill No: auto-assigned on save</div>

            <div class="form-grid mt-3">
              <div class="form-group">
                <label for="customer" class="form-label">Customer <span class="required">*</span></label>
                <select v-model="form.customer" id="customer" class="form-input" required>
                  <option value="">Select Customer</option>
                  <option v-for="c in customers" :key="c.id" :value="c.id">
                    {{ c.name }}{{ c.city ? ` — ${c.city}` : '' }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="sale_type" class="form-label">Sale Type <span class="required">*</span></label>
                <select v-model="form.sale_type" id="sale_type" class="form-input" required>
                  <option value="REGULAR">Regular</option>
                  <option value="WALK_IN">Walk-in</option>
                  <option value="PHONE_ORDER">Phone Order</option>
                </select>
              </div>

              <div class="form-group">
                <label for="payment_status" class="form-label">Payment Status <span class="required">*</span></label>
                <select v-model="form.payment_status" id="payment_status" class="form-input" required>
                  <option value="UNPAID">Unpaid</option>
                  <option value="PARTIAL">Partial</option>
                  <option value="PAID">Paid</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Products Section -->
          <div class="section">
            <h3 class="section-title">Products (quantities in dozens)</h3>

            <!-- Add item row -->
            <div class="add-product-section">
              <div class="add-product-grid">
                <div class="form-group">
                  <label class="form-label">Product</label>
                  <select v-model="newItem.product_id" class="form-input" @change="onProductChange">
                    <option :value="0">Select Product</option>
                    <option v-for="p in products" :key="p.id" :value="p.id">
                      {{ p.name }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">Size Range</label>
                  <select v-model="newItem.size_range_id" class="form-input">
                    <option :value="0">Select Size</option>
                    <option v-for="sr in filteredSizeRanges" :key="sr.id" :value="sr.id">
                      {{ sr.name }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">Color</label>
                  <select v-model="newItem.color_id" class="form-input">
                    <option :value="0">Select Color</option>
                    <option v-for="c in colors" :key="c.id" :value="c.id">
                      {{ c.name }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">Stock (dz)</label>
                  <span class="form-input bg-gray-50 text-center font-mono">
                    {{ availableDozen }}
                  </span>
                </div>

                <div class="form-group">
                  <label class="form-label">Qty (dozens)</label>
                  <input
                    v-model.number="newItem.quantity_dozens"
                    type="number"
                    step="1"
                    class="form-input"
                    placeholder="0"
                  />
                </div>

                <div class="form-group">
                  <label class="form-label">Price / dozen (₨)</label>
                  <input
                    v-model.number="newItem.unit_price"
                    type="number"
                    step="0.01"
                    min="0"
                    class="form-input"
                    placeholder="0.00"
                  />
                </div>

                <div class="form-group">
                  <label class="form-label">&nbsp;</label>
                  <button
                    type="button"
                    @click="addItem"
                    class="btn-add"
                    :disabled="!canAddItem"
                  >+ Add</button>
                </div>
              </div>
            </div>

            <!-- Items list -->
            <div v-if="saleItems.length > 0" class="products-list mt-3">
              <div v-for="(item, idx) in saleItems" :key="idx" class="product-item">
                <div class="product-info">
                  <div class="product-name">{{ getProductName(item.product_id) }}</div>
                  <div class="product-details">
                    {{ getSizeRangeName(item.size_range_id) }} / {{ getColorName(item.color_id) }}
                    &nbsp;·&nbsp;
                    <strong>{{ item.quantity_dozens }} dz</strong>
                    × ₨{{ item.unit_price.toFixed(2) }}
                    = ₨{{ (item.quantity_dozens * item.unit_price).toFixed(2) }}
                  </div>
                </div>
                <button type="button" @click="removeItem(idx)" class="btn-remove">✕</button>
              </div>
            </div>
            <div v-else class="empty-products">No products added yet.</div>

            <!-- Total -->
            <div class="total-section">
              <span class="total-label">Total:</span>
              <span class="total-value">₨{{ totalAmount.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <button type="button" @click="$emit('close')" class="btn-cancel">Cancel</button>
          <button type="submit" class="btn-save" :disabled="saleItems.length === 0">
            {{ sale?.id ? 'Update Sale' : 'Create Sale' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useProductsStore } from '@/modules/products/stores/products'
import { useColorStore } from '@/modules/products/stores/color'
import { useSizeRangeStore } from '@/modules/products/stores/sizeRange'
import { useProductVariantStore } from '@/modules/products/stores/productVariant'
import type { Sale, CreateSaleRequest } from '../types'

interface Props {
  sale?: Sale | null
  customers: any[]
}

const props = defineProps<Props>()
const emit = defineEmits(['save', 'close'])

const productsStore = useProductsStore()
const colorStore = useColorStore()
const sizeRangeStore = useSizeRangeStore()
const variantStore = useProductVariantStore()

const products = computed(() => productsStore.products || [])
const colors = computed(() => colorStore.colors || [])

// Size ranges relevant to the selected product
const filteredSizeRanges = computed(() => {
  if (!newItem.value.product_id) return sizeRangeStore.sizeRanges
  const product = products.value.find(p => p.id === newItem.value.product_id)
  if (!product) return sizeRangeStore.sizeRanges
  // Product.size_range is the FK; show that plus any variant size ranges
  const variantSrIds = new Set(
    variantStore.variants
      .filter(v => v.product === newItem.value.product_id)
      .map(v => v.size_range)
  )
  if (product.size_range) variantSrIds.add(product.size_range)
  if (variantSrIds.size === 0) return sizeRangeStore.sizeRanges
  return sizeRangeStore.sizeRanges.filter(sr => variantSrIds.has(sr.id))
})

// Available stock for selected product+size+color combination
const availableDozen = computed(() => {
  const { product_id, size_range_id, color_id } = newItem.value
  if (!product_id || !size_range_id || !color_id) return '—'
  const variant = variantStore.variants.find(
    v => v.product === product_id && v.size_range === size_range_id && v.color === color_id
  )
  return variant ? variant.quantity_dozens : 0
})

const form = ref<CreateSaleRequest>({
  customer: 0,
  sale_type: 'REGULAR',
  total_amount: 0,
  date: new Date().toISOString().split('T')[0],
  payment_status: 'UNPAID',
  items: [],
})

const saleItems = ref<Array<{
  product_id: number
  size_range_id: number
  color_id: number
  quantity_dozens: number
  unit_price: number
}>>([])

const newItem = ref({ product_id: 0, size_range_id: 0, color_id: 0, quantity_dozens: 0, unit_price: 0 })

const totalAmount = computed(() =>
  saleItems.value.reduce((sum, i) => sum + i.quantity_dozens * i.unit_price, 0)
)

const canAddItem = computed(() =>
  newItem.value.product_id > 0 &&
  newItem.value.size_range_id > 0 &&
  newItem.value.color_id > 0 &&
  newItem.value.quantity_dozens > 0 &&
  newItem.value.unit_price > 0
)

function onProductChange() {
  newItem.value.size_range_id = 0
  newItem.value.color_id = 0
  if (newItem.value.product_id) {
    variantStore.fetchVariants(newItem.value.product_id)
  }
}

function getProductName(id: number) {
  return products.value.find(p => p.id === id)?.name ?? 'Unknown'
}
function getSizeRangeName(id: number) {
  return sizeRangeStore.sizeRanges.find(sr => sr.id === id)?.name ?? '—'
}
function getColorName(id: number) {
  return colors.value.find(c => c.id === id)?.name ?? '—'
}

function addItem() {
  if (!canAddItem.value) return
  saleItems.value.push({ ...newItem.value })
  newItem.value = { product_id: 0, size_range_id: 0, color_id: 0, quantity_dozens: 0, unit_price: 0 }
}

function removeItem(idx: number) {
  saleItems.value.splice(idx, 1)
}

watch(() => props.sale, (val) => {
  if (val) {
    form.value = {
      customer: val.customer,
      sale_type: val.sale_type || 'REGULAR',
      total_amount: val.total_amount,
      date: val.date?.split('T')[0] ?? new Date().toISOString().split('T')[0],
      payment_status: val.payment_status,
      items: [],
    }
    saleItems.value = (val.sale_items || []).map(item => ({
      product_id: item.product,
      size_range_id: item.size_range,
      color_id: item.color,
      quantity_dozens: item.quantity_dozens,
      unit_price: item.unit_price,
    }))
  } else {
    form.value = {
      customer: 0,
      sale_type: 'REGULAR',
      total_amount: 0,
      date: new Date().toISOString().split('T')[0],
      payment_status: 'UNPAID',
      items: [],
    }
    saleItems.value = []
  }
}, { immediate: true })

async function onSubmit() {
  form.value.total_amount = totalAmount.value
  form.value.items = saleItems.value.map(i => ({
    product_id: i.product_id,
    size_range_id: i.size_range_id,
    color_id: i.color_id,
    quantity_dozens: i.quantity_dozens,
    unit_price: i.unit_price,
  }))
  emit('save', { ...form.value })
}

onMounted(async () => {
  await Promise.all([
    productsStore.products.length === 0 ? productsStore.fetchProducts() : Promise.resolve(),
    colorStore.colors.length === 0 ? colorStore.fetchColors() : Promise.resolve(),
    sizeRangeStore.sizeRanges.length === 0 ? sizeRangeStore.fetchSizeRanges() : Promise.resolve(),
  ])
})
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.6);
  backdrop-filter: blur(4px); display: flex; align-items: center;
  justify-content: center; z-index: 1000; padding: 1rem;
}
.modal-container { width: 100%; max-width: 960px; max-height: 92vh; display: flex; }
.modal-content {
  background: white; border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,.3);
  display: flex; flex-direction: column; width: 100%; overflow: hidden;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1.25rem 2rem; border-bottom: 2px solid #f0f0f0;
}
.modal-title {
  font-size: 1.375rem; font-weight: 700; color: #1a1a1a;
  display: flex; align-items: center; gap: .75rem; margin: 0;
}
.close-button {
  background: none; border: none; padding: .5rem; cursor: pointer;
  color: #6b7280; border-radius: 8px; transition: all .2s;
}
.close-button:hover { background: #f3f4f6; color: #1f2937; }
.modal-body { flex: 1; overflow-y: auto; padding: 1.5rem 2rem; background: #fafafa; }
.section {
  background: white; border-radius: 12px; padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.section-title {
  font-size: 1rem; font-weight: 600; color: #1f2937;
  margin-bottom: 1rem; padding-bottom: .5rem; border-bottom: 2px solid #e5e7eb;
}
.bill-badge {
  display: inline-block; background: #eff6ff; color: #1d4ed8;
  border: 1px solid #bfdbfe; border-radius: 6px; padding: .25rem .75rem;
  font-size: .875rem;
}
.form-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;
}
.form-group { display: flex; flex-direction: column; }
.form-label {
  font-size: .8125rem; font-weight: 600; color: #374151; margin-bottom: .375rem;
}
.required { color: #ef4444; }
.form-input {
  padding: .625rem .875rem; border: 2px solid #e5e7eb; border-radius: 8px;
  font-size: .9rem; transition: border-color .2s; background: white;
}
.form-input:focus { outline: none; border-color: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,.1); }
.add-product-section {
  background: #f9fafb; border: 2px dashed #d1d5db; border-radius: 8px; padding: 1rem;
}
.add-product-grid {
  display: grid;
  grid-template-columns: 2fr 1.2fr 1.2fr .8fr .8fr 1fr auto;
  gap: .75rem; align-items: end;
}
.btn-add {
  padding: .625rem 1rem; background: #10b981; color: white;
  border: none; border-radius: 8px; font-weight: 600; cursor: pointer;
  white-space: nowrap; transition: background .2s;
}
.btn-add:hover:not(:disabled) { background: #059669; }
.btn-add:disabled { background: #d1d5db; cursor: not-allowed; }
.products-list { display: flex; flex-direction: column; gap: .625rem; }
.product-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: .75rem 1rem; background: #f9fafb; border: 1px solid #e5e7eb;
  border-radius: 8px;
}
.product-info { flex: 1; }
.product-name { font-weight: 600; color: #1f2937; font-size: .9rem; }
.product-details { font-size: .8125rem; color: #6b7280; margin-top: .125rem; }
.btn-remove {
  background: #fee2e2; color: #dc2626; border: none;
  padding: .375rem .625rem; border-radius: 6px; cursor: pointer; font-size: .875rem;
}
.btn-remove:hover { background: #fecaca; }
.empty-products { text-align: center; padding: 1.5rem; color: #9ca3af; font-size: .875rem; }
.total-section {
  display: flex; justify-content: flex-end; align-items: center; gap: 1rem;
  border-top: 2px solid #e5e7eb; padding-top: .875rem; margin-top: .875rem;
}
.total-label { font-size: 1rem; font-weight: 600; color: #1f2937; }
.total-value { font-size: 1.375rem; font-weight: 700; color: #10b981; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 1rem;
  padding: 1.25rem 2rem; border-top: 2px solid #f0f0f0; background: white;
}
.btn-cancel {
  padding: .625rem 1.25rem; border: 2px solid #e5e7eb; background: white;
  color: #6b7280; font-weight: 600; border-radius: 8px; cursor: pointer;
}
.btn-cancel:hover { background: #f3f4f6; }
.btn-save {
  padding: .625rem 2rem; border: none;
  background: linear-gradient(135deg,#10b981,#059669);
  color: white; font-weight: 600; border-radius: 8px; cursor: pointer;
  box-shadow: 0 4px 12px rgba(16,185,129,.3); transition: all .2s;
}
.btn-save:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(16,185,129,.4); }
.btn-save:disabled { background: #d1d5db; cursor: not-allowed; box-shadow: none; }
@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  .add-product-grid { grid-template-columns: 1fr; }
}
</style>
