import APIService from '@/services/APIService'

export default {
  namespaced: true,

  state: {
    entity: null,
  },

  mutations: {
    SET(state, data) {
      state.entity = data
    },
  },

  actions: {
    fetchEntity({ state, commit, dispatch }, id) {
      if (state.entity?.id !== id) {
        return APIService.entityFetch(id)
          .then(({ data }) => {
            commit('SET', data)
          })
          .catch((error) =>
            dispatch('message/pushError', error, { root: true })
          )
      }
    },
  },
}
