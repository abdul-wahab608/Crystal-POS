<template>
  <div class="cost-management-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Cost Management</h1>
        <p class="subtitle">Set per-dozen production cost components for each product. Every change adds a new dated entry — past profit reports keep using the price that was actually in effect.</p>
      </div>
      <div class="header-actions">
        <router-link to="/profit" class="btn-secondary">View Profit Analytics</router-link>
        <button v-if="authStore.isManager" class="btn-primary" @click="showAddComponent = true">+ Add Custom Cost Field</button>
      </div>
    </div>

    <div v-if="authStore.isManager" class="filter-group product-select">
      <label>Product</label>
      <SearchableSelect
        :modelValue="selectedProductId"
        @update:modelValue="(value) => (selectedProductId = value === null ? null : Number(value))"
        :options="productOptions"
        id="cost-product"
        placeholder="Search for a product..."
      />
    </div>

    <div v-if="!authStore.isManager" class="empty-state">Product costs are available to managers only.</div>

    <div v-else-if="!selectedProductId" class="empty-state">
      Pick a product above to view or edit its cost breakdown.
    </div>

    <div v-else class="cost-content">
      <div class="current-cost-card">
        <h3>Cost Used for Profit (as of {{ today }})</h3>
        <p class="source-line">Source: <strong>{{ costSourceLabel(profitStore.currentCost?.cost_source) }}</strong></p>
        <div v-if="profitStore.currentCost?.cost_source === 'MISSING'" class="missing-note">
          {{ COST_MISSING_MESSAGE }}. Profit for this product is not shown until a cost is known.
        </div>
        <template v-else>
          <div v-if="profitStore.currentCost?.cost_source === 'COP'" class="fallback-note">
            No manual cost or production run applies, so the Cost of Production on the product (₨{{ formatMoney(totalPerDozen) }}/dozen) is used. Add a manual cost or record a production run to replace it.
          </div>
          <div v-if="profitStore.currentCost?.components?.length" class="cost-breakdown">
            <div v-for="c in profitStore.currentCost?.components || []" :key="c.component_type" class="cost-line">
              <span>{{ c.component_type_name }}</span>
              <span>₨{{ formatMoney(c.amount_per_dozen) }}/dz <small>(since {{ c.valid_from }})</small></span>
            </div>
          </div>
          <div class="cost-total">
            Total: ₨{{ formatMoney(totalPerDozen) }}/dozen &nbsp;·&nbsp; ₨{{ formatMoney(totalPerDozen / 12) }}/piece
          </div>
        </template>
        <p class="override-note">
          A manual cost entry always overrides production-derived cost. Production cost is used only while no manual entry is in effect.
        </p>
      </div>

      <div class="production-section">
        <h3>Production-Derived Cost</h3>
        <p class="form-hint">
          Per unit = cost of the run's raw-material inputs (each at its latest purchase price on or before the run date) ÷ units produced in that run. The most recent run dated on or before the date is used, unless a manual cost applies.
        </p>
        <table class="history-table">
          <thead>
            <tr>
              <th>Run</th>
              <th>Date</th>
              <th>Produced</th>
              <th>Input cost</th>
              <th>Cost/unit</th>
              <th>Used for profit</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="run in profitStore.currentCost?.production_runs || []" :key="run.run_id">
              <td>#{{ run.run_id }}</td>
              <td>{{ run.date }}</td>
              <td>{{ formatMoney(run.output_quantity) }}</td>
              <td>{{ run.input_cost === null ? '—' : `₨${formatMoney(run.input_cost)}` }}</td>
              <td>{{ run.unit_cost === null ? 'Not usable' : `₨${formatMoney(run.unit_cost)}` }}</td>
              <td>
                <span v-if="run.run_id === profitStore.currentCost?.production_run_id" class="used-badge">Used</span>
                <span v-else-if="run.unit_cost === null" class="form-hint">No inputs, or an input has no purchase price</span>
              </td>
            </tr>
            <tr v-if="!profitStore.currentCost?.production_runs?.length">
              <td colspan="6" class="empty-row">No production runs have produced this product.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <form v-if="authStore.isManager" class="add-cost-form" @submit.prevent="submitCost">
        <h3>Add a Cost Entry</h3>
        <div class="form-row">
          <div class="form-group">
            <label for="cost-component">Component</label>
            <select id="cost-component" v-model.number="form.component_type" required class="filter-select">
              <option :value="null" disabled>Choose a component</option>
              <option v-for="c in profitStore.costComponents" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="cost-amount">Amount per dozen (₨)</label>
            <input id="cost-amount" v-model.number="form.amount_per_dozen" type="number" min="0" step="0.01" required class="filter-input" />
          </div>
          <div class="form-group">
            <label for="cost-valid-from">Effective from</label>
            <input id="cost-valid-from" v-model="form.valid_from" type="date" required class="filter-input" />
          </div>
          <button type="submit" class="btn-primary" :disabled="submitting || !form.component_type">Save</button>
        </div>
        <p v-if="costError" class="form-error">{{ costError }}</p>
      </form>

      <div class="history-section">
        <h3>Cost History</h3>
        <table class="history-table">
          <thead>
            <tr>
              <th>Component</th>
              <th>Amount/dz</th>
              <th>Effective From</th>
              <th v-if="authStore.isManager"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in pageItems" :key="c.id">
              <td>{{ c.component_type_name }}</td>
              <td>₨{{ formatMoney(c.amount_per_dozen) }}</td>
              <td>{{ c.valid_from }}</td>
              <td v-if="authStore.isManager">
                <button class="btn-link-danger" @click="removeCost(c.id)">Delete</button>
              </td>
            </tr>
            <tr v-if="profitStore.productCosts.length === 0">
              <td colspan="4" class="empty-row">No cost history recorded yet.</td>
            </tr>
          </tbody>
        </table>
        <PaginationBar
          v-if="profitStore.productCosts.length"
          :page="page"
          :totalPages="totalPages"
          :total="total"
          :pageSize="pageSize"
          @update:page="goTo"
          @update:pageSize="setPageSize"
        />
      </div>
    </div>

    <div v-if="showAddComponent" class="modal-overlay" @click.self="showAddComponent = false">
      <div class="modal-card">
        <h3>Add Custom Cost Field</h3>
        <p class="form-hint">e.g. Packaging, Transport, Overheads — it becomes available for every product.</p>
        <input v-model="newComponentName" type="text" placeholder="Field name" class="filter-input" @keyup.enter="addComponent" />
        <p v-if="componentError" class="form-error">{{ componentError }}</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showAddComponent = false">Cancel</button>
          <button class="btn-primary" :disabled="!newComponentName.trim()" @click="addComponent">Add</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useProfitStore } from '../stores/profit'
import { useProductsStore } from '../../products/stores/products'
import { useAuthStore } from '../../../shared/stores/auth'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import { COST_MISSING_MESSAGE, costSourceLabel } from '../utils/costSource'
import { errorMessageOf } from '../../raw_materials/utils/errorMessage'

const profitStore = useProfitStore()
const productsStore = useProductsStore()
const authStore = useAuthStore()

const selectedProductId = ref<number | null>(null)
const showAddComponent = ref(false)
const newComponentName = ref('')
const submitting = ref(false)
const costError = ref('')
const componentError = ref('')
const today = new Date().toLocaleDateString('en-CA')

const form = ref<{ component_type: number | null; amount_per_dozen: number; valid_from: string }>({
  component_type: null,
  amount_per_dozen: 0,
  valid_from: today,
})

const productOptions = computed(() =>
  productsStore.products.map((p) => ({ value: p.id, label: `${p.name} (${p.unit})` })),
)

const totalPerDozen = computed(() => Number(profitStore.currentCost?.unit_cost || 0))

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(computed(() => profitStore.productCosts))
watch(selectedProductId, reset)

function formatMoney(value: number | string) {
  return Number(value).toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadForProduct() {
  if (!selectedProductId.value) return
  await Promise.all([
    profitStore.fetchProductCosts(selectedProductId.value),
    profitStore.fetchCurrentCost(selectedProductId.value),
  ])
}

watch(selectedProductId, loadForProduct)

async function submitCost() {
  if (!selectedProductId.value || !form.value.component_type) return
  submitting.value = true
  costError.value = ''
  try {
    await acceptQueued(() => profitStore.addProductCost({
      product: selectedProductId.value!,
      component_type: form.value.component_type!,
      amount_per_dozen: form.value.amount_per_dozen,
      valid_from: form.value.valid_from,
    }))
    await loadForProduct()
    form.value.amount_per_dozen = 0
  } catch (error) {
    costError.value = errorMessageOf(error)
  } finally {
    submitting.value = false
  }
}

async function removeCost(id: number) {
  if (!confirm('Remove this cost entry?')) return
  try {
    await acceptQueued(() => profitStore.deleteProductCost(id))
    if (selectedProductId.value) await profitStore.fetchCurrentCost(selectedProductId.value)
  } catch (error) {
    costError.value = errorMessageOf(error)
  }
}

async function addComponent() {
  const name = newComponentName.value.trim()
  if (!name) return
  componentError.value = ''
  try {
    await acceptQueued(() => profitStore.createCostComponent(name))
    newComponentName.value = ''
    showAddComponent.value = false
  } catch (error) {
    componentError.value = errorMessageOf(error)
  }
}

onMounted(async () => {
  await Promise.all([productsStore.fetchProducts(), profitStore.fetchCostComponents()])
})
</script>

<style scoped>
.cost-management-page {
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #111827;
  margin: 0;
}

.subtitle {
  color: #64748b;
  margin-top: 0.25rem;
  max-width: 60ch;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-primary {
  background: #2563eb;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6b7280;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.btn-link-danger {
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  font-size: 0.875rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.product-select {
  max-width: 320px;
  margin-bottom: 1.5rem;
}

.filter-select,
.filter-input {
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  background: white;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #64748b;
  background: white;
  border-radius: 12px;
}

.cost-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.current-cost-card,
.add-cost-form,
.history-section,
.production-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.current-cost-card h3,
.add-cost-form h3,
.history-section h3,
.production-section h3 {
  margin: 0 0 1rem 0;
  color: #0f172a;
}

.source-line {
  margin: 0 0 0.75rem 0;
  color: #334155;
  font-size: 0.875rem;
}

.fallback-note {
  background: #fef3c7;
  border: 1px solid #fde68a;
  color: #92400e;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.missing-note {
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.override-note {
  margin: 1rem 0 0 0;
  color: #64748b;
  font-size: 0.8125rem;
}

.used-badge {
  background: #dcfce7;
  color: #166534;
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.cost-breakdown {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cost-line {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.cost-line small {
  color: #94a3b8;
}

.cost-total {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid #e2e8f0;
  font-weight: 700;
  font-size: 1.125rem;
  color: #0f172a;
}

.form-hint {
  color: #64748b;
  font-size: 0.875rem;
  margin: -0.5rem 0 1rem 0;
}

.form-row {
  display: flex;
  gap: 1rem;
  align-items: end;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
}

.empty-row {
  text-align: center;
  color: #94a3b8;
  padding: 2rem !important;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  width: min(400px, 90vw);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
.form-error {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}
</style>
