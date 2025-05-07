import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({
  baseURL: '/',
  timeout: 5000
})

service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Response error:', error)
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('请先登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请稍后重试')
    }
    
    return Promise.reject(error)
  }
)

export default service 