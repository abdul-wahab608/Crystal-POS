import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../shared/layouts/MainLayout.vue'

// Placeholder views for each module
const CustomersView = () => import('../modules/customers/views/CustomersView.vue')
const VendorsView = () => import('../modules/vendors/views/VendorsView.vue')
const ProductsView = () => import('../modules/products/views/ProductsView.vue')
const SalesView = () => import('../modules/sales/views/SalesView.vue')
const PurchasesView = () => import('../modules/purchases/views/PurchasesView.vue')
const AssetsView = () => import('../modules/assets/views/AssetsView.vue')
const PaymentsView = () => import('../modules/payments/views/PaymentsView.vue')
const ReportsView = () => import('../modules/reports/views/ReportsView.vue')
const UsersView = () => import('../modules/users/views/UsersView.vue')
const RawMaterialsView = () => import('../modules/raw_materials/views/RawMaterialsView.vue')
const DashboardView = () => import('../views/HomeView.vue')
const LoginView = () => import('../views/LoginView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'dashboard', component: DashboardView },
        { path: 'customers', name: 'customers', component: CustomersView },
        { path: 'vendors', name: 'vendors', component: VendorsView },
        { path: 'products', name: 'products', component: ProductsView },
        { path: 'sales', name: 'sales', component: SalesView },
        { path: 'purchases', name: 'purchases', component: PurchasesView },
        { path: 'assets', name: 'assets', component: AssetsView },
        { path: 'payments', name: 'payments', component: PaymentsView },
        { path: 'reports', name: 'reports', component: ReportsView },
        { path: 'users', name: 'users', component: UsersView },
        { path: 'raw-materials', name: 'raw-materials', component: RawMaterialsView },
      ],
    },
  ],
})

// Navigation guard to check authentication
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  
  if (to.path === '/login') {
    if (token) {
      // Already logged in, redirect to dashboard
      next('/')
    } else {
      // Not logged in, allow access to login page
      next()
    }
  } else {
    if (token) {
      // Has token, allow access to protected routes
      next()
    } else {
      // No token, redirect to login
      next('/login')
    }
  }
})

export default router
