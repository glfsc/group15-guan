export interface ListeningQuestion {
  question_id: string
  question: string
  audio_url: string
  audio_duration: number
  image_url?: string
  script_reference?: string
  options: {
    option_0: string
    option_1: string
    option_2: string
    option_3: string
  }
  correct_answer: number
  analysis?: string
  difficulty: string
  question_type: string
  created_at: string
}

export interface GrammarQuestion {
  question_id: string
  content: string
  question_mark: string
  options: {
    option_0: string
    option_1: string
    option_2: string
    option_3: string
  }
  correct_answer: number
  grammar_rule?: string
  example?: string
  knowledge_point: string
  difficulty: string
  created_at: string
}
