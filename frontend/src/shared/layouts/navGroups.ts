export interface NavItem {
  name: string
  href: string
  superuserOnly?: boolean
  managerOnly?: boolean
}

export interface NavSection {
  name: string
  items: NavItem[]
}

export const NAV_DASHBOARD: NavItem = { name: 'Dashboard', href: '/' }

export const NAV_SECTIONS: NavSection[] = [
  {
    name: 'Catalog',
    items: [
      { name: 'Catalog', href: '/catalog' },
      { name: 'Products', href: '/products' },
    ],
  },
  {
    name: 'Inventory',
    items: [
      { name: 'Raw Materials', href: '/raw-materials' },
      { name: 'Production', href: '/production' },
    ],
  },
  {
    name: 'Buying',
    items: [
      { name: 'Vendors', href: '/vendors' },
      { name: 'Purchases', href: '/purchases' },
    ],
  },
  {
    name: 'Selling',
    items: [
      { name: 'Customers', href: '/customers' },
      { name: 'Sales', href: '/sales' },
      { name: 'Payments', href: '/payments' },
    ],
  },
  {
    name: 'Finance',
    items: [
      { name: 'Profit', href: '/profit', managerOnly: true },
      { name: 'Reports', href: '/reports' },
      { name: 'Bank Accounts', href: '/bank-accounts' },
      { name: 'Assets', href: '/assets' },
    ],
  },
  {
    name: 'Admin',
    items: [
      { name: 'Users', href: '/users' },
      { name: 'Import History', href: '/import-history', superuserOnly: true },
    ],
  },
]

export function visibleSections(
  sections: NavSection[],
  user: { is_superuser?: boolean; role?: string } | null,
): NavSection[] {
  const isManager = ['ADMIN', 'MANAGER'].includes(user?.role ?? '')
  return sections
    .map((section) => ({
      name: section.name,
      items: section.items.filter(
        (item) =>
          (!item.superuserOnly || user?.is_superuser === true) &&
          (!item.managerOnly || isManager),
      ),
    }))
    .filter((section) => section.items.length > 0)
}

export function sectionForPath(sections: NavSection[], path: string): string | null {
  const hit = sections.find((section) =>
    section.items.some((item) => path === item.href || path.startsWith(`${item.href}/`)),
  )
  return hit ? hit.name : null
}
