import { computed, ref, watch } from 'vue'

export const PAGE_SIZE_OPTIONS = [10, 25, 50]

interface ListSource<T> {
  readonly value: readonly T[]
}

export function usePagination<T>(source: ListSource<T>, initialPageSize = 25) {
  const page = ref(1)
  const pageSize = ref(initialPageSize)

  const total = computed(() => source.value.length)
  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

  watch(totalPages, (last) => {
    if (page.value > last) page.value = last
  }, { flush: 'sync' })

  const pageItems = computed<T[]>(() => {
    const start = (page.value - 1) * pageSize.value
    return source.value.slice(start, start + pageSize.value) as T[]
  })

  function goTo(n: number) {
    page.value = Math.min(Math.max(1, Math.floor(n)), totalPages.value)
  }

  function setPageSize(n: number) {
    pageSize.value = n
    page.value = 1
  }

  function reset() {
    page.value = 1
  }

  return { page, pageSize, totalPages, pageItems, total, goTo, setPageSize, reset }
}
