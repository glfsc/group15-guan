<template>
  <Layout>
    <div class="grammar-page">
      <el-card v-if="stage === 'config'" class="config-card animate-fade-in-up">
        <h2>
          <span class="title-icon">📝</span> 语法练习
        </h2>
        <el-form :inline="true" style="margin: 20px 0">
          <el-form-item label="知识点">
            <el-select v-model="knowledgePoint" style="width: 150px">
              <el-option label="时态" value="tense" />
              <el-option label="语态" value="voice" />
              <el-option label="从句" value="clause" />
              <el-option label="虚拟语气" value="subjunctive" />
            </el-select>
          </el-form-item>
          <el-form-item label="难度">
            <el-select v-model="difficulty" style="width: 120px">
              <el-option label="初级" value="easy" />
              <el-option label="中级" value="medium" />
              <el-option label="高级" value="hard" />
            </el-select>
          </el-form-item>
          <el-form-item label="数量">
            <el-input-number v-model="count" :min="1" :max="20" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="generateQuestions" :loading="loading">生成题目</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card v-else-if="stage === 'quiz' && currentQuestion" class="quiz-card animate-fade-in">
        <div class="quiz-header">
          <h2>{{ showPerQuestionFeedback ? '📝 语法练习解析' : '📝 语法练习进行中' }}</h2>
          <div class="progress-badge">
            <span class="progress-text">第 {{ currentIndex + 1 }} / {{ totalCount }} 题</span>
            <span class="timer-text">{{ formatTime(currentQuestionTime) }}</span>
            <span v-if="loadingMore" class="loading-more-badge">后续题目生成中...</span>
          </div>
        </div>

        <el-progress :percentage="progressPercent" :stroke-width="8" :color="progressColor" />

        <div class="question-item" :key="currentIndex">
          <h3 class="question-content">{{ currentQuestion.content }}</h3>
          <div class="options-group">
            <div
              v-for="(opt, idx) in currentOptionItems"
              :key="idx"
              class="option-item"
              :class="optionClass(idx)"
              @click="selectAnswer(idx)"
            >
              <span class="option-label">{{ opt.label }}</span>
              <span class="option-text">{{ opt.text }}</span>
              <span v-if="showPerQuestionFeedback && idx === currentResult?.correct_answer" class="option-tag tag-correct">✓ 正确</span>
              <span v-else-if="showPerQuestionFeedback && idx === answers[currentIndex] && idx !== currentResult?.correct_answer" class="option-tag tag-wrong">✗ 错误</span>
            </div>
          </div>

          <div v-if="showPerQuestionFeedback && currentResult" class="inline-result animate-fade-in-up">
            <el-alert
              :title="currentResult.is_correct ? '回答正确！' : '回答错误'"
              :type="currentResult.is_correct ? 'success' : 'error'"
              :closable="false"
              show-icon
            />
            <div class="analysis-card">
              <p><strong>你的答案：</strong>{{ optionLabel(answers[currentIndex]) }}</p>
              <p><strong>正确答案：</strong>{{ optionLabel(currentResult.correct_answer) }}</p>
              <p v-if="currentResult.grammar_rule"><strong>语法规则：</strong>{{ currentResult.grammar_rule }}</p>
              <p v-if="currentResult.example"><strong>例句：</strong>{{ currentResult.example }}</p>
            </div>
          </div>
        </div>

        <div class="actions">
          <el-button @click="prevQuestion" :disabled="currentIndex === 0">上一题</el-button>
          <el-button @click="nextQuestion" :disabled="currentIndex === questions.length - 1">下一题</el-button>
          <el-button v-if="!showPerQuestionFeedback" type="success" @click="submitAllAnswers" :loading="submitting">提交练习</el-button>
          <el-button v-else type="primary" @click="stage = 'result'">查看总结果</el-button>
        </div>
      </el-card>

      <el-card v-else class="result-card animate-fade-in-up">
        <h2>🎯 练习结果</h2>
        <div class="result-summary">
          <div class="summary-item">
            <span class="summary-value">{{ accuracy }}%</span>
            <span class="summary-label">正确率</span>
          </div>
          <div class="summary-item">
            <span class="summary-value">{{ correctCount }}/{{ questions.length }}</span>
            <span class="summary-label">正确/总题数</span>
          </div>
          <div class="summary-item">
            <span class="summary-value">{{ formatTime(totalTime) }}</span>
            <span class="summary-label">总用时</span>
          </div>
        </div>

        <div v-for="(q, index) in questions" :key="q.question_id" class="result-item" :style="{ animationDelay: `${index * 0.05}s` }">
          <div class="result-header">
            <h3>第 {{ index + 1 }} 题</h3>
            <el-tag :type="resultMap[index]?.is_correct ? 'success' : 'danger'" effect="dark" round>
              {{ resultMap[index]?.is_correct ? '✓ 正确' : '✗ 错误' }}
            </el-tag>
          </div>
          <p>{{ q.content }}</p>
          <p><strong>你的答案：</strong>{{ optionLabel(answers[index]) }}</p>
          <p><strong>正确答案：</strong>{{ optionLabel(resultMap[index]?.correct_answer ?? -1) }}</p>
          <p v-if="resultMap[index]?.grammar_rule"><strong>语法规则：</strong>{{ resultMap[index]?.grammar_rule }}</p>
          <p v-if="resultMap[index]?.example"><strong>例句：</strong>{{ resultMap[index]?.example }}</p>
          <el-button text type="primary" @click="goToQuestionReview(index)">回到本题查看解析</el-button>
        </div>

        <div class="result-actions">
          <el-button @click="backToQuizReview">逐题查看解析</el-button>
          <el-button type="primary" @click="restart">再练一次</el-button>
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { computed, ref, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { AxiosError } from 'axios'
import Layout from '@/components/Layout.vue'
import { questionApi } from '@/api/questions'
import { answerApi } from '@/api/answers'
import { userApi } from '@/api/user'
import type { GrammarQuestion } from '@/types/question'
import type { AnswerResult } from '@/types/answer'

const knowledgePoint = ref('tense')
const difficulty = ref('medium')
const count = ref(10)
const loading = ref(false)
const submitting = ref(false)
const loadingMore = ref(false)
const stage = ref<'config' | 'quiz' | 'result'>('config')
const showPerQuestionFeedback = ref(false)

const BATCH_SIZE = 3

const questions = ref<GrammarQuestion[]>([])
const answers = ref<number[]>([])
const resultMap = ref<Record<number, AnswerResult>>({})
const currentIndex = ref(0)
const totalCount = ref(0)
let abortGeneration = false

const questionStartTimes = ref<number[]>([])
const questionTimes = ref<number[]>([])
let timerInterval: ReturnType<typeof setInterval> | null = null
const currentQuestionTime = ref(0)

const currentQuestion = computed(() => questions.value[currentIndex.value])
const currentResult = computed(() => resultMap.value[currentIndex.value])
const progressPercent = computed(() => Math.round(((currentIndex.value + 1) / Math.max(totalCount.value, 1)) * 100))
const progressColor = computed(() => {
  if (progressPercent.value < 30) return '#409eff'
  if (progressPercent.value < 70) return '#e6a23c'
  return '#67c23a'
})
const correctCount = computed(() => Object.values(resultMap.value).filter(r => r.is_correct).length)
const accuracy = computed(() => questions.value.length ? ((correctCount.value / questions.value.length) * 100).toFixed(1) : '0.0')
const totalTime = computed(() => questionTimes.value.reduce((a, b) => a + b, 0))

const currentOptionItems = computed(() => {
  const opts = currentQuestion.value?.options
  if (!opts) return []
  return [
    { label: 'A', text: opts.option_0 },
    { label: 'B', text: opts.option_1 },
    { label: 'C', text: opts.option_2 },
    { label: 'D', text: opts.option_3 }
  ]
})

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function startTimer() {
  stopTimer()
  currentQuestionTime.value = 0
  timerInterval = setInterval(() => {
    currentQuestionTime.value += 1
  }, 1000)
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

function recordCurrentQuestionTime() {
  const idx = currentIndex.value
  if (idx >= 0 && idx < questionTimes.value.length) {
    questionTimes.value[idx] = currentQuestionTime.value
  }
}

watch(currentIndex, () => {
  recordCurrentQuestionTime()
  if (stage.value === 'quiz' && !showPerQuestionFeedback.value) {
    startTimer()
  }
})

onUnmounted(() => {
  stopTimer()
})

function selectAnswer(index: number) {
  if (showPerQuestionFeedback.value) return
  answers.value[currentIndex.value] = index
}

function optionClass(index: number): Record<string, boolean> {
  const selected = answers.value[currentIndex.value] === index
  if (!showPerQuestionFeedback.value) {
    return { 'option-selected': selected, 'option-default': !selected }
  }
  const isCorrect = currentResult.value?.correct_answer === index
  const isWrong = selected && !isCorrect
  return { 'option-correct': isCorrect, 'option-wrong': isWrong }
}

async function ensureUserId(): Promise<string> {
  const user = await userApi.ensureUser('TOEIC grammar practice')
  return user.user_id
}

function appendQuestions(newQuestions: GrammarQuestion[]) {
  questions.value.push(...newQuestions)
  while (answers.value.length < questions.value.length) answers.value.push(-1)
  while (questionTimes.value.length < questions.value.length) questionTimes.value.push(0)
  while (questionStartTimes.value.length < questions.value.length) questionStartTimes.value.push(Date.now())
}

async function generateQuestions() {
  loading.value = true
  abortGeneration = false
  totalCount.value = count.value
  try {
    const firstBatch = await questionApi.generateGrammar(knowledgePoint.value, difficulty.value, Math.min(BATCH_SIZE, count.value))
    if (!firstBatch.length) {
      ElMessage.warning('生成成功但未返回题目，请重试')
      return
    }

    questions.value = firstBatch
    answers.value = new Array(firstBatch.length).fill(-1)
    questionTimes.value = new Array(firstBatch.length).fill(0)
    questionStartTimes.value = new Array(firstBatch.length).fill(Date.now())
    resultMap.value = {}
    currentIndex.value = 0
    showPerQuestionFeedback.value = false
    stage.value = 'quiz'
    startTimer()
    ElMessage.success(`首批${firstBatch.length}道题目已就绪，共${count.value}题`)

    if (firstBatch.length < count.value) {
      loadMoreQuestions(count.value - firstBatch.length)
    }
  } catch (error) {
    const apiError = error as AxiosError<{ detail?: string }>
    ElMessage.error(apiError.response?.data?.detail || '生成题目失败')
  } finally {
    loading.value = false
  }
}

async function loadMoreQuestions(remaining: number) {
  loadingMore.value = true
  let left = remaining
  while (left > 0 && !abortGeneration) {
    const batchCount = Math.min(BATCH_SIZE, left)
    try {
      const batch = await questionApi.generateGrammar(knowledgePoint.value, difficulty.value, batchCount)
      if (batch.length > 0) {
        appendQuestions(batch)
        left -= batch.length
      } else {
        break
      }
    } catch {
      ElMessage.warning('部分题目生成失败，已就绪的题目仍可作答')
      break
    }
  }
  loadingMore.value = false
}

function prevQuestion() {
  if (currentIndex.value > 0) currentIndex.value -= 1
}

function nextQuestion() {
  if (currentIndex.value < questions.value.length - 1) currentIndex.value += 1
}

function optionLabel(index: number): string {
  return ['A', 'B', 'C', 'D'][index] || '-'
}

async function submitAllAnswers() {
  const availableAnswers = answers.value.slice(0, questions.value.length)
  const unfinished = availableAnswers.findIndex(a => a === -1)
  if (unfinished !== -1) {
    ElMessage.warning(`请先完成第${unfinished + 1}题`)
    currentIndex.value = unfinished
    return
  }

  if (loadingMore.value) {
    try {
      await ElMessageBox.confirm('后续题目仍在生成中，确定只提交当前已就绪的题目吗？', '提示', { type: 'warning' })
    } catch {
      return
    }
  }

  recordCurrentQuestionTime()
  stopTimer()
  submitting.value = true
  try {
    const userId = await ensureUserId()
    const entries: Record<number, AnswerResult> = {}

    for (const [index, q] of questions.value.entries()) {
      entries[index] = await answerApi.submitAnswer({
        user_id: userId,
        question_id: q.question_id,
        question_type: 'grammar',
        user_answer: answers.value[index],
        time_spent: questionTimes.value[index] || 0
      })
    }

    resultMap.value = entries
    showPerQuestionFeedback.value = true
    stage.value = 'quiz'
    currentIndex.value = 0
    ElMessage.success('提交成功，现在可以逐题查看对错与解析')
  } catch (error) {
    const apiError = error as AxiosError<{ detail?: string }>
    ElMessage.error(apiError.response?.data?.detail || '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

function goToQuestionReview(index: number) {
  currentIndex.value = index
  stage.value = 'quiz'
  showPerQuestionFeedback.value = true
}

function backToQuizReview() {
  currentIndex.value = 0
  stage.value = 'quiz'
  showPerQuestionFeedback.value = true
}

function restart() {
  abortGeneration = true
  stopTimer()
  stage.value = 'config'
  questions.value = []
  answers.value = []
  resultMap.value = {}
  currentIndex.value = 0
  showPerQuestionFeedback.value = false
  questionStartTimes.value = []
  questionTimes.value = []
  loadingMore.value = false
  totalCount.value = 0
}
</script>

<style scoped>
.grammar-page {
  max-width: 1000px;
  margin: 0 auto;
}

.config-card, .quiz-card, .result-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  background: var(--bg-card, #fff);
}

.title-icon {
  font-size: 28px;
  margin-right: 8px;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-badge {
  display: flex;
  gap: 12px;
  align-items: center;
}

.progress-text {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.timer-text {
  background: rgba(230, 162, 60, 0.15);
  color: #e6a23c;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.loading-more-badge {
  background: rgba(64, 158, 255, 0.12);
  color: #409eff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  animation: pulse 2s ease-in-out infinite;
}

.question-item {
  margin: 24px 0;
  padding: 24px;
  background: var(--bg-question, #f9f9f9);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.question-content {
  line-height: 1.7;
  color: var(--text-primary, #333);
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  border: 2px solid var(--border-color, #e0e0e0);
  background: var(--bg-card, #fff);
}

.option-default:hover {
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.05);
  transform: translateX(4px);
}

.option-selected {
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.1);
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.option-correct {
  border-color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
}

.option-wrong {
  border-color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.option-label {
  min-width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.option-selected .option-label {
  background: linear-gradient(135deg, #337ecc, #409eff);
}

.option-text {
  flex: 1;
  line-height: 1.6;
  color: var(--text-primary, #333);
}

.option-tag {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 12px;
  white-space: nowrap;
}

.tag-correct {
  background: rgba(103, 194, 58, 0.15);
  color: #67c23a;
}

.tag-wrong {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
}

.inline-result {
  margin-top: 20px;
}

.analysis-card {
  margin-top: 12px;
  padding: 16px;
  background: var(--bg-card, #fff);
  border: 1px solid var(--border-light, #ebeef5);
  border-radius: 12px;
}

.result-summary {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin: 24px 0;
  padding: 20px;
  background: var(--bg-question, #f9f9f9);
  border-radius: 12px;
}

.summary-item {
  text-align: center;
}

.summary-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.summary-label {
  font-size: 13px;
  color: var(--text-secondary, #909399);
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.result-item {
  margin: 16px 0;
  padding: 16px;
  border: 1px solid var(--border-color, #eee);
  border-radius: 12px;
  background: var(--bg-card, #fff);
  animation: fadeInUp 0.4s ease-out both;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.result-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}
</style>
