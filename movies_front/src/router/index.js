import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
import Home from '../views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/hot',
      name: 'hot',
      component: () => import('../views/Hot.vue')
    },
    {
      path: '/rank',
      name: 'rank',
      component: () => import('../views/Rank.vue')
    },
    {
      path: '/recommend',
      name: 'recommend',
      component: () => import('../views/Recommend.vue')
    },
    {
      path: '/movie/:id',
      name: 'movie-detail',
      component: () => import('../views/MovieDetail.vue'),
      props: true
    },
    {
      path: '/user-center',
      name: 'user-center',
      component: () => import('../views/UserCenter.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn()) {
    next('/')
  } else {
    next()
  }
})

export default router 