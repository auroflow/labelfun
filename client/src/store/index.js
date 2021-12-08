import Vue from 'vue'
import Vuex from 'vuex'

import * as user from '@/store/modules/user.js'
import message from '@/store/modules/message.js'
import task from '@/store/modules/task.js'
Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    user,
    message,
    task,
  },
})

const userString = localStorage.getItem('user')
if (userString) {
  const userData = JSON.parse(userString)
  store.commit('user/SET_USER_DATA', userData)
}

export default store
