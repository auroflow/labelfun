import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8080',
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
  timeout: 5000,
})

export default {
  setAuth(token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },
  clearAuth() {
    delete apiClient.defaults.headers.common['Authorization']
  },
  login(user) {
    return apiClient.post('/api/auth/login', {
      grant_type: 'password',
      ...user,
    })
  },
  userCreate(newUser) {
    return apiClient.post('/api/users', newUser)
  },
  userUpdate(info) {
    return apiClient.patch('/api/users/' + info.id, info.data)
  },
  tasksFetch() {
    return apiClient.get('/api/tasks', {
      params: {
        order: 'desc',
      },
    })
  },
  taskFetch(id) {
    return apiClient.get('/api/tasks/' + id)
  },
}
