import APIService from '@/services/APIService.js'
import router from '@/router.js'

export const namespaced = true

export const state = {
  // The current logged-in user. Format (when not null):
  // {
  //   id: 1
  //   name: 'Justin Liu'
  //   email: 'my@email.com'
  // }
  current: null,
}

export const mutations = {
  SET_USER_DATA(state, userData) {
    state.current = userData
    localStorage.setItem('user', JSON.stringify(userData))
    APIService.setAuth(userData.token)
  },
  CLEAR_USER_DATA(state) {
    localStorage.removeItem('user')
    state.current = null
  },
}

export const actions = {
  login({ commit }, credentials) {
    return APIService.login(credentials).then(({ data }) => {
      commit('SET_USER_DATA', data)
    })
  },
  signup({ commit }, credentials) {
    return APIService.signup(credentials).then(({ data }) => {
      commit('SET_USER_DATA', data)
    })
  },
  logout({ commit, dispatch }) {
    commit('CLEAR_USER_DATA')
    dispatch(
      'message/push',
      {
        type: 'success',
        text: '注销成功。',
      },
      { root: true }
    )
    router.push({ name: 'home' })
  },
}
