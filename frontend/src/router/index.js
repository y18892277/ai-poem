import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/battle',
      name: 'Battle',
      component: () => import('@/views/Battle.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/rankings',
      name: 'rankings',
      component: () => import('@/views/Rankings.vue')
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/Profile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/poetry',
      name: 'poetry',
      component: () => import('@/views/PoetryLibrary.vue')
    }
  ]
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const token = localStorage.getItem('token')
  
  // 如果需要登录且没有token
  if (to.meta.requiresAuth && !token) {
    next('/login')
  }
  // 如果已登录且访问登录/注册页
  else if (token && (to.path === '/login' || to.path === '/register')) {
    next('/')
  }
  else {
    next()
  }
})

export default router