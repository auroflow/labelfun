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

    // for image classification
    ADD_LABEL(state, label) {
      state.entity.annotation.push(label)
    },
    DELETE_LABEL(state, label) {
      state.entity.annotation = state.entity.annotation.filter(
        (elem) => elem !== label
      )
    },
    // for image object detection
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

    // for video object detection
    ADD_OBJECT(state, object) {
      state.entity.annotation.push(object)
    },
    ADD_BOX_TO_OBJECT(state, payload) {
      payload.object.trajectory.push(payload.snapshot)
    },
    RESIZE_BOX_IN_OBJECT(state, payload) {
      state.entity.annotation[payload.index].trajectory.find(
        (snapshot) => snapshot.frame_number === payload.frame_number
      ).bbox = payload.bbox
    },
    DELETE_BOX_IN_FRAME(state, payload) {
      payload.object.trajectory = payload.object.trajectory.filter(
        (snapshot) => snapshot.frame_number !== payload.frame_number
      )
    },
    DELETE_OBJECT(state, objectToDelete) {
      state.entity.annotation = state.entity.annotation.filter(
        (object) => object !== objectToDelete
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

    // for image classification
    addLabel({ commit }, label) {
      commit('ADD_LABEL', label)
    },
    deleteLabel({ commit }, label) {
      commit('DELETE_LABEL', label)
    },
    // for image object detection
    addBox({ commit }, box) {
      commit('ADD_BOX', box)
    },
    resizeBox({ commit }, payload) {
      commit('RESIZE_BOX', payload)
    },
    deleteBox({ commit }, box) {
      commit('DELETE_BOX', box)
    },

    // for video object detection
    addObject({ commit }, label) {
      const object = {
        label: label,
        trajectory: [],
      }
      commit('ADD_OBJECT', object)
    },

    addBoxToObject({ commit }, payload) {
      commit('ADD_BOX_TO_OBJECT', payload)
    },

    resizeBoxInObject({ commit }, payload) {
      commit('RESIZE_BOX_IN_OBJECT', payload)
    },

    deleteBoxInFrame({ commit }, payload) {
      commit('DELETE_BOX_IN_FRAME', payload)
    },

    deleteObject({ commit }, objectToDelete) {
      commit('DELETE_OBJECT', objectToDelete)
    },

    // for review
    reviewEntity({ commit, dispatch }, payload) {
      return APIService.entityReview(payload.id, payload.data)
        .then(({ data }) => {
          commit('task/EXPIRE_TASKS', null, { root: true })
          commit('SET', data)
        })
        .catch((error) => dispatch('message/pushError', error, { root: true }))
    },
  },
}
