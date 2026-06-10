import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, registerCustomer, getCurrentUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value.role === 'admin')
  const isCustomer = computed(() => userInfo.value.role === 'customer')

  async function fetchUserInfo() {
    try {
      const res = await getCurrentUserInfo()
      userInfo.value = res
      localStorage.setItem('userInfo', JSON.stringify(res))
      return res
    } catch (e) {
      console.error('获取用户信息失败', e)
      throw e
    }
  }

  async function login(username, password) {
    const response = await apiLogin(username, password)
    token.value = response.access
    refreshToken.value = response.refresh
    localStorage.setItem('token', response.access)
    localStorage.setItem('refreshToken', response.refresh)
    await fetchUserInfo()
    return response
  }

  async function register(data) {
    const response = await registerCustomer(data)
    token.value = response.access
    refreshToken.value = response.refresh
    localStorage.setItem('token', response.access)
    localStorage.setItem('refreshToken', response.refresh)
    userInfo.value = response.user
    localStorage.setItem('userInfo', JSON.stringify(response.user))
    return response
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    isAdmin,
    isCustomer,
    login,
    register,
    logout,
    fetchUserInfo
  }
})
