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

    <div class="filter-group product-select">
      <label>Product</label>
      <select v-model.number="selectedProductId" class="filter-select">
        <option :value="null">Select a product...</option>
        <option v-for="p in productsStore.products" :key="p.id" :value="p.id">{{ p.name }} ({{ p.unit }})</option>
      </select>
    </div>

    <div v-if="!selectedProductId" class="empty-state">
      Pick a product above to view or edit its cost breakdown.
    </div>

    <div v-else class="cost-content">
      <div class="current-cost-card">
        <h3>Current Effective Cost (as of {{ today }})</h3>
        <div v-if="profitStore.currentCost?.using_fallback_cop" class="fallback-note">
          No cost history recorded yet for this product — showing its Cost of Production (₨{{ formatMoney(totalPerDozen) }}/dozen) as a fallback. Add a cost below to start tracking real components.
        </div>
        <div v-else class="cost-breakdown">
          <div v-for="c in profitStore.currentCost?.components || []" :key="c.component_type" class="cost-line">
            <span>{{ c.component_type_name }}</span>
            <span>₨{{ formatMoney(c.amount_per_dozen) }}/dz <small>(since {{ c.valid_from }})</small></span>
          </div>
        </div>
        <div class="cost-total">
          Total: ₨{{ formatMoney(totalPerDozen) }}/dozen &nbsp;·&nbsp; ₨{{ formatMoney(totalPerDozen / 12) }}/piece
        </div>
      </div>

      <form v-if="authStore.isManager" class="add-cost-form" @submit.prevent="submitCost">
        <h3>Add a Cost Entry</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Component</label>
            <select v-model.number="form.component_type" required class="filter-select">
              <option v-for="c in profitStore.costComponents" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Amount per dozen (₨)</label>
            <input v-model.number="form.amount_per_dozen" type="number" min="0" step="0.01" required class="filter-input" />
          </div>
          <div class="form-group">
            <label>Effective from</label>
            <input v-model="form.valid_from" type="date" required class="filter-input" />
          </div>
          <button type="submit" class="btn-primary" :disabled="submitting || !form.component_type">Save</button>
        </div>
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
            <tr v-for="c in profitStore.productCosts" :key="c.id">
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
      </div>
    </div>

    <div v-if="showAddComponent" class="modal-overlay" @click.self="showAddComponent = false">
      <div class="modal-card">
        <h3>Add Custom Cost Field</h3>
        <p class="form-hint">e.g. Packaging, Transport, Overheads — it becomes available for every product.</p>
        <input v-model="newComponentName" type="text" placeholder="Field name" class="filter-input" @keyup.enter="addComponent" />
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

const profitStore = useProfitStore()
const productsStore = useProductsStore()
const authStore = useAuthStore()

const selectedProductId = ref<number | null>(null)
const showAddComponent = ref(false)
const newComponentName = ref('')
const submitting = ref(false)
const today = new Date().toISOString().slice(0, 10)

const form = ref<{ component_type: number | null; amount_per_dozen: number; valid_from: string }>({
  component_type: null,
  amount_per_dozen: 0,
  valid_from: today,
})

const totalPerDozen = computed(() => Number(profitStore.currentCost?.total_per_dozen || 0))

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
  try {
    await profitStore.addProductCost({
      product: selectedProductId.value,
      component_type: form.value.component_type,
      amount_per_dozen: form.value.amount_per_dozen,
      valid_from: form.value.valid_from,
    })
    await loadForProduct()
    form.value.amount_per_dozen = 0
  } finally {
    submitting.value = false
  }
}

async function removeCost(id: number) {
  if (!confirm('Remove this cost entry?')) return
  await profitStore.deleteProductCost(id)
  if (selectedProductId.value) await profitStore.fetchCurrentCost(selectedProductId.value)
}

async function addComponent() {
  const name = newComponentName.value.trim()
  if (!name) return
  await profitStore.createCostComponent(name)
  newComponentName.value = ''
  showAddComponent.value = false
}

onMounted(async () => {
  await Promise.all([productsStore.fetchProducts(), profitStore.fetchCostComponents()])
  if (form.value.component_type === null && profitStore.costComponents.length) {
    form.value.component_type = profitStore.costComponents[0].id
  }
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
.history-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.current-cost-card h3,
.add-cost-form h3,
.history-section h3 {
  margin: 0 0 1rem 0;
  color: #0f172a;
}

.fallback-note {
  background: #fef3c7;
  border: 1px solid #fde68a;
  color: #92400e;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
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
</style>
