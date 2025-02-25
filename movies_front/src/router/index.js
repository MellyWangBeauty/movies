import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
import Home from '../views/Home.vue'
import Hot from '../views/Hot.vue'
import Rank from '../views/Rank.vue'
import Recommend from '../views/Recommend.vue'
import MovieDetail from '../views/MovieDetail.vue'
import UserCenter from '../views/UserCenter.vue'

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
      component: Hot
    },
    {
      path: '/rank',
      name: 'rank',
      component: Rank
    },
    {
      path: '/recommend',
      name: 'recommend',
      component: Recommend
    },
    {
      path: '/movie/:id',
      name: 'movie-detail',
      component: MovieDetail
    },
    {
      path: '/user-center',
      name: 'user-center',
      component: UserCenter,
      meta: { requiresAuth: true }
    },
    {
      path: '/search',
      name: 'Search',
      component: () => import('../views/Search.vue')
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