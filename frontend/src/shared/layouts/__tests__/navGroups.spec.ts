import { describe, it, expect } from 'vitest'
import { NAV_SECTIONS, sectionForPath, visibleSections } from '../navGroups'

describe('visibleSections', () => {
  it('hides superuser-only items from non-superusers and drops empty sections', () => {
    const sections = visibleSections(NAV_SECTIONS, { is_superuser: false })
    const admin = sections.find((s) => s.name === 'Admin')
    expect(admin?.items.map((i) => i.href)).toEqual(['/users'])
  })

  it('shows import history to superusers', () => {
    const sections = visibleSections(NAV_SECTIONS, { is_superuser: true })
    const admin = sections.find((s) => s.name === 'Admin')
    expect(admin?.items.map((i) => i.href)).toEqual(['/users', '/import-history'])
  })

  it('keeps every route from the owner layout spec', () => {
    const hrefs = visibleSections(NAV_SECTIONS, { is_superuser: true, role: 'ADMIN' }).flatMap((s) => s.items.map((i) => i.href))
    expect(hrefs.sort()).toEqual([
      '/assets', '/bank-accounts', '/catalog', '/customers', '/import-history', '/payments',
      '/production', '/products', '/profit', '/purchases', '/raw-materials', '/reports', '/sales',
      '/users', '/vendors',
    ])
  })
})

describe('manager-only items', () => {
  it('hides profit from staff and shows it to managers', () => {
    const staff = visibleSections(NAV_SECTIONS, { is_superuser: false, role: 'STAFF' }).flatMap((s) => s.items.map((i) => i.href))
    const manager = visibleSections(NAV_SECTIONS, { is_superuser: false, role: 'MANAGER' }).flatMap((s) => s.items.map((i) => i.href))
    expect(staff).not.toContain('/profit')
    expect(manager).toContain('/profit')
  })
})

describe('sectionForPath', () => {
  it('finds the section for an exact route', () => {
    expect(sectionForPath(NAV_SECTIONS, '/payments')).toBe('Selling')
  })

  it('finds the section for a nested route', () => {
    expect(sectionForPath(NAV_SECTIONS, '/bank-accounts/12')).toBe('Finance')
  })

  it('returns null for routes outside any section', () => {
    expect(sectionForPath(NAV_SECTIONS, '/')).toBeNull()
    expect(sectionForPath(NAV_SECTIONS, '/units')).toBeNull()
  })
})
