<template>
  <div ref="root" class="searchable-select" :class="{ 'is-open': open }">
    <input
      :id="id"
      ref="input"
      type="text"
      role="combobox"
      autocomplete="off"
      :aria-expanded="open"
      :placeholder="placeholder"
      :required="required && !modelValue"
      :disabled="disabled"
      :value="open ? query : selectedLabel"
      class="form-input searchable-select-input"
      @focus="openList"
      @input="onInput"
      @keydown.down.prevent="move(1)"
      @keydown.up.prevent="move(-1)"
      @keydown.enter.prevent="pickActive"
      @keydown.esc="close"
      @blur="onBlur"
    />
    <ul v-if="open" class="searchable-select-list" role="listbox">
      <li
        v-for="(opt, idx) in filtered"
        :key="String(opt.value)"
        role="option"
        :aria-selected="opt.value === modelValue"
        :class="{ 'is-active': idx === activeIndex, 'is-selected': opt.value === modelValue }"
        @mousedown.prevent="select(opt.value)"
        @mouseenter="activeIndex = idx"
      >
        {{ opt.label }}
      </li>
      <li v-if="!filtered.length" class="searchable-select-empty">No matches</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'

export interface SelectOption {
  value: string | number
  label: string
}

const props = withDefaults(defineProps<{
  modelValue: string | number | null | undefined
  options: SelectOption[]
  id?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
}>(), {
  placeholder: 'Select or type to search',
  required: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | null]
  change: [value: string | number | null]
}>()

const root = ref<HTMLElement | null>(null)
const input = ref<HTMLInputElement | null>(null)
const open = ref(false)
const query = ref('')
const activeIndex = ref(0)

const selectedLabel = computed(() => {
  const hit = props.options.find(o => o.value === props.modelValue)
  return hit ? hit.label : ''
})

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return props.options
  return props.options.filter(o => o.label.toLowerCase().includes(q))
})

watch(filtered, () => { activeIndex.value = 0 })

function openList() {
  if (props.disabled) return
  query.value = ''
  activeIndex.value = Math.max(0, props.options.findIndex(o => o.value === props.modelValue))
  open.value = true
  document.addEventListener('mousedown', onDocumentMouseDown)
}

function close() {
  open.value = false
  query.value = ''
  document.removeEventListener('mousedown', onDocumentMouseDown)
}

function onInput(e: Event) {
  query.value = (e.target as HTMLInputElement).value
  if (!open.value) {
    open.value = true
    document.addEventListener('mousedown', onDocumentMouseDown)
  }
}

function move(step: number) {
  if (!open.value) { openList(); return }
  const n = filtered.value.length
  if (!n) return
  activeIndex.value = (activeIndex.value + step + n) % n
}

function pickActive() {
  if (!open.value) return
  const opt = filtered.value[activeIndex.value]
  if (opt) select(opt.value)
  else close()
}

function select(value: string | number) {
  emit('update:modelValue', value)
  emit('change', value)
  close()
}

function onBlur() {
  if (open.value) close()
  if (input.value) input.value.value = selectedLabel.value
}

function onDocumentMouseDown(e: MouseEvent) {
  if (root.value && !root.value.contains(e.target as Node)) close()
}

onBeforeUnmount(() => document.removeEventListener('mousedown', onDocumentMouseDown))
</script>

<style scoped>
.searchable-select {
  position: relative;
  width: 100%;
}
.searchable-select-list {
  position: absolute;
  z-index: 60;
  left: 0;
  right: 0;
  top: 100%;
  margin-top: 4px;
  max-height: 240px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  list-style: none;
  padding: 4px 0;
}
.searchable-select-list li {
  padding: 6px 10px;
  cursor: pointer;
  font-size: 0.875rem;
}
.searchable-select-list li.is-active {
  background: #eef2ff;
}
.searchable-select-list li.is-selected {
  font-weight: 600;
}
.searchable-select-empty {
  color: #6b7280;
  cursor: default !important;
}
</style>
