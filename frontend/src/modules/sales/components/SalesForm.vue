<template>
  <form class="sale-form" @submit.prevent="submit">
    <div class="field">
      <label for="sale-customer">Customer</label>
      <SearchableSelect
        id="sale-customer"
        v-model="customerId"
        :options="customerOptions"
        placeholder="Search customer"
        required
      />
    </div>

    <div class="field narrow">
      <label for="sale-type">Sale type</label>
      <select id="sale-type" v-model="saleType" class="form-input">
        <option value="REGULAR">Regular</option>
        <option value="WALK_IN">Walk-in</option>
        <option value="PHONE_ORDER">Phone order</option>
      </select>
    </div>

    <div class="lines">
      <div class="line-head">
        <span>Product</span><span>Size range</span><span>Color</span><span>Quantity</span><span>Unit price</span><span>Line total</span><span />
      </div>
      <div v-for="(line, index) in lines" :key="line.key" class="line" :data-testid="`sale-line-${index}`">
        <SearchableSelect
          :id="`line-product-${line.key}`"
          :model-value="line.productId"
          :options="productOptions"
          placeholder="Product"
          @update:model-value="(v) => onProductChange(line, v)"
        />
        <SearchableSelect
          :id="`line-size-${line.key}`"
          :model-value="line.sizeRangeId"
          :options="sizeOptionsFor(line)"
          placeholder="Size range"
          :disabled="!line.productId"
          @update:model-value="(v) => onSizeChange(line, v)"
        />
        <SearchableSelect
          :id="`line-color-${line.key}`"
          :model-value="line.colorId"
          :options="colorOptionsFor(line)"
          placeholder="Color"
          :disabled="!line.sizeRangeId"
          @update:model-value="(v) => (line.colorId = (v as number | null))"
        />
        <div class="qty">
          <input
            type="number"
            min="0.01"
            step="0.01"
            class="form-input"
            :value="line.quantity ?? ''"
            :aria-label="`Quantity line ${index + 1}`"
            @input="line.quantity = toNumber(($event.target as HTMLInputElement).value)"
          />
          <span class="unit">{{ unitOf(line) }}</span>
          <small v-if="line.colorId" class="available">
            Available: {{ availableLabel(line) }}
          </small>
        </div>
        <input
          type="number"
          min="0"
          step="0.01"
          class="form-input"
          placeholder="Type price"
          :value="line.unitPrice ?? ''"
          :aria-label="`Unit price line ${index + 1}`"
          @input="line.unitPrice = toNumber(($event.target as HTMLInputElement).value)"
        />
        <span class="line-total">{{ formatMoney(lineTotal(line)) }}</span>
        <button type="button" class="link-btn" :disabled="lines.length === 1" @click="removeLine(line.key)">Remove</button>
        <small v-if="errors.get(line.key)" class="line-error">{{ errors.get(line.key) }}</small>
      </div>
      <button type="button" class="secondary-btn" @click="addLine">Add line</button>
    </div>

    <div class="totals">
      <div><span>Sale total</span><strong>{{ formatMoney(total) }}</strong></div>
      <div><span>Balance after receipt</span><strong>{{ formatMoney(balance) }}</strong></div>
    </div>

    <div class="field-row">
      <div class="field">
        <label for="sale-received">Amount received now</label>
        <input
          id="sale-received"
          type="number"
          min="0"
          step="0.01"
          class="form-input"
          :value="amountReceived ?? ''"
          @input="amountReceived = toNumber(($event.target as HTMLInputElement).value)"
        />
      </div>
      <div class="field">
        <label for="sale-method">Payment method</label>
        <select id="sale-method" v-model="paymentMethod" class="form-input" :disabled="!amountReceived">
          <option value="">Choose</option>
          <option value="CASH">Cash</option>
          <option value="BANK">Bank transfer</option>
          <option value="CHEQUE">Cheque</option>
          <option value="PARCHI">Parchi (promissory)</option>
        </select>
      </div>
    </div>

    <p v-if="receiptError" class="form-error">{{ receiptError }}</p>
    <p v-if="submitError" class="form-error">{{ submitError }}</p>

    <div class="actions">
      <button type="button" class="secondary-btn" @click="emit('cancel')">Cancel</button>
      <button type="submit" class="primary-btn" :disabled="!canSubmit || submitting">
        {{ submitting ? 'Saving...' : 'Save sale' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import { useSalesStore } from '../stores/sales'
import { useCustomersStore } from '../../customers/stores/customers'
import { useToastStore } from '../../../shared/stores/toast'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import {
  lineErrors, lineTotal, saleTotal, validateLine, roundMoney,
  type SaleLineDraft, type LineStock,
} from '../utils/saleLines'
import { apiErrorMessage } from '../../../shared/utils/apiError'
import type { CatalogProduct, CatalogVariant, CreateSaleRequest, PaymentMethod, Sale, SaleType } from '../types'

const emit = defineEmits<{
  saved: [sale: Sale | undefined]
  cancel: []
}>()

const salesStore = useSalesStore()
const customersStore = useCustomersStore()
const toast = useToastStore()

let nextKey = 1
const newLine = (): SaleLineDraft => ({
  key: nextKey++, productId: null, sizeRangeId: null, colorId: null, quantity: null, unitPrice: null,
})

const customerId = ref<number | null>(null)
const saleType = ref<SaleType>('REGULAR')
const lines = ref<SaleLineDraft[]>([newLine()])
const amountReceived = ref<number | null>(null)
const paymentMethod = ref<PaymentMethod | ''>('')
const submitting = ref(false)
const submitError = ref('')

const toNumber = (raw: string): number | null => (raw === '' ? null : Number(raw))

const customerOptions = computed(() =>
  customersStore.customers
    .filter(c => c.is_active)
    .map(c => ({ value: c.id, label: c.city ? `${c.name} - ${c.city}` : c.name })),
)

const productById = computed(() => new Map(salesStore.products.map(p => [p.id, p])))
const sizeNameById = computed(() => new Map(salesStore.sizeRanges.map(s => [s.id, s.name])))

const productOptions = computed(() =>
  salesStore.products.map(p => ({ value: p.id, label: `${p.name} (${p.unit})` })),
)

const sizeOptionsFor = (line: SaleLineDraft) => {
  const product = line.productId ? productById.value.get(line.productId) : undefined
  if (!product) return []
  return product.size_ranges.map(id => ({ value: id, label: sizeNameById.value.get(id) ?? String(id) }))
}

const variantsFor = (line: SaleLineDraft): CatalogVariant[] => {
  const product = line.productId ? productById.value.get(line.productId) : undefined
  if (!product || !line.sizeRangeId) return []
  return product.variants.filter(v => v.size_range === line.sizeRangeId)
}

const colorOptionsFor = (line: SaleLineDraft) =>
  variantsFor(line).map(v => ({
    value: v.color,
    label: `${v.color_name} - ${roundMoney(Number(v.quantity))} ${productById.value.get(line.productId!)?.unit ?? ''} available`,
  }))

const variantFor = (line: SaleLineDraft): CatalogVariant | undefined =>
  variantsFor(line).find(v => v.color === line.colorId)

const unitOf = (line: SaleLineDraft): string => {
  const product: CatalogProduct | undefined = line.productId ? productById.value.get(line.productId) : undefined
  return product?.unit ?? ''
}

const availableLabel = (line: SaleLineDraft): string => {
  const variant = variantFor(line)
  return variant ? `${roundMoney(Number(variant.quantity))} ${unitOf(line)}` : 'none recorded'
}

const stockOf = (line: SaleLineDraft): LineStock => {
  const product = line.productId ? productById.value.get(line.productId) : undefined
  const variant = variantFor(line)
  const sizeName = sizeNameById.value.get(line.sizeRangeId ?? 0) ?? ''
  const label = `${product?.name ?? ''} (${sizeName}, ${variant?.color_name ?? ''})`
  return { label, available: variant ? Number(variant.quantity) : null }
}

const onProductChange = (line: SaleLineDraft, value: string | number | null) => {
  line.productId = value === null ? null : Number(value)
  line.sizeRangeId = null
  line.colorId = null
}

const onSizeChange = (line: SaleLineDraft, value: string | number | null) => {
  line.sizeRangeId = value === null ? null : Number(value)
  line.colorId = null
}

const addLine = () => lines.value.push(newLine())
const removeLine = (key: number) => {
  lines.value = lines.value.filter(l => l.key !== key)
}

const errors = computed(() => lineErrors(lines.value, stockOf))
const total = computed(() => saleTotal(lines.value))
const received = computed(() => amountReceived.value ?? 0)
const balance = computed(() => roundMoney(total.value - received.value))

const receiptError = computed(() => {
  if (received.value < 0) return 'Amount received cannot be negative.'
  if (received.value > total.value) return 'Amount received cannot exceed the sale total.'
  if (received.value > 0 && !paymentMethod.value) return 'Choose how the amount was received.'
  return ''
})

const canSubmit = computed(() =>
  customerId.value !== null
  && lines.value.length > 0
  && lines.value.every(l => validateLine(l) === null)
  && errors.value.size === 0
  && receiptError.value === '',
)

const formatMoney = (value: number) => `₨${value.toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

const submit = async () => {
  if (!canSubmit.value || customerId.value === null) return
  submitting.value = true
  submitError.value = ''

  const payload: CreateSaleRequest = {
    customer: customerId.value,
    sale_type: saleType.value,
    items: lines.value.map(l => ({
      product_id: l.productId as number,
      size_range_id: l.sizeRangeId as number,
      color_id: l.colorId as number,
      quantity: String(l.quantity),
      unit_price: String(l.unitPrice),
    })),
  }
  if (received.value > 0) {
    payload.amount_received = received.value.toFixed(2)
    payload.payment_method = paymentMethod.value as PaymentMethod
  }

  try {
    const sale = await acceptQueued(() => salesStore.createSale(payload))
    if (sale === undefined) {
      toast.info('Sale queued', 'It will be saved when the server is reachable.')
    } else {
      toast.success('Sale saved', sale.bill_no)
    }
    emit('saved', sale)
  } catch (e) {
    submitError.value = apiErrorMessage(e)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const loads: Promise<unknown>[] = [salesStore.fetchCatalog()]
  if (!customersStore.customers.length) loads.push(customersStore.fetchCustomers())
  try {
    await Promise.all(loads)
  } catch (e) {
    submitError.value = apiErrorMessage(e)
  }
})
</script>

<style scoped>
.sale-form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.field.narrow { max-width: 14rem; }
.field-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); gap: 1rem; }
.lines { display: flex; flex-direction: column; gap: 0.5rem; }
.line-head, .line {
  display: grid;
  grid-template-columns: minmax(10rem, 1.4fr) minmax(7rem, 1fr) minmax(9rem, 1.2fr) minmax(8rem, 1fr) minmax(6rem, 0.8fr) 6rem 5rem;
  gap: 0.5rem;
  align-items: start;
}
.line-head { font-size: 0.8rem; font-weight: 600; opacity: 0.7; }
.line-error { grid-column: 1 / -1; color: #b42318; }
.qty { display: flex; flex-wrap: wrap; align-items: center; gap: 0.35rem; }
.qty input { width: 6rem; }
.unit { font-size: 0.85rem; opacity: 0.8; }
.available { flex-basis: 100%; opacity: 0.7; }
.line-total { font-variant-numeric: tabular-nums; padding-top: 0.5rem; }
.totals { display: flex; gap: 2rem; flex-wrap: wrap; }
.totals div { display: flex; flex-direction: column; }
.totals span { font-size: 0.8rem; opacity: 0.7; }
.totals strong { font-size: 1.25rem; }
.form-error { color: #b42318; margin: 0; }
.actions { display: flex; justify-content: flex-end; gap: 0.5rem; }
.link-btn { background: none; border: none; color: #b42318; cursor: pointer; padding-top: 0.5rem; }
.link-btn:disabled { opacity: 0.4; cursor: default; }
@media (max-width: 760px) {
  .line-head { display: none; }
  .line { grid-template-columns: 1fr 1fr; }
}
</style>
