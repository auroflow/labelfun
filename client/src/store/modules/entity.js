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
    ADD_BOX(state, box) {
      state.entity.annotation.push(box)
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
      } else {
        return Promise.resolve()
      }
    },
    labelEntity({ commit, dispatch }, payload) {
      return APIService.entityLabel(payload.id, payload.data)
        .then(({ data }) => {
          commit('task/EXPIRE_TASKS', null, { root: true })
          commit('SET', data)
        })
        .catch((error) => dispatch('message/pushError', error, { root: true }))
    },
    addBox({ commit }, box) {
      commit('ADD_BOX', box)
    },
  },
}
