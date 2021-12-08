import APIService from '@/services/APIService'
import NProgress from 'nprogress'

export default {
  namespaced: true,

  state: {
    tasksOutdated: true,
    tasks: [],
    task: {},
    pagination: {},
  },

  getters: {
    getUnlabeledTasks: (state) => {
      return state.tasks.filter((task) => task.progress === 'unlabeled')
    },
    getUnreviewedTasks: (state) => {
      return state.tasks.filter((task) => task.progress === 'unreviewed')
    },
    getDoneTasks: (state) => {
      return state.tasks.filter((task) => task.progress === 'done')
    },
    getTasksByCreator: (state) => (id) => {
      return state.tasks.filter((task) => task.creator.id === id)
    },
    getTasksByLabeler: (state) => (id) => {
      return state.tasks.filter(
        (task) => task.labeler && task.labeler.id === id
      )
    },
    getTasksByReviewer: (state) => (id) => {
      return state.tasks.filter(
        (task) => task.reviewer && task.reviewer.id === id
      )
    },
  },

  mutations: {
    SET_TASKS(state, data) {
      state.tasks = data
      state.tasksOutdated = false
    },
    SET_TASK(state, data) {
      state.task = data
    },
    SET_PAGINATION(state, data) {
      state.pagination = data
    },
    EXPIRE_TASKS(state) {
      state.tasksOutdated = true
    },
  },

  actions: {
    createTask({ commit, dispatch }, data) {
      return APIService.taskCreate(data)
        .then(({ data }) => {
          commit('SET_TASK', data)
          commit('EXPIRE_TASKS')
        })
        .catch((error) => dispatch('message/pushError', error, { root: true }))
    },
    updateTask({ commit, dispatch }, data) {
      return APIService.taskUpdate(data.id, data.task)
        .then(({ data }) => {
          commit('SET_TASK', data)
          commit('EXPIRE_TASKS')
        })
        .catch((error) => dispatch('message/pushError', error, { root: true }))
    },
    fetchTasks({ state, commit, dispatch }) {
      if (state.tasksOutdated) {
        return APIService.tasksFetch()
          .then(({ data }) => {
            commit('SET_TASKS', data.tasks)
            commit('SET_PAGINATION', data.pagination)
          })
          .catch((error) =>
            dispatch('message/pushError', error, { root: true })
          )
      }
    },
    fetchTask({ state, commit, dispatch }, id) {
      if (state.task?.id !== id) {
        return APIService.taskFetch(id)
          .then(({ data }) => {
            commit('SET_TASK', data)
          })
          .catch((error) =>
            dispatch('message/pushError', error, { root: true })
          )
      }
    },
    claim({ commit, dispatch }, data) {
      NProgress.start()
      return APIService.taskClaim(data.id, data.action)
        .then(({ data }) => {
          commit('SET_TASK', data)
          commit('EXPIRE_TASKS')
          NProgress.done()
        })
        .catch((error) => dispatch('message/pushError', error, { root: true }))
    },
    complete({ commit, dispatch }, data) {
      NProgress.start()
      return APIService.taskComplete(data.id, data.action)
        .then(({ data }) => {
          commit('SET_TASK', data)
          commit('EXPIRE_TASKS')
          NProgress.done()
        })
        .catch((error) => dispatch('message/pushError', error, { root: true }))
    },
  },
}
