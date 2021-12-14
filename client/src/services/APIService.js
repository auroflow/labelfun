import axios from 'axios'
import store from '@/store'
import router from '@/router'

const apiClient = axios.create({
  baseURL: 'http://localhost:8080/api',
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      store.dispatch('user/logout')
      store.commit('message/POP_ALL')
      store.dispatch('message/push', {
        type: 'error',
        text: '登录超时，请重新登录。',
      })
      router.push({ name: 'login' })
    } else return Promise.reject(error)
  }
)

// eslint-disable-next-line no-unused-vars
const uploadClient = axios.create({
  baseURL: 'http://localhost:8080/upload',
})

export default {
  setAuth(token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },
  clearAuth() {
    delete apiClient.defaults.headers.common['Authorization']
  },
  login(user) {
    return apiClient.post('/auth/login', {
      grant_type: 'password',
      ...user,
    })
  },
  userCreate(newUser) {
    return apiClient.post('/users', newUser)
  },
  userUpdate(info) {
    return apiClient.patch('/users/' + info.id, info.data)
  },
  tasksFetch() {
    return apiClient.get('/tasks')
  },
  taskFetch(id) {
    return apiClient.get('/tasks/' + id)
  },
  taskClaim(id, action) {
    return apiClient.post(`/tasks/${id}`, { type: action })
  },
  taskComplete(id, action) {
    return apiClient.patch(`/tasks/${id}`, { type: action })
  },
  taskCreate(data) {
    return apiClient.post('/tasks', data)
  },
  taskUpdate(id, data) {
    return apiClient.put(`/tasks/${id}`, data)
  },
  taskPublish(id) {
    return apiClient.put(`/tasks/${id}`, { published: true })
  },
  taskDelete(id) {
    return apiClient.delete('/tasks/' + id)
  },
  entitiesCreate(data) {
    return apiClient.post('/entities', data)
  },
  entitiesPatch(key, duration) {
    return apiClient.patch('/entities', { key: key, duration: duration })
  },
  entityFetch(id) {
    return apiClient.get(`/entities/${id}`)
  },
  entityLabel(id, data) {
    return apiClient.post(`/entities/${id}`, data)
  },
  entityDelete(id) {
    return apiClient.delete(`/entities/${id}`)
  },
}
