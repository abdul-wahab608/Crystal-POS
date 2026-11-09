<template>
  <div class="table-container">
    <table v-if="vendors.length" class="vendors-table">
      <thead>
        <tr>
          <th>Vendor</th>
          <th>Contact</th>
          <th>City</th>
          <th class="num">Balance owed</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="vendor in vendors" :key="vendor.id" :class="{ expanded: expandedId === vendor.id }">
          <td>{{ vendor.name }}</td>
          <td>{{ vendor.contact_person || '-' }}<span v-if="vendor.phone" class="muted"> · {{ vendor.phone }}</span></td>
          <td>{{ vendor.city || '-' }}</td>
          <td class="num" :class="{ owed: Number(vendor.balance) > 0 }">{{ Number(vendor.balance).toFixed(2) }}</td>
          <td>
            <span :class="vendor.is_active ? 'badge badge-ok' : 'badge badge-off'">{{ vendor.is_active ? 'Active' : 'Inactive' }}</span>
          </td>
          <td class="actions">
            <button class="link-btn" :aria-expanded="expandedId === vendor.id" @click="$emit('toggle-ledger', vendor)">
              {{ expandedId === vendor.id ? 'Hide ledger' : 'Ledger' }}
            </button>
            <button class="link-btn" @click="$emit('edit', vendor)">Edit</button>
            <button class="link-btn danger" @click="$emit('delete', vendor)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty-state">No vendors match.</p>
  </div>
</template>

<script setup lang="ts">
import type { Vendor } from '../types'

defineProps<{ vendors: Vendor[]; expandedId: number | null }>()
defineEmits<{ 'toggle-ledger': [vendor: Vendor]; edit: [vendor: Vendor]; delete: [vendor: Vendor] }>()
</script>

<style scoped>
.table-container { background: white; border-radius: 0.5rem; border: 1px solid #e5e7eb; overflow-x: auto; }
.vendors-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.vendors-table th, .vendors-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: left; }
.vendors-table th { background: #f9fafb; font-weight: 600; }
.num { text-align: right; white-space: nowrap; }
.owed { color: #b91c1c; font-weight: 600; }
.muted { color: #6b7280; }
.badge { padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; }
.badge-ok { background: #dcfce7; color: #166534; }
.badge-off { background: #e5e7eb; color: #374151; }
.actions { white-space: nowrap; }
.link-btn { background: none; border: none; color: #2563eb; cursor: pointer; margin-right: 0.75rem; font-size: 0.875rem; }
.link-btn.danger { color: #b91c1c; }
.empty-state { padding: 2rem; text-align: center; color: #6b7280; }
</style>
