import APIService from '@/services/APIService'
import NProgress from 'nprogress'
import * as qiniu from 'qiniu-js'

export default {
  namespaced: true,

  state: {
    tasksOutdated: true,
    tasks: [],
    task: {},
    pagination: {},
    uploading: false, // uploading to qiniu
    showDialog: false, // the dialog box to upload files
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
    UPLOAD_SET(state) {
      state.uploading = true
    },
    UPLOAD_CLEAR(state) {
      state.uploading = false
    },
    SHOW_ADD_ENTITIES(state) {
      state.showDialog = true
    },
    HIDE_ADD_ENTITIES(state) {
      state.showDialog = false
    },
  },

  actions: {
    expireTasks({ commit }) {
      commit('EXPIRE_TASKS')
    },
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
      } else {
        return Promise.resolve()
      }
    },
    fetchTask({ state, commit, dispatch }, id) {
      if (state.task?.id !== id || state.tasksOutdated) {
        return APIService.taskFetch(id)
          .then(({ data }) => {
            commit('SET_TASK', data)
          })
          .catch((error) =>
            dispatch('message/pushError', error, { root: true })
          )
      } else {
        return Promise.resolve()
      }
    },
    publish({ commit, dispatch }, id) {
      NProgress.start()
      return APIService.taskPublish(id)
        .then(({ data }) => {
          commit('SET_TASK', data)
          NProgress.done()
        })
        .catch((error) => dispatch('message/pushError', error, { root: true }))
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
    addEntities({ commit, dispatch }, { request_data, files }) {
      commit('UPLOAD_SET')
      return APIService.entitiesCreate(request_data)
        .then(({ data }) => {
          commit('SET_TASK', data['task'])
          const creds = data['credentials']
          for (const cred of creds) {
            const file = files.find((file) => file.name === cred['path'])
            const observable = qiniu.upload(file, cred['key'], cred['token'])
            observable.subscribe({
              error: (res) => {
                console.log(cred['path'], 'failed to uploaded as', cred['key'])
                APIService.entityDelete(cred['key'])
                dispatch(
                  'message/pushError',
                  {
                    message: `上传 ${cred['path']} 失败：${res.message}`,
                  },
                  { root: true }
                )
              },
              complete: (res) => {
                APIService.entitiesPatch(res.key, res.duration)
              },
            })
          }
          commit('UPLOAD_CLEAR')
          commit('HIDE_ADD_ENTITIES')
        })
        .catch((error) => dispatch('message/pushError', error, { root: true }))
    },
  },
}
