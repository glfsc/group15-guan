import apiClient from './client'
import type { AnswerSubmit, AnswerResult } from '@/types/answer'

export const answerApi = {
  async submitAnswer(data: AnswerSubmit): Promise<AnswerResult> {
    const response = await apiClient.post('/answers/submit', data)
    return response.data
  }
}
