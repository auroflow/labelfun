import APIService from '@/services/APIService'

export default {
  namespaced: true,

  state: {
    tasks: [],
    task: {},
    pagination: {},
  },

  getters: {
    getUnlabeledTasks(state) {
      return state.tasks.filter((task) => task.type === 'unlabeled')
    },
    getUnreviewedTasks(state) {
      return state.tasks.filter((task) => task.type === 'unreviewed')
    },
    getDoneTasks(state) {
      return state.tasks.filter((task) => task.type === 'done')
    },
  },

  mutations: {
    SET_TASKS(state, data) {
      state.tasks = data
    },
    SET_TASK(state, data) {
      state.task = data
    },
    SET_PAGINATION(state, data) {
      state.pagination = data
    },
  },

  actions: {
    createTask() {},
    modifyTask() {},
    fetchTasks({ commit }) {
      return APIService.tasksFetch().then(({ data }) => {
        commit('SET_TASKS', data.tasks)
        commit('SET_PAGINATION', data.pagination)
      })
    },
    fetchTask({ commit }, id) {
      return APIService.taskFetch(id).then(({ data }) => {
        commit('SET_TASK', data)
      })
    },
  },
}
