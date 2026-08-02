<template>
  <div class="customer-sales-report">
    <h1 class="text-2xl font-bold mb-4">Customer Sales Report</h1>
    <form class="flex gap-4 mb-4 flex-wrap" @submit.prevent="fetchReport">
      <input v-model="filters.start_date" type="date" class="input" />
      <input v-model="filters.end_date" type="date" class="input" />
      <select v-model="filters.product" class="input">
        <option value="">All Products</option>
        <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
      <select v-model="filters.size_range" class="input">
        <option value="">All Sizes</option>
        <option v-for="sr in sizeRanges" :key="sr.id" :value="sr.id">{{ sr.name }}</option>
      </select>
      <select v-model="filters.color" class="input">
        <option value="">All Colors</option>
        <option v-for="c in colors" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <button type="submit" class="btn">Filter</button>
    </form>
    <table class="table-auto w-full border">
      <thead>
        <tr>
          <th class="border px-2 py-1">Customer</th>
          <th class="border px-2 py-1">Total Sales</th>
          <th class="border px-2 py-1">Total Quantity</th>
          <th class="border px-2 py-1">Sale Count</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in report" :key="row.customer_id">
          <td class="border px-2 py-1">{{ row.customer_name }}</td>
          <td class="border px-2 py-1">₨{{ row.total_sales.toFixed(2) }}</td>
          <td class="border px-2 py-1">{{ row.total_quantity }}</td>
          <td class="border px-2 py-1">{{ row.sale_count }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="loading" class="mt-4">Loading...</div>
    <div v-if="error" class="text-red-500 mt-4">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from '../../../shared/api/axios'

const report = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const filters = ref({ start_date: '', end_date: '', product: '', size_range: '', color: '' })
const products = ref<any[]>([])
const sizeRanges = ref<any[]>([])
const colors = ref<any[]>([])

async function fetchReport() {
  loading.value = true
  error.value = null
  try {
    const params: any = {}
    if (filters.value.start_date) params.start_date = filters.value.start_date
    if (filters.value.end_date) params.end_date = filters.value.end_date
    if (filters.value.product) params.product = filters.value.product
    if (filters.value.size_range) params.size_range = filters.value.size_range
    if (filters.value.color) params.color = filters.value.color
    const res = await axios.get('/reports/customer-sales/', { params })
    report.value = res.data
  } catch (e: any) {
    error.value = e.message || 'Failed to fetch report'
  } finally {
    loading.value = false
  }
}

async function fetchFilters() {
  const [prods, sizes, cols] = await Promise.all([
    axios.get('/products/'),
    axios.get('/products/size-ranges/'),
    axios.get('/products/colors/')
  ])
  products.value = prods.data
  sizeRanges.value = sizes.data
  colors.value = cols.data
}

onMounted(() => {
  fetchFilters()
  fetchReport()
})
</script>

<style scoped>
.input { border: 1px solid #ccc; padding: 0.4rem; border-radius: 4px; }
.btn { background: #2563eb; color: #fff; padding: 0.3rem 0.7rem; border-radius: 4px; }
.table-auto th, .table-auto td { text-align: left; }
</style>
