import APIService from '@/services/APIService.js'

export const namespaced = true

export const state = {
  // The current logged-in user. Format (when not null):
  // {
  //   id: 1,
  //   name: 'Justin Liu',
  //   email: 'my@email.com',
  //   type: 'user',
  //   token: ...
  // }
  user: null,
}

export const mutations = {
  SET_USER_DATA(state, userData) {
    let old_token = null
    const userString = localStorage.getItem('user')
    if (userString) {
      const userData = JSON.parse(userString)
      old_token = userData['token']
    }

    state.user = {
      id: userData.id,
      name: userData.name,
      email: userData.email,
      type: userData.type,
      token: userData.access_token ? userData.access_token : old_token, // every field is required!
    }
    localStorage.setItem('user', JSON.stringify(state.user))
    APIService.setAuth(state.user.token)
  },
  CLEAR_USER_DATA(state) {
    localStorage.removeItem('user')
    state.user = null
    APIService.clearAuth()
  },
}

export const getters = {
  getCurrentUser(state) {
    return state.user
  },
}

export const actions = {
  login({ commit }, credentials) {
    return APIService.login(credentials).then(({ data }) => {
      commit('SET_USER_DATA', data)
    })
  },
  signup(context, credentials) {
    return APIService.userCreate(credentials)
  },
  updateInfo({ commit }, info) {
    return APIService.userUpdate(info).then(({ data }) => {
      commit('SET_USER_DATA', data)
    })
  },
  logout({ commit }) {
    commit('CLEAR_USER_DATA')
  },
}
