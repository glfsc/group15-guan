<template>
  <Layout>
    <div class="progress-page">
      <el-card class="main-card animate-fade-in-up">
        <h2><span class="title-icon">📊</span> 学习进度</h2>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="8">
            <div class="stat-card stat-total animate-bounce-in" style="animation-delay: 0s">
              <div class="stat-icon">📚</div>
              <div class="stat-value">{{ progress?.total_questions || 0 }}</div>
              <div class="stat-label">完成题数</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-card stat-accuracy animate-bounce-in" style="animation-delay: 0.1s">
              <div class="stat-icon">🎯</div>
              <div class="stat-value">{{ progress?.overall_accuracy?.toFixed(1) || 0 }}%</div>
              <div class="stat-label">总体正确率</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-card stat-time animate-bounce-in" style="animation-delay: 0.2s">
              <div class="stat-icon">⏱</div>
              <div class="stat-value">{{ formatTime(progress?.total_practice_time || 0) }}</div>
              <div class="stat-label">学习时长</div>
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="12">
            <div class="ability-card animate-fade-in-up" style="animation-delay: 0.2s">
              <h3>🎧 听力能力</h3>
              <div class="ability-row">
                <span class="ability-label">完成题数</span>
                <span class="ability-value">{{ progress?.listening_questions || 0 }}</span>
              </div>
              <div class="ability-row">
                <span class="ability-label">正确率</span>
                <span class="ability-value">{{ progress?.listening_accuracy?.toFixed(1) || 0 }}%</span>
              </div>
              <div class="ability-row">
                <span class="ability-label">能力等级</span>
                <el-tag :type="levelTagType(progress?.listening_level)" effect="dark" round>{{ levelLabel(progress?.listening_level) }}</el-tag>
              </div>
              <el-progress :percentage="progress?.listening_accuracy || 0" :stroke-width="6" :color="'#409eff'" style="margin-top: 8px" />
            </div>
          </el-col>
          <el-col :span="12">
            <div class="ability-card animate-fade-in-up" style="animation-delay: 0.3s">
              <h3>📝 语法能力</h3>
              <div class="ability-row">
                <span class="ability-label">完成题数</span>
                <span class="ability-value">{{ progress?.grammar_questions || 0 }}</span>
              </div>
              <div class="ability-row">
                <span class="ability-label">正确率</span>
                <span class="ability-value">{{ progress?.grammar_accuracy?.toFixed(1) || 0 }}%</span>
              </div>
              <div class="ability-row">
                <span class="ability-label">能力等级</span>
                <el-tag :type="levelTagType(progress?.grammar_level)" effect="dark" round>{{ levelLabel(progress?.grammar_level) }}</el-tag>
              </div>
              <el-progress :percentage="progress?.grammar_accuracy || 0" :stroke-width="6" :color="'#67c23a'" style="margin-top: 8px" />
            </div>
          </el-col>
        </el-row>
      </el-card>

      <el-card class="error-card animate-fade-in-up" style="margin-top: 20px; animation-delay: 0.4s">
        <div class="error-header">
          <h2><span class="title-icon">❌</span> 错题集</h2>
          <el-button v-if="errorQuestions.length > 0" type="primary" @click="startRedo" :disabled="redoing">错题重做</el-button>
        </div>

        <div v-if="!redoing">
          <el-empty v-if="errorQuestions.length === 0" description="暂无错题，继续加油！" />
          <div v-else class="error-list">
            <div v-for="(eq, index) in errorQuestions" :key="eq.question_id" class="error-item" :style="{ animationDelay: `${index * 0.05}s` }">
              <div class="error-info">
                <el-tag :type="eq.question_type === 'listening' ? 'primary' : 'success'" effect="plain" size="small">
                  {{ eq.question_type === 'listening' ? '听力' : '语法' }}
                </el-tag>
                <span class="error-id">题目 #{{ eq.question_id.slice(0, 8) }}</span>
                <span class="error-count">错误 {{ eq.error_count }} 次</span>
                <span class="error-time">{{ formatDateTime(eq.last_error_time) }}</span>
              </div>
              <div class="error-detail">
                <span>你的答案：<strong>{{ optionLabel(eq.user_answer) }}</strong></span>
                <span>正确答案：<strong class="correct-text">{{ optionLabel(eq.correct_answer) }}</strong></span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="redo-section">
          <div class="redo-header">
            <h3>错题重做 ({{ redoIndex + 1 }}/{{ redoQuestions.length }})</h3>
            <el-button @click="cancelRedo">退出重做</el-button>
          </div>

          <div v-if="currentRedoQuestion" class="redo-question animate-fade-in">
            <p class="redo-question-text">{{ currentRedoQuestion.displayText }}</p>
            <div class="redo-options">
              <div
                v-for="(opt, idx) in currentRedoQuestion.options"
                :key="idx"
                class="redo-option"
                :class="{ 'redo-option-selected': redoAnswer === idx, 'redo-option-correct': redoSubmitted && idx === currentRedoQuestion.correctAnswer, 'redo-option-wrong': redoSubmitted && redoAnswer === idx && idx !== currentRedoQuestion.correctAnswer }"
                @click="selectRedoAnswer(idx)"
              >
                <span class="option-label">{{ optionLabel(idx) }}</span>
                <span>{{ opt }}</span>
              </div>
            </div>

            <div v-if="redoSubmitted" class="redo-result animate-fade-in-up">
              <el-alert
                :title="redoAnswer === currentRedoQuestion.correctAnswer ? '回答正确！错题已消除' : '回答错误，请继续努力'"
                :type="redoAnswer === currentRedoQuestion.correctAnswer ? 'success' : 'error'"
                :closable="false"
                show-icon
              />
              <el-button type="primary" style="margin-top: 16px" @click="nextRedoQuestion">
                {{ redoIndex < redoQuestions.length - 1 ? '下一题' : '完成重做' }}
              </el-button>
            </div>
            <el-button v-else type="success" style="margin-top: 16px" :disabled="redoAnswer === -1" @click="submitRedoAnswer">提交答案</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { statsApi } from '@/api/stats'
import { questionApi } from '@/api/questions'
import { answerApi } from '@/api/answers'
import { userApi } from '@/api/user'
import type { ProgressData, ErrorQuestion } from '@/api/stats'
import type { ListeningQuestion, GrammarQuestion } from '@/types/question'
import type { AnswerResult } from '@/types/answer'

const progress = ref<ProgressData | null>(null)
const errorQuestions = ref<ErrorQuestion[]>([])
const userId = ref('')

const redoing = ref(false)
const redoQuestions = ref<RedoQuestion[]>([])
const redoIndex = ref(0)
const redoAnswer = ref(-1)
const redoSubmitted = ref(false)

interface RedoQuestion {
  questionId: string
  questionType: string
  displayText: string
  options: string[]
  correctAnswer: number
}

const currentRedoQuestion = computed(() => redoQuestions.value[redoIndex.value] || null)

function getOrCreateUserId(): string {
  const existing = localStorage.getItem('userId')
  if (existing) return existing
  const newId = crypto.randomUUID()
  localStorage.setItem('userId', newId)
  return newId
}

function formatTime(totalSeconds: number): string {
  if (!totalSeconds) return '0分钟'
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  if (hours > 0) return `${hours}小时${minutes}分`
  if (minutes > 0) return `${minutes}分${seconds}秒`
  return `${seconds}秒`
}

function formatDateTime(isoStr: string): string {
  const d = new Date(isoStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}

function optionLabel(index: number): string {
  return ['A', 'B', 'C', 'D'][index] || '-'
}

function levelLabel(level?: string): string {
  if (level === 'advanced') return '高级'
  if (level === 'intermediate') return '中级'
  return '初级'
}

function levelTagType(level?: string): string {
  if (level === 'advanced') return 'success'
  if (level === 'intermediate') return 'warning'
  return 'info'
}

onMounted(async () => {
  userId.value = getOrCreateUserId()
  await loadData()
})

async function loadData() {
  try {
    progress.value = await statsApi.getProgress(userId.value)
  } catch {
    ElMessage.error('获取进度失败')
  }
  try {
    errorQuestions.value = await statsApi.getErrorQuestions(userId.value, 50)
  } catch {
    console.error('获取错题失败')
  }
}

async function startRedo() {
  if (errorQuestions.value.length === 0) return

  const questions: RedoQuestion[] = []
  for (const eq of errorQuestions.value) {
    try {
      if (eq.question_type === 'listening') {
        const q = await questionApi.getListening(eq.question_id) as ListeningQuestion
        questions.push({
          questionId: eq.question_id,
          questionType: 'listening',
          displayText: q.question,
          options: [q.options.option_0, q.options.option_1, q.options.option_2, q.options.option_3],
          correctAnswer: q.correct_answer
        })
      } else {
        const q = await questionApi.getGrammar(eq.question_id) as GrammarQuestion
        questions.push({
          questionId: eq.question_id,
          questionType: 'grammar',
          displayText: q.content,
          options: [q.options.option_0, q.options.option_1, q.options.option_2, q.options.option_3],
          correctAnswer: q.correct_answer
        })
      }
    } catch {
      console.error(`Failed to load question ${eq.question_id}`)
    }
  }

  if (questions.length === 0) {
    ElMessage.warning('无法加载错题详情')
    return
  }

  redoQuestions.value = questions
  redoIndex.value = 0
  redoAnswer.value = -1
  redoSubmitted.value = false
  redoing.value = true
}

function cancelRedo() {
  redoing.value = false
  redoQuestions.value = []
  redoIndex.value = 0
  redoAnswer.value = -1
  redoSubmitted.value = false
}

function selectRedoAnswer(index: number) {
  if (redoSubmitted.value) return
  redoAnswer.value = index
}

async function submitRedoAnswer() {
  if (redoAnswer.value === -1) return
  redoSubmitted.value = true

  const q = currentRedoQuestion.value!
  const isCorrect = redoAnswer.value === q.correctAnswer

  if (isCorrect) {
    try {
      await statsApi.deleteErrorQuestion(userId.value, q.questionId)
    } catch {
      console.error('Failed to delete error question')
    }
  }

  try {
    const user = await userApi.ensureUser('TOEIC error redo')
    await answerApi.submitAnswer({
      user_id: user.user_id,
      question_id: q.questionId,
      question_type: q.questionType,
      user_answer: redoAnswer.value,
      time_spent: 0
    })
  } catch {
    console.error('Failed to submit redo answer')
  }
}

async function nextRedoQuestion() {
  if (redoIndex.value < redoQuestions.value.length - 1) {
    redoIndex.value += 1
    redoAnswer.value = -1
    redoSubmitted.value = false
  } else {
    ElMessage.success('错题重做完成！')
    cancelRedo()
    await loadData()
  }
}
</script>

<style scoped>
.progress-page {
  max-width: 1000px;
  margin: 0 auto;
}

.main-card, .error-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  background: var(--bg-card, #fff);
}

.title-icon {
  font-size: 24px;
  margin-right: 8px;
}

.stat-card {
  text-align: center;
  padding: 24px 16px;
  border-radius: 16px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-total {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(64, 158, 255, 0.05));
}

.stat-accuracy {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1), rgba(103, 194, 58, 0.05));
}

.stat-time {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.1), rgba(230, 162, 60, 0.05));
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #333);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary, #909399);
  margin-top: 4px;
}

.ability-card {
  padding: 20px;
  border-radius: 12px;
  background: var(--bg-question, #f9f9f9);
  border: 1px solid var(--border-light, #ebeef5);
}

.ability-card h3 {
  margin-bottom: 12px;
  color: var(--text-primary, #333);
}

.ability-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.ability-label {
  color: var(--text-secondary, #909399);
}

.ability-value {
  font-weight: 600;
  color: var(--text-primary, #333);
}

.error-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.error-header h2 {
  margin: 0;
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.error-item {
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--bg-question, #f9f9f9);
  border: 1px solid var(--border-light, #ebeef5);
  animation: fadeInUp 0.3s ease-out both;
  transition: transform 0.2s ease;
}

.error-item:hover {
  transform: translateX(4px);
}

.error-info {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 8px;
}

.error-id {
  font-size: 13px;
  color: var(--text-secondary, #909399);
  font-family: monospace;
}

.error-count {
  font-size: 13px;
  color: #f56c6c;
  font-weight: 600;
}

.error-time {
  font-size: 12px;
  color: var(--text-secondary, #909399);
  margin-left: auto;
}

.error-detail {
  display: flex;
  gap: 20px;
  font-size: 14px;
}

.correct-text {
  color: #67c23a;
}

.redo-section {
  padding: 20px 0;
}

.redo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.redo-question {
  padding: 20px;
  background: var(--bg-question, #f9f9f9);
  border-radius: 12px;
}

.redo-question-text {
  font-size: 16px;
  line-height: 1.7;
  margin-bottom: 16px;
  color: var(--text-primary, #333);
}

.redo-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.redo-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid var(--border-color, #e0e0e0);
  background: var(--bg-card, #fff);
}

.redo-option:hover {
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.05);
}

.redo-option-selected {
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.1);
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.redo-option-correct {
  border-color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
}

.redo-option-wrong {
  border-color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.option-label {
  min-width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.redo-result {
  margin-top: 16px;
}
</style>
