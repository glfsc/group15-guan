import apiClient from './client'
import type { ListeningQuestion, GrammarQuestion } from '@/types/question'

const GENERATION_TIMEOUT = 120000
const LISTENING_GENERATION_TIMEOUT = 300000

export const questionApi = {
  async generateListening(
    difficulty: string,
    questionType: string,
    count: number = 10
  ): Promise<ListeningQuestion[]> {
    const response = await apiClient.post(
      `/questions/listening/generate?difficulty=${difficulty}&question_type=${questionType}&count=${count}`,
      undefined,
      { timeout: LISTENING_GENERATION_TIMEOUT }
    )
    return response.data
  },

  async generateGrammar(
    knowledgePoint: string,
    difficulty: string,
    count: number = 10
  ): Promise<GrammarQuestion[]> {
    const response = await apiClient.post(
      `/questions/grammar/generate?knowledge_point=${knowledgePoint}&difficulty=${difficulty}&count=${count}`,
      undefined,
      { timeout: GENERATION_TIMEOUT }
    )
    return response.data
  },

  async getListening(questionId: string): Promise<ListeningQuestion> {
    const response = await apiClient.get(`/questions/listening/${questionId}`)
    return response.data
  },

  async getGrammar(questionId: string): Promise<GrammarQuestion> {
    const response = await apiClient.get(`/questions/grammar/${questionId}`)
    return response.data
  }
}
