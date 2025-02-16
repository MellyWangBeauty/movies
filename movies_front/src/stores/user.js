import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  // 设置token
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    // 设置axios默认header
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
  }

  // 清除token
  const clearToken = () => {
    token.value = ''
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  // 注册
  const register = async (userData) => {
    try {
      const response = await axios.post('/api/users/register', userData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || '注册失败')
    }
  }

  // 登录
  const login = async (credentials) => {
    try {
      const formData = new FormData()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)
      
      const response = await axios.post('/api/users/token', formData)
      setToken(response.data.access_token)
      await fetchUserInfo()
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || '登录失败')
    }
  }

  // 登出
  const logout = async () => {
    try {
      await axios.post('/api/users/logout')
      clearToken()
      userInfo.value = null
    } catch (error) {
      // 即使后端请求失败，也要清除本地状态
      clearToken()
      userInfo.value = null
      throw new Error(error.response?.data?.detail || '退出登录失败')
    }
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const response = await axios.get('/api/users/me')
      userInfo.value = response.data
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || '获取用户信息失败')
    }
  }

  // 更新用户信息
  const updateUserInfo = async (updateData) => {
    try {
      const response = await axios.put('/api/users/me', updateData)
      userInfo.value = response.data
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || '更新用户信息失败')
    }
  }

  // 检查是否已登录
  const isLoggedIn = () => {
    return !!token.value
  }

  return {
    token,
    userInfo,
    register,
    login,
    logout,
    fetchUserInfo,
    updateUserInfo,
    isLoggedIn
  }
}) 