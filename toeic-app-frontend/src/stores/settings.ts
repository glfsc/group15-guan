import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, PageSettings } from '@/types/user'
import { userApi } from '@/api/user'

export const useSettingsStore = defineStore('settings', () => {
  const currentUser = ref<User | null>(null)
  const pageSettings = ref<PageSettings | null>(null)
  const loading = ref(false)

  async function loadUser(userId: string) {
    loading.value = true
    try {
      const user = await userApi.getUser(userId)
      currentUser.value = user
    } catch (error) {
      console.error('Failed to load user:', error)
    } finally {
      loading.value = false
    }
  }

  async function loadPageSettings(userId: string) {
    loading.value = true
    try {
      const settings = await userApi.getPageSettings(userId)
      pageSettings.value = settings
      applySettings(settings)
    } catch (error) {
      console.error('Failed to load page settings:', error)
    } finally {
      loading.value = false
    }
  }

  async function updatePageSettings(userId: string, data: { font_size: string; background_color: string }) {
    loading.value = true
    try {
      const settings = await userApi.updatePageSettings(userId, data)
      pageSettings.value = settings
      applySettings(settings)
      return settings
    } catch (error) {
      console.error('Failed to update page settings:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function applySettings(settings: PageSettings) {
    const root = document.documentElement
    const body = document.body

    const percent = parseInt(settings.font_size, 10)
    const safePercent = isNaN(percent) ? 100 : Math.max(50, Math.min(200, percent))
    root.style.fontSize = `${safePercent}%`

    root.classList.remove('theme-light', 'theme-dark', 'theme-eye-care')
    if (settings.background_color === 'dark') {
      root.classList.add('theme-dark')
      body.style.backgroundColor = '#2d2d2d'
      body.style.color = '#e0e0e0'
    } else if (settings.background_color === 'eye_care') {
      root.classList.add('theme-eye-care')
      body.style.backgroundColor = '#c7edcc'
      body.style.color = '#333333'
    } else {
      root.classList.add('theme-light')
      body.style.backgroundColor = '#ffffff'
      body.style.color = '#333333'
    }
  }

  return {
    currentUser,
    pageSettings,
    loading,
    loadUser,
    loadPageSettings,
    updatePageSettings,
    applySettings
  }
})
