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
    RESIZE_BOX(state, payload) {
      state.entity.annotation[payload.index].bbox = payload.bbox
    },
    DELETE_BOX(state, boxToDelete) {
      state.entity.annotation = state.entity.annotation.filter(
        (box) => box !== boxToDelete
      )
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
    resizeBox({ commit }, payload) {
      commit('RESIZE_BOX', payload)
    },
    deleteBox({ commit }, box) {
      commit('DELETE_BOX', box)
    },
  },
}
