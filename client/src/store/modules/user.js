import APIService from '@/services/APIService.js'

export const namespaced = true

export const state = {
  current: null,
}

export const mutations = {
  SET_USER_DATA(state, userData) {
    state.current = userData
    localStorage.setItem('user', JSON.stringify(userData))
    APIService.setAuth(userData.token)
  },
  CLEAR_USER_DATA() {
    localStorage.removeItem('user')
    location.reload()
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
  logout({ commit }) {
    commit('CLEAR_USER_DATA')
  },
}
