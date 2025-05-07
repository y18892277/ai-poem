import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/utils/axios'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
  }

  const setUserInfo = (info) => {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  const login = async (username, password) => {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await axios.post('/api/v1/token', formData)
      setToken(response.data.access_token)
      
      const userResponse = await axios.get('/api/v1/users/me')
      setUserInfo(userResponse.data)
      
      return true
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const register = async (userData) => {
    try {
      const response = await axios.post('/api/v1/register', userData)
      return response.data
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    }
  }

  const logout = () => {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    delete axios.defaults.headers.common['Authorization']
  }

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put('/api/v1/users/me', profileData)
      setUserInfo(response.data)
      return response.data
    } catch (error) {
      console.error('Profile update failed:', error)
      throw error
    }
  }

  return {
    token,
    userInfo,
    login,
    register,
    logout,
    updateProfile
  }
}) 