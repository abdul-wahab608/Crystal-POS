<template>
  <div class="table-container">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading raw materials...</p>
    </div>
    
    <div v-else>
      <table class="materials-table">
        <thead>
          <tr>
            <th class="checkbox-col">
              <SelectAllCheckbox 
                entityType="raw_materials" 
                :allIds="materials.map(m => m.id)" 
              />
            </th>
            <th>Name</th>
            <th>Unit</th>
            <th>Unit Price</th>
            <th>Available Stock</th>
            <th>Reorder Level</th>
            <th>Supplier</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="mat in materials" :key="mat.id" class="table-row">
            <td class="checkbox-col">
              <SelectableCheckbox entityType="raw_materials" :id="mat.id" />
            </td>
            <td>{{ mat.name }}</td>
            <td>{{ mat.unit }}</td>
            <td>{{ mat.unit_price ? Number(mat.unit_price).toFixed(2) : '0.00' }}</td>
            <td :class="{ 'low-stock': mat.needs_reorder }">
              {{ mat.available_stock ? Number(mat.available_stock).toFixed(2) : '0.00' }}
            </td>
            <td>{{ mat.reorder_level ? Number(mat.reorder_level).toFixed(2) : '0.00' }}</td>
            <td>{{ mat.supplier || '-' }}</td>
            <td>
              <span :class="getStatusClass(mat.needs_reorder)">
                {{ mat.needs_reorder ? 'Low Stock' : 'In Stock' }}
              </span>
            </td>
            <td>
              <div class="actions">
                <button class="action-btn edit" @click="$emit('edit', mat)" title="Edit">
                  ✏️
                </button>
                <button class="action-btn usage" @click="$emit('usage', mat)" title="Record Usage">
                  📉
                </button>
                <button class="action-btn purchase" @click="$emit('purchase', mat)" title="Record Purchase">
                  📈
                </button>
                <button class="action-btn history" @click="$emit('history', mat)" title="View History">
                  📋
                </button>
                <button class="action-btn delete" @click="$emit('delete', mat.id)" title="Delete">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="materials.length === 0" class="empty-state">
        <p>No raw materials found.</p>
        <button class="btn-primary" @click="$emit('refresh')">Refresh</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RawMaterial } from '../types'
import SelectAllCheckbox from '../../../shared/components/SelectAllCheckbox.vue'
import SelectableCheckbox from '../../../shared/components/SelectableCheckbox.vue'

const props = defineProps<{ 
  materials: RawMaterial[]
  loading?: boolean
}>()

const emit = defineEmits<{
  refresh: []
  edit: [material: RawMaterial]
  delete: [id: number]
  usage: [material: RawMaterial]
  purchase: [material: RawMaterial]
  history: [material: RawMaterial]
}>()

function getStatusClass(needsReorder: boolean) {
  return needsReorder ? 'status-low' : 'status-ok'
}
</script>

<style scoped>
.table-container {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 2rem;
}

.loading-state {
  text-align: center;
  padding: 3rem;
}

.spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.materials-table {
  width: 100%;
  border-collapse: collapse;
}

.materials-table th,
.materials-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.materials-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.checkbox-col {
  width: 40px;
  text-align: center;
}

.table-row:hover {
  background: #f9fafb;
}

.low-stock {
  color: #dc2626;
  font-weight: bold;
}

.status-ok {
  background: #d1fae5;
  color: #065f46;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-low {
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
}

.action-btn.edit:hover {
  background: #dbeafe;
}

.action-btn.usage:hover {
  background: #fef3c7;
}

.action-btn.purchase:hover {
  background: #d1fae5;
}

.action-btn.history:hover {
  background: #f3e8ff;
}

.action-btn.delete:hover {
  background: #fee2e2;
}

.empty-state {
  text-align: center;
  color: #6b7280;
  padding: 3rem;
}

.btn-primary {
  background: #2563eb;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  margin-top: 1rem;
}

.btn-primary:hover {
  background: #1d4ed8;
}
</style> 