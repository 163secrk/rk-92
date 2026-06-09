import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const response = await apiLogin(username, password)
    token.value = response.access
    localStorage.setItem('token', response.access)
    localStorage.setItem('refreshToken', response.refresh)
    localStorage.setItem('userInfo', JSON.stringify({ username }))
    userInfo.value = { username }
    return response
  }

  function logout() {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    logout
  }
})
