import { defineStore } from 'pinia'
import { login as apiLogin } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,  // 有 token = 已登录
  },

  actions: {
    async login(username: string, password: string) {
      const res = await apiLogin(username, password)
      this.token = res.data.access_token
      localStorage.setItem('token', this.token)
    },

    logout() {
      this.token = ''
      localStorage.removeItem('token')
    },
  },
})
