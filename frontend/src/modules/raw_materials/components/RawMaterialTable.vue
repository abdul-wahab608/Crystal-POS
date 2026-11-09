<template>
  <div class="table-container">
    <table v-if="materials.length" class="materials-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Unit</th>
          <th class="num">On hand</th>
          <th class="num">Reorder level</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="material in materials" :key="material.id">
          <td>{{ material.name }}</td>
          <td>{{ material.unit }}</td>
          <td class="num" :class="{ 'is-low': material.needs_reorder }">{{ Number(material.quantity).toFixed(2) }} {{ material.unit }}</td>
          <td class="num">{{ Number(material.reorder_level).toFixed(2) }} {{ material.unit }}</td>
          <td>
            <span :class="material.needs_reorder ? 'badge badge-low' : 'badge badge-ok'">
              {{ material.needs_reorder ? 'Low stock' : 'In stock' }}
            </span>
          </td>
          <td class="actions">
            <button class="link-btn" @click="$emit('edit', material)">Edit</button>
            <button class="link-btn" @click="$emit('usage', material)">Record usage</button>
            <button class="link-btn" @click="$emit('history', material)">History</button>
            <button class="link-btn danger" @click="$emit('delete', material)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty-state">No raw materials yet.</p>
  </div>
</template>

<script setup lang="ts">
import type { RawMaterial } from '../types'

defineProps<{ materials: RawMaterial[] }>()
defineEmits<{ edit: [material: RawMaterial]; usage: [material: RawMaterial]; history: [material: RawMaterial]; delete: [material: RawMaterial] }>()
</script>

<style scoped>
.table-container { background: white; border-radius: 0.5rem; overflow-x: auto; border: 1px solid #e5e7eb; }
.materials-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.materials-table th, .materials-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: left; }
.materials-table th { background: #f9fafb; font-weight: 600; color: #374151; }
.num { text-align: right; white-space: nowrap; }
.is-low { color: #b91c1c; font-weight: 600; }
.badge { padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; }
.badge-low { background: #fee2e2; color: #991b1b; }
.badge-ok { background: #dcfce7; color: #166534; }
.actions { white-space: nowrap; }
.link-btn { background: none; border: none; color: #2563eb; cursor: pointer; margin-right: 0.75rem; font-size: 0.875rem; }
.link-btn.danger { color: #b91c1c; }
.empty-state { padding: 2rem; text-align: center; color: #6b7280; }
</style>
