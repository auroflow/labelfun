import axios from 'axios'
import store from '@/store'
import router from '@/router'

const apiClient = axios.create({
  baseURL: 'http://localhost:8080/api',
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
  timeout: 5000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      store.dispatch('user/logout')
      error.response.data.message = '登录失效，请重新登录。'
      router.push({ name: 'login' })
    } else return Promise.reject(error)
  }
)

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
}
