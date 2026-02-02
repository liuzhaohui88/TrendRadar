import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'stats-chart' }
      },
      {
        path: 'sources',
        name: 'sources',
        component: () => import('../views/Sources.vue'),
        meta: { title: '数据源', icon: 'globe' }
      },
      {
        path: 'keywords',
        name: 'keywords',
        component: () => import('../views/Keywords.vue'),
        meta: { title: '关键词策略', icon: 'key' }
      },
      {
        path: 'channels',
        name: 'channels',
        component: () => import('../views/Channels.vue'),
        meta: { title: '推送渠道', icon: 'send' }
      },
      {
        path: 'rules',
        name: 'rules',
        component: () => import('../views/Rules.vue'),
        meta: { title: '分发规则', icon: 'git-branch' }
      },
      {
        path: 'news',
        name: 'news',
        component: () => import('../views/News.vue'),
        meta: { title: '新闻数据', icon: 'newspaper' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 未登录跳转登录页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'login' && !token) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
