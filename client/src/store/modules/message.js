import NProgress from 'nprogress'

const errors = {
  INCORRECT_EMAIL_OR_PASSWORD: '用户名或密码错误。',
  'Validation error': '表单验证错误',
  DUPLICATED_EMAIL: '该邮箱已注册。',
  OLD_PASSWORD_REQUIRED: '需要填写原密码。',
  INCORRECT_PASSWORD: '密码错误。',
  UNAUTHORIZED: '无权限。',
  'Not Found': '找不到资源。',
  NO_SUCH_TASK: '没有这个任务。',
  TASK_UNDERTAKEN: '任务已领取。',
  NO_ENTITIES: '任务为空，请先添加图片或视频。',
  TASK_PUBLISHED: '任务已发布。',
  TASK_UNPUBLISHED: '任务未发布。',
  TASK_NOT_LABELED: '任务未标注完成。',
  TASK_STATUS_IS_NOT_UNLABELED: '任务未在标注中。',
  TASK_STATUS_IS_NOT_UNREVIEWED: '任务未在审核中。',
  JOB_IS_NOT_DONE: '未完成任务。',
  ENTITY_IS_NOT_UNLABELED_NOR_UNREVIEWED: '标注已完成，不能重复标注。',
  ENTITY_IS_NOT_UNREVIEWED: '审核已完成，或还没有完成标注。',
}

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
    POP_ALL(state) {
      state.messages = []
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
      return Promise.resolve(message)
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
    pushError({ dispatch }, error) {
      if (error.response?.data?.message) {
        let message = null
        if (error.response.data.message in errors) {
          message = errors[error.response.data.message]
        } else {
          message = error.response.data.message
        }
        dispatch('push', {
          type: 'error',
          text: '错误 ' + error.response.status + '：' + message,
        })
      } else if (error.message) {
        dispatch('push', {
          type: 'error',
          text: '错误：' + error.message,
        })
      } else {
        dispatch('push', {
          type: 'error',
          text: '出现了未知错误。',
        })
      }
      NProgress.done()
      return Promise.reject(error)
    },
    pushSuccess({ dispatch }, message) {
      return dispatch('push', {
        type: 'success',
        text: message,
      })
    },
  },
}
