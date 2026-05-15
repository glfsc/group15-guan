export interface AnswerSubmit {
  user_id: string
  question_id: string
  question_type: string
  user_answer: number
  time_spent: number
}

export interface AnswerResult {
  is_correct: boolean
  correct_answer: number
  analysis?: string
  grammar_rule?: string
  example?: string
}
