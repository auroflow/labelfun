export default {
  namespaced: true,

  state: {
    messages: [],
    popInterval: null,
  },

  getters: {
    count(state) {
      return state.messages.length
    },
  },

  mutations: {
    PUSH(state, message) {
      state.messages.push({
        type: message.type,
        text: message.text,
      })
    },
    POP(state) {
      state.messages.shift()
    },
    SET_POP_INTERVAL(state) {
      if (state.popInterval == null) {
        state.popInterval = setInterval(() => {
          this.dispatch('message/autoPop')
        }, 4000)
      }
    },
    RESET_POP_INTERVAL(state) {
      if (state.popInterval) {
        clearInterval(state.popInterval)
      }
      state.popInterval = setInterval(() => {
        this.dispatch('message/autoPop')
      }, 4000)
    },
    CLEAR_POP_INTERVAL(state) {
      if (state.popInterval) {
        clearInterval(state.popInterval)
        state.popInterval = null
      }
    },
  },

  actions: {
    push({ commit }, message) {
      commit('PUSH', message)
      commit('SET_POP_INTERVAL')
    },
    pop({ state, commit }) {
      commit('POP')
      if (state.messages.length) {
        commit('RESET_POP_INTERVAL')
      } else {
        commit('CLEAR_POP_INTERVAL')
      }
    },
    autoPop({ state, commit }) {
      commit('POP')
      if (!state.messages.length) {
        commit('CLEAR_POP_INTERVAL')
      }
    },
  },
}
