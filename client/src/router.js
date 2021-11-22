import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import NProgress from 'nprogress'
import store from '@/store'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: {
        displayName: '首页',
      },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('./views/Login.vue'),
      meta: {
        requiresNoAuth: true,
        displayName: '登录',
      },
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('./views/Signup.vue'),
      meta: {
        requiresNoAuth: true,
        displayName: '注册',
      },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('./views/Profile.vue'),
      meta: {
        requiresAuth: true,
      },
    },
  ],
})

router.beforeEach((to, from, next) => {
  NProgress.start()
  const loggedIn = localStorage.getItem('user')
  // protected route
  if (to.matched.some((record) => record.meta.requiresAuth) && !loggedIn) {
    store.dispatch('message/push', {
      type: 'error',
      text: '请登录。',
    })
    next('/login')
  }
  // routes hidden for logged-in users, e.g. login and register pages
  else if (
    to.matched.some((record) => record.meta.requiresNoAuth) &&
    loggedIn
  ) {
    next('/')
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
