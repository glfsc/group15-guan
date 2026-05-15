import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/practice'
  },
  {
    path: '/practice',
    name: 'Practice',
    component: () => import('@/views/Practice.vue'),
    meta: { title: '练习' }
  },
  {
    path: '/listening',
    name: 'Listening',
    component: () => import('@/views/Listening.vue'),
    meta: { title: '听力练习' }
  },
  {
    path: '/grammar',
    name: 'Grammar',
    component: () => import('@/views/Grammar.vue'),
    meta: { title: '语法练习' }
  },
  {
    path: '/progress',
    name: 'Progress',
    component: () => import('@/views/Progress.vue'),
    meta: { title: '学习进度' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '设置' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = (to.meta.title as string) || '托业学习应用'
  next()
})

export default router
