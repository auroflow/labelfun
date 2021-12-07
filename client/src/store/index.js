import Vue from 'vue'
import Vuex from 'vuex'

import * as user from '@/store/modules/user.js'
import message from '@/store/modules/message.js'
import task from '@/store/modules/task.js'
Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    user,
    message,
    task,
  },
})
