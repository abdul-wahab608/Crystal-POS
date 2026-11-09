import { computed, ref } from 'vue'
import { describe, it, expect } from 'vitest'
import { usePagination } from '../usePagination'

function makeItems(count: number) {
  return Array.from({ length: count }, (_, i) => i + 1)
}

describe('usePagination', () => {
  it('defaults to page 1 with 25 rows per page', () => {
    const list = ref(makeItems(60))
    const p = usePagination(computed(() => list.value))

    expect(p.page.value).toBe(1)
    expect(p.pageSize.value).toBe(25)
    expect(p.total.value).toBe(60)
    expect(p.totalPages.value).toBe(3)
    expect(p.pageItems.value).toHaveLength(25)
    expect(p.pageItems.value[0]).toBe(1)
  })

  it('slices the list for the requested page', () => {
    const list = ref(makeItems(60))
    const p = usePagination(computed(() => list.value))

    p.goTo(3)
    expect(p.pageItems.value).toEqual(makeItems(10).map(n => n + 50))
  })

  it('clamps goTo to the valid range', () => {
    const list = ref(makeItems(30))
    const p = usePagination(computed(() => list.value))

    p.goTo(99)
    expect(p.page.value).toBe(2)
    p.goTo(0)
    expect(p.page.value).toBe(1)
  })

  it('reports one empty page when the list is empty', () => {
    const list = ref<number[]>([])
    const p = usePagination(computed(() => list.value))

    expect(p.totalPages.value).toBe(1)
    expect(p.pageItems.value).toEqual([])
  })

  it('clamps the page when the list shrinks', () => {
    const list = ref(makeItems(60))
    const p = usePagination(computed(() => list.value))

    p.goTo(3)
    list.value = makeItems(30)
    expect(p.totalPages.value).toBe(2)
    expect(p.page.value).toBe(2)
    expect(p.pageItems.value).toHaveLength(5)

    list.value = []
    expect(p.page.value).toBe(1)
    expect(p.pageItems.value).toEqual([])
  })

  it('setPageSize changes the page size and returns to page 1', () => {
    const list = ref(makeItems(60))
    const p = usePagination(computed(() => list.value))

    p.goTo(2)
    p.setPageSize(10)
    expect(p.pageSize.value).toBe(10)
    expect(p.page.value).toBe(1)
    expect(p.totalPages.value).toBe(6)
    expect(p.pageItems.value).toHaveLength(10)

    p.setPageSize(50)
    expect(p.totalPages.value).toBe(2)
    expect(p.pageItems.value).toHaveLength(50)
  })

  it('reset returns to page 1 without changing the page size', () => {
    const list = ref(makeItems(100))
    const p = usePagination(computed(() => list.value), 10)

    p.goTo(4)
    p.reset()
    expect(p.page.value).toBe(1)
    expect(p.pageSize.value).toBe(10)
  })

  it('follows filtered source changes', () => {
    const list = ref(makeItems(60))
    const filtered = computed(() => list.value.filter(n => n % 2 === 0))
    const p = usePagination(filtered)

    expect(p.total.value).toBe(30)
    expect(p.totalPages.value).toBe(2)
    p.goTo(2)
    expect(p.pageItems.value[0]).toBe(52)
  })
})
