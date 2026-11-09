<template>
  <div class="bill-wrap">
    <div class="bill-actions no-print">
      <button type="button" class="primary-btn" @click="printBill">Print</button>
      <button type="button" class="secondary-btn" @click="emit('close')">Close</button>
    </div>
    <article class="bill" aria-label="Bill">
      <header class="bill-head">
        <div>
          <h2>{{ sale.bill_no }}</h2>
          <p>{{ formatDate(sale.date) }}</p>
        </div>
        <div class="bill-status">
          <span class="badge" :class="sale.payment_status.toLowerCase()">{{ paymentStatusLabel(sale.payment_status) }}</span>
        </div>
      </header>
      <section class="bill-parties">
        <div>
          <span class="muted">Bill to</span>
          <strong>{{ sale.customer_name }}</strong>
          <span v-if="sale.customer_city">{{ sale.customer_city }}</span>
        </div>
      </section>
      <table class="bill-table">
        <thead>
          <tr>
            <th>Product</th>
            <th>Size</th>
            <th>Color</th>
            <th class="num">Quantity</th>
            <th class="num">Unit price</th>
            <th class="num">Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in sale.sale_items" :key="item.id">
            <td>{{ item.product_name }}</td>
            <td>{{ item.size_range_name }}</td>
            <td>{{ item.color_name }}</td>
            <td class="num">{{ Number(item.quantity).toFixed(2) }} {{ unitOf(item.product) }}</td>
            <td class="num">{{ formatMoney(Number(item.unit_price)) }}</td>
            <td class="num">{{ formatMoney(Number(item.subtotal)) }}</td>
          </tr>
        </tbody>
      </table>
      <dl class="bill-totals">
        <div><dt>Total</dt><dd>{{ formatMoney(Number(sale.total_amount)) }}</dd></div>
        <div><dt>Received</dt><dd>{{ formatMoney(Number(sale.amount_paid)) }}</dd></div>
        <div><dt>Balance</dt><dd>{{ formatMoney(Number(sale.balance)) }}</dd></div>
      </dl>
    </article>
  </div>
</template>

<script setup lang="ts">
import type { Sale } from '../types'
import { useAuthStore } from '../../../shared/stores/auth'
import { paymentStatusLabel } from '../../../shared/utils/statusLabels'

const auth = useAuthStore()

const props = defineProps<{ sale: Sale; unitByProductId?: Record<number, string> }>()
const emit = defineEmits<{ close: [] }>()

const unitOf = (productId: number) => props.unitByProductId?.[productId] ?? ''

const formatDate = (value: string) => new Date(value).toLocaleString('en-PK')

const formatMoney = (value: number) => `₨${value.toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

const printBill = () => window.print()
</script>

<style scoped>
.bill-wrap { display: flex; flex-direction: column; gap: 1rem; }
.bill-actions { display: flex; justify-content: flex-end; gap: 0.5rem; }
.bill { background: #fff; color: #111; padding: 1.5rem; border: 1px solid #ddd; border-radius: 8px; }
.bill-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.bill-head h2 { margin: 0; font-size: 1.4rem; }
.bill-head p { margin: 0.25rem 0 0; color: #555; }
.bill-parties { margin: 1rem 0; display: flex; flex-direction: column; }
.muted { color: #666; font-size: 0.8rem; display: block; }
.bill-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.bill-table th, .bill-table td { padding: 0.45rem 0.5rem; border-bottom: 1px solid #eee; text-align: left; }
.bill-table .num { text-align: right; font-variant-numeric: tabular-nums; }
.bill-totals { margin: 1rem 0 0; display: flex; flex-direction: column; align-items: flex-end; gap: 0.25rem; }
.bill-totals div { display: flex; gap: 2rem; }
.bill-totals dt { color: #555; }
.bill-totals dd { margin: 0; min-width: 8rem; text-align: right; font-variant-numeric: tabular-nums; }
.badge { padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; background: #eee; }
.badge.paid { background: #d1fae5; color: #065f46; }
.badge.partial { background: #fef3c7; color: #92400e; }
.badge.unpaid { background: #fee2e2; color: #991b1b; }
@media print {
  body * { visibility: hidden; }
  .bill, .bill * { visibility: visible; }
  .bill { position: absolute; left: 0; top: 0; width: 100%; border: none; }
  .no-print { display: none !important; }
}
</style>
