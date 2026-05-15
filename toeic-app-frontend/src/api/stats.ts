import apiClient from './client'

export interface ProgressData {
  user_id: string
  total_questions: number
  listening_questions: number
  grammar_questions: number
  overall_accuracy: number
  listening_accuracy: number
  grammar_accuracy: number
  total_practice_time: number
  listening_level: string
  grammar_level: string
  updated_at: string
}

export interface ErrorQuestion {
  record_id: string
  question_id: string
  question_type: string
  user_answer: number
  correct_answer: number
  error_count: number
  first_error_time: string
  last_error_time: string
}

export interface PracticeHistory {
  record_id: string
  question_id: string
  question_type: string
  user_answer: number
  is_correct: boolean
  time_spent: number
  answered_at: string
}

export interface DailyStats {
  date: string
  total_questions: number
  correct_questions: number
  accuracy: number
}

export const statsApi = {
  async getProgress(userId: string): Promise<ProgressData> {
    const response = await apiClient.get(`/stats/progress/${userId}`)
    return response.data
  },

  async getErrorQuestions(userId: string, limit: number = 20): Promise<ErrorQuestion[]> {
    const response = await apiClient.get(`/stats/errors/${userId}?limit=${limit}`)
    return response.data
  },

  async deleteErrorQuestion(userId: string, questionId: string): Promise<void> {
    await apiClient.delete(`/stats/errors/${userId}/${questionId}`)
  },

  async getPracticeHistory(userId: string, limit: number = 50): Promise<PracticeHistory[]> {
    const response = await apiClient.get(`/stats/history/${userId}?limit=${limit}`)
    return response.data
  },

  async getDailyStats(userId: string, days: number = 7): Promise<DailyStats[]> {
    const response = await apiClient.get(`/stats/daily/${userId}?days=${days}`)
    return response.data
  }
}
