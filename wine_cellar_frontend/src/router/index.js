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
        path: 'tasting',
        name: 'Tasting',
        component: () => import('@/views/Tasting.vue')
      },
      {
        path: 'tasting/:id',
        name: 'TastingDetail',
        component: () => import('@/views/TastingDetail.vue')
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
      },
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('@/views/Sales.vue')
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
  const userInfoStr = localStorage.getItem('userInfo')
  let userInfo = {}
  try {
    userInfo = JSON.parse(userInfoStr || '{}')
  } catch (e) {}

  if (to.meta.requiresAuth && !token) {
    return '/login'
  } else if (to.path === '/login' && token) {
    if (userInfo.role === 'customer') {
      return '/sales'
    }
    return '/dashboard'
  }

  if (token && userInfo.role === 'customer') {
    const allowedPaths = ['/sales', '/login']
    const basePath = '/' + to.path.split('/').filter(Boolean)[0]
    if (!allowedPaths.includes(basePath) && to.path !== '/login') {
      return '/sales'
    }
  }
})

export default router
