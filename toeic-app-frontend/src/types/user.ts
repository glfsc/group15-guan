export interface User {
  user_id: string
  user_name: string
  email: string
  learning_goal?: string
  created_at: string
  updated_at: string
}

export interface PageSettings {
  setting_id: string
  user_id: string
  font_size: string
  background_color: string
  updated_at: string
}

export interface Progress {
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
