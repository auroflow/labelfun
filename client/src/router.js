import Vue from 'vue'
import Router from 'vue-router'
import TaskCenter from './views/TaskCenter.vue'
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
      component: TaskCenter,
      meta: {
        requiresAuth: true,
        displayName: '任务中心',
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
    {
      path: '/task/new',
      name: 'create',
      component: () => import('./views/TaskCreate.vue'),
      meta: {
        requiresAuth: true,
        displayName: '新建任务',
      },
    },
    {
      path: '/task/:id',
      name: 'task',
      component: () => import('./views/TaskView.vue'),
      props: (route) => ({
        id: Number(route.params.id),
      }),
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
