import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'monitoring',
        name: 'Monitoring',
        component: () => import('@/views/Monitoring.vue')
      },
      {
        path: 'collection',
        name: 'Collection',
        component: () => import('@/views/Collection.vue')
      },
      {
        path: 'collection/new',
        name: 'WineCreate',
        component: () => import('@/views/WineCreate.vue')
      },
      {
        path: 'collection/:id',
        name: 'WineDetail',
        component: () => import('@/views/WineDetail.vue')
      },
      {
        path: 'mortgage',
        name: 'Mortgage',
        component: () => import('@/views/Mortgage.vue')
      },
      {
        path: 'mortgage/:id',
        name: 'MortgageDetail',
        component: () => import('@/views/MortgageDetail.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    return '/login'
  } else if (to.path === '/login' && token) {
    return '/dashboard'
  }
})

export default router
