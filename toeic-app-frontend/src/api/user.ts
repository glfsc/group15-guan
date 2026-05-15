import apiClient from './client'
import type { User, PageSettings } from '@/types/user'

function buildAnonymousUserPayload(learningGoal?: string) {
  const suffix = crypto.randomUUID().replace(/-/g, '').slice(0, 12)
  return {
    user_name: `Learner-${Date.now().toString().slice(-6)}`,
    email: `learner.${suffix}@example.com`,
    learning_goal: learningGoal
  }
}

export const userApi = {
  async createUser(data: { user_name: string; email: string; learning_goal?: string }): Promise<User> {
    const response = await apiClient.post('/settings/users', data)
    return response.data
  },

  async getUser(userId: string): Promise<User> {
    const response = await apiClient.get(`/settings/users/${userId}`)
    return response.data
  },

  async updateUser(userId: string, data: Partial<User>): Promise<User> {
    const response = await apiClient.put(`/settings/users/${userId}`, data)
    return response.data
  },

  async getPageSettings(userId: string): Promise<PageSettings> {
    const response = await apiClient.get(`/settings/page/${userId}`)
    return response.data
  },

  async updatePageSettings(userId: string, data: { font_size: string; background_color: string }): Promise<PageSettings> {
    const response = await apiClient.put(`/settings/page/${userId}`, data)
    return response.data
  },

  async ensureUser(learningGoal?: string): Promise<User> {
    const storedUserId = localStorage.getItem('userId')
    if (storedUserId) {
      try {
        return await this.getUser(storedUserId)
      } catch {
        localStorage.removeItem('userId')
      }
    }

    const user = await this.createUser(buildAnonymousUserPayload(learningGoal))
    localStorage.setItem('userId', user.user_id)
    return user
  }
}
