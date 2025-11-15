<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ material.name }} - History</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-content">
        <div class="tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'usage' }"
            @click="activeTab = 'usage'"
          >
            Usage History
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'purchase' }"
            @click="activeTab = 'purchase'"
          >
            Purchase History
          </button>
        </div>
        
        <div v-if="activeTab === 'usage'" class="tab-content">
          <div v-if="store.usageHistory.length === 0" class="empty-state">
            No usage records found.
          </div>
          <div v-else class="history-list">
            <div v-for="usage in store.usageHistory" :key="usage.id" class="history-item">
              <div class="history-header">
                <span class="quantity">{{ usage.quantity_used }} {{ material.unit }}</span>
                <span class="date">{{ formatDate(usage.date_used) }}</span>
              </div>
              <div v-if="usage.reference" class="reference">
                Reference: {{ usage.reference }}
              </div>
              <div v-if="usage.notes" class="notes">
                {{ usage.notes }}
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="activeTab === 'purchase'" class="tab-content">
          <div v-if="store.purchaseHistory.length === 0" class="empty-state">
            No purchase records found.
          </div>
          <div v-else class="history-list">
            <div v-for="purchase in store.purchaseHistory" :key="purchase.id" class="history-item">
              <div class="history-header">
                <span class="quantity">{{ purchase.quantity_purchased }} {{ material.unit }}</span>
                <span class="amount">₨{{ purchase.total_amount.toFixed(2) }}</span>
                <span class="date">{{ formatDate(purchase.purchase_date) }}</span>
              </div>
              <div v-if="purchase.supplier" class="supplier">
                Supplier: {{ purchase.supplier }}
              </div>
              <div v-if="purchase.invoice_number" class="invoice">
                Invoice: {{ purchase.invoice_number }}
              </div>
              <div v-if="purchase.notes" class="notes">
                {{ purchase.notes }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRawMaterialsStore } from '../stores/raw_materials'
import type { RawMaterial } from '../types'

const props = defineProps<{
  material: RawMaterial
}>()

const emit = defineEmits<{
  close: []
}>()

const store = useRawMaterialsStore()
const activeTab = ref<'usage' | 'purchase'>('usage')

onMounted(() => {
  store.fetchUsageHistory(props.material.id)
  store.fetchPurchaseHistory(props.material.id)
})

function formatDate(date: string) {
  return new Date(date).toLocaleString()
}
</script>

<style scoped>
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

.modal {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 800px;
  max-height: 80vh;
  margin: 1rem;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
}

.modal-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
}

.tab-btn {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  border-bottom: 2px solid transparent;
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.empty-state {
  text-align: center;
  color: #6b7280;
  padding: 2rem;
}

.history-list {
  space-y: 1rem;
}

.history-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.quantity {
  font-weight: 600;
  color: #111827;
}

.amount {
  font-weight: 600;
  color: #059669;
}

.date {
  font-size: 0.875rem;
  color: #6b7280;
}

.reference, .supplier, .invoice {
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 0.25rem;
}

.notes {
  font-size: 0.875rem;
  color: #6b7280;
  font-style: italic;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
}
</style> 