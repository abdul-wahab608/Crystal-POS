<template>
  <div class="products-page">
    <div class="page-header">
      <h1 class="page-title">Products</h1>
      <div class="header-actions">
        <ExportButton entityType="products" />
        <button v-if="authStore.canImport" class="btn-secondary" @click="showImportWizard = true">Import</button>
        <button class="btn-primary" @click="openForm(null)">Add Product</button>
      </div>
    </div>

    <BatchActionsToolbar
      entityType="products"
      entityLabel="product"
      :showActivate="false"
      :showDeactivate="false"
      @action-complete="handleBatchActionComplete"
    />

    <p v-if="pageError || store.error" class="form-error">{{ pageError || store.error }}</p>

    <div class="filters-section">
      <input v-model="searchTerm" type="text" placeholder="Search products..." class="search-input" />
      <SearchableSelect id="unit-filter" v-model="unitFilter" :options="unitFilterOptions" placeholder="All units" class="filter-select" />
      <SearchableSelect id="size-range-filter" v-model="sizeRangeFilter" :options="sizeRangeFilterOptions" placeholder="All size ranges" class="filter-select" />
      <SearchableSelect id="color-filter" v-model="colorFilter" :options="colorFilterOptions" placeholder="All colors" class="filter-select" />
    </div>

    <div v-if="store.loading && !store.products.length" class="loading-state">Loading products...</div>

    <div v-else class="table-container">
      <table class="products-table">
        <thead>
          <tr>
            <th class="checkbox-col">
              <SelectAllCheckbox entityType="products" :allIds="pageIds" />
            </th>
            <th>Name</th>
            <th>Unit</th>
            <th>Size ranges</th>
            <th>Colors</th>
            <th class="num">Total quantity</th>
            <th v-if="authStore.isManager" class="num">Cost per unit</th>
            <th v-if="authStore.isManager">Cost source</th>
            <th>Type</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="product in pageItems" :key="product.id">
          <tr>
            <td class="checkbox-col">
              <SelectableCheckbox entityType="products" :id="product.id" />
            </td>
            <td>
              {{ product.name }}
              <button type="button" class="stock-toggle" :aria-expanded="expandedId === product.id" @click="toggleStock(product)">{{ expandedId === product.id ? 'Hide stock' : 'Stock by size and color' }}</button>
            </td>
            <td><span class="unit-badge">{{ product.unit }}</span></td>
            <td>{{ sizeRangeNames(product).join(', ') || '—' }}</td>
            <td>{{ colorNames(product).join(', ') || '—' }}</td>
            <td class="num">{{ Number(product.quantity) }} {{ product.unit }}</td>
            <td v-if="authStore.isManager" class="num">{{ Number(product.cop) > 0 ? Number(product.cop).toFixed(2) : '—' }}</td>
            <td v-if="authStore.isManager">{{ costSourceLabel(product.cost_source) }}</td>
            <td>{{ product.product_type === 'PURCHASED' ? 'Purchased' : 'Manufactured' }}</td>
            <td>
              <div class="actions">
                <button class="action-btn edit" @click="openForm(product)">Edit</button>
                <button v-if="authStore.isManager" class="action-btn delete" @click="removeProduct(product)">Delete</button>
              </div>
            </td>
          </tr>
          <tr v-if="expandedId === product.id" class="stock-row">
            <td :colspan="columnCount">
              <table v-if="stockGridFor(product).sizes.length" class="stock-grid">
                <thead>
                  <tr>
                    <th>Size range</th>
                    <th v-for="color in stockGridFor(product).colors" :key="color.id" class="num">{{ color.name }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="size in stockGridFor(product).sizes" :key="size.id">
                    <td>{{ size.name }}</td>
                    <td v-for="color in stockGridFor(product).colors" :key="color.id" class="num">
                      {{ stockGridFor(product).cells[cellKey(size.id, color.id)] ?? '—' }}<span v-if="stockGridFor(product).cells[cellKey(size.id, color.id)] !== undefined"> {{ product.unit }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="muted">No size ranges or stock recorded for this product.</p>
            </td>
          </tr>
          </template>
          <tr v-if="!filteredProducts.length">
            <td :colspan="columnCount" class="empty">No products match these filters.</td>
          </tr>
        </tbody>
      </table>
      <PaginationBar
        :page="page"
        :totalPages="totalPages"
        :total="total"
        :pageSize="pageSize"
        @update:page="goTo"
        @update:pageSize="setPageSize"
      />
    </div>

    <ProductFormModal v-if="formOpen" :product="editingProduct" @close="closeForm" />

    <ImportWizard v-if="showImportWizard" entityType="products" @close="handleImportClose" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useProductsStore } from '../stores/products'
import { useSizeRangeStore } from '../stores/sizeRange'
import { useColorStore } from '../stores/color'
import { useAuthStore } from '../../../shared/stores/auth'
import { useUnitsStore } from '../../../shared/stores/units'
import ImportWizard from '../../../shared/components/ImportWizard/ImportWizard.vue'
import ExportButton from '../../../shared/components/ExportButton.vue'
import BatchActionsToolbar from '../../../shared/components/BatchActionsToolbar.vue'
import SelectAllCheckbox from '../../../shared/components/SelectAllCheckbox.vue'
import SelectableCheckbox from '../../../shared/components/SelectableCheckbox.vue'
import SearchableSelect from '../../../shared/components/SearchableSelect.vue'
import PaginationBar from '../../../shared/components/PaginationBar.vue'
import { usePagination } from '../../../shared/composables/usePagination'
import ProductFormModal from '../components/ProductFormModal.vue'
import { acceptQueued } from '../../../shared/utils/queuedWrite'
import { buildStockGrid, cellKey, type StockGrid } from '../utils/stockGrid'
import type { Product } from '../types'
import { costSourceLabel } from '../../profit/utils/costSource'

const store = useProductsStore()
const sizeRangeStore = useSizeRangeStore()
const colorStore = useColorStore()
const unitsStore = useUnitsStore()
const authStore = useAuthStore()

const searchTerm = ref('')
const unitFilter = ref<string | number>('')
const sizeRangeFilter = ref<string | number>('')
const colorFilter = ref<string | number>('')
const formOpen = ref(false)
const editingProduct = ref<Product | null>(null)
const showImportWizard = ref(false)
const pageError = ref('')
const expandedId = ref<number | null>(null)

const columnCount = computed(() => (authStore.isManager ? 10 : 8))

function toggleStock(product: Product) {
  expandedId.value = expandedId.value === product.id ? null : product.id
}

function stockGridFor(product: Product): StockGrid {
  return buildStockGrid(product, id => sizeRangeStore.sizeRanges.find(sr => sr.id === id)?.name ?? `#${id}`)
}

onMounted(() => {
  store.fetchProducts()
  sizeRangeStore.fetchSizeRanges()
  colorStore.fetchColors()
  unitsStore.fetchUnits().catch(() => { pageError.value = 'Could not load units.' })
})

const unitFilterOptions = computed(() => [{ value: '', label: 'All units' }, ...unitsStore.unitOptions])
const sizeRangeFilterOptions = computed(() => [
  { value: '', label: 'All size ranges' },
  ...sizeRangeStore.sizeRanges.map(sr => ({ value: sr.id, label: sr.name })),
])
const colorFilterOptions = computed(() => [
  { value: '', label: 'All colors' },
  ...colorStore.colors.map(c => ({ value: c.id, label: c.name })),
])

const filteredProducts = computed<Product[]>(() => {
  const term = searchTerm.value.trim().toLowerCase()
  const sizeId = sizeRangeFilter.value === '' ? null : Number(sizeRangeFilter.value)
  const colorId = colorFilter.value === '' ? null : Number(colorFilter.value)
  return store.products.filter(p => {
    if (term && !p.name.toLowerCase().includes(term)) return false
    if (unitFilter.value && p.unit !== unitFilter.value) return false
    if (sizeId !== null && !p.size_ranges.includes(sizeId) && !p.variants.some(v => v.size_range === sizeId)) return false
    if (colorId !== null && !p.variants.some(v => v.color === colorId)) return false
    return true
  })
})

const { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset } = usePagination(filteredProducts)
const pageIds = computed(() => pageItems.value.map(p => p.id))

watch([searchTerm, unitFilter, sizeRangeFilter, colorFilter], reset)

function sizeRangeNames(product: Product): string[] {
  return product.size_ranges
    .map(id => sizeRangeStore.sizeRanges.find(sr => sr.id === id)?.name)
    .filter((name): name is string => Boolean(name))
}

function colorNames(product: Product): string[] {
  return [...new Set(product.variants.map(v => v.color_name))]
}

function openForm(product: Product | null) {
  editingProduct.value = product
  formOpen.value = true
}

function closeForm() {
  formOpen.value = false
  editingProduct.value = null
}

async function removeProduct(product: Product) {
  if (!confirm(`Delete ${product.name}?`)) return
  pageError.value = ''
  try {
    await acceptQueued(() => store.deleteProduct(product.id))
  } catch (e: any) {
    pageError.value = e.response?.data?.error || e.response?.data?.detail || 'Could not delete the product.'
  }
}

function handleImportClose() {
  showImportWizard.value = false
  store.fetchProducts()
}

function handleBatchActionComplete() {
  store.fetchProducts()
}
</script>

<style scoped>
.products-page { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 1.5rem; font-weight: 700; }
.header-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.filters-section { display: grid; grid-template-columns: minmax(200px, 2fr) repeat(3, minmax(160px, 1fr)); gap: 10px; margin: 16px 0; }
.search-input { width: 100%; }
.table-container { overflow-x: auto; }
.products-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.products-table th, .products-table td { padding: 8px 10px; border-bottom: 1px solid #e5e7eb; text-align: left; vertical-align: top; }
.products-table th.num, .products-table td.num { text-align: right; white-space: nowrap; }
.products-table .empty { text-align: center; color: #6b7280; }
.checkbox-col { width: 36px; }
.unit-badge { background: #f3f4f6; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
.actions { display: flex; gap: 8px; }
.action-btn { background: none; border: none; cursor: pointer; font-size: 0.8125rem; }
.action-btn.edit { color: #4338ca; }
.action-btn.delete { color: #b91c1c; }
.stock-toggle { display: block; margin-top: 4px; background: none; border: none; color: #4338ca; cursor: pointer; font-size: 0.75rem; padding: 0; }
.stock-row > td { background: #f9fafb; }
.stock-grid { border-collapse: collapse; font-size: 0.8125rem; }
.stock-grid th, .stock-grid td { padding: 4px 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }
.stock-grid .num { text-align: right; white-space: nowrap; }
.muted { color: #6b7280; }
.form-error { color: #b91c1c; margin: 8px 0; }
.loading-state { padding: 24px; color: #6b7280; }
@media (max-width: 900px) {
  .filters-section { grid-template-columns: 1fr 1fr; }
}
</style>
