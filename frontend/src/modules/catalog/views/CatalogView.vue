<template>
  <div class="catalog-page">
    <div class="page-header">
      <h1 class="page-title">Catalog</h1>
      <p class="page-subtitle">Units, size ranges and colors. Products are built from these.</p>
    </div>

    <nav class="tabs" role="tablist">
      <button
        v-for="t in tabs"
        :key="t.id"
        type="button"
        role="tab"
        :aria-selected="tab === t.id"
        :class="['tab', { active: tab === t.id }]"
        @click="tab = t.id"
      >
        {{ t.label }}
      </button>
    </nav>

    <UnitsPanel v-if="tab === 'units'" />

    <NamedListPanel
      v-else-if="tab === 'sizes'"
      label="size range"
      plural="size ranges"
      :items="sizeRangeStore.sizeRanges"
      :error="sizeRangeStore.error ?? ''"
      @add="sizeRangeStore.addSizeRange"
      @rename="sizeRangeStore.renameSizeRange"
      @remove="sizeRangeStore.deleteSizeRange"
    />

    <NamedListPanel
      v-else
      label="color"
      plural="colors"
      :items="colorStore.colors"
      :error="colorStore.error ?? ''"
      @add="colorStore.addColor"
      @rename="colorStore.renameColor"
      @remove="colorStore.deleteColor"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSizeRangeStore } from '../../products/stores/sizeRange'
import { useColorStore } from '../../products/stores/color'
import UnitsPanel from '../components/UnitsPanel.vue'
import NamedListPanel from '../components/NamedListPanel.vue'

type TabId = 'units' | 'sizes' | 'colors'

const tabs: { id: TabId; label: string }[] = [
  { id: 'units', label: 'Units' },
  { id: 'sizes', label: 'Size Ranges' },
  { id: 'colors', label: 'Colors' },
]

const tab = ref<TabId>('units')
const sizeRangeStore = useSizeRangeStore()
const colorStore = useColorStore()

onMounted(() => {
  sizeRangeStore.fetchSizeRanges()
  colorStore.fetchColors()
})
</script>

<style scoped>
.catalog-page { padding: 24px; max-width: 900px; }
.page-header { margin-bottom: 16px; }
.page-title { font-size: 1.5rem; font-weight: 700; }
.page-subtitle { color: #6b7280; margin-top: 4px; }
.tabs { display: flex; gap: 4px; border-bottom: 1px solid #e5e7eb; margin-bottom: 16px; }
.tab { padding: 8px 14px; background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; color: #6b7280; font-weight: 500; }
.tab.active { color: #4338ca; border-bottom-color: #4338ca; }
</style>
