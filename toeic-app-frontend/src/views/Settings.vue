<template>
  <Layout>
    <div class="settings-page">
      <el-card>
        <h2>设置</h2>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="页面设置" name="page">
            <el-form label-width="100px" style="max-width: 500px">
              <el-form-item label="字体大小">
                <div class="font-size-control">
                  <el-slider
                    v-model="fontSizePercent"
                    :min="50"
                    :max="200"
                    :step="5"
                    :marks="fontMarks"
                    :format-tooltip="(v: number) => `${v}%`"
                    style="flex: 1; margin-right: 16px"
                  />
                  <el-input-number
                    v-model="fontSizePercent"
                    :min="50"
                    :max="200"
                    :step="5"
                    size="small"
                    style="width: 90px"
                  />
                  <span style="margin-left: 4px; color: var(--text-secondary, #909399)">%</span>
                </div>
              </el-form-item>

              <el-form-item label="背景颜色">
                <el-radio-group v-model="pageSettings.background_color" @change="updateSettings">
                  <el-radio label="light">浅色</el-radio>
                  <el-radio label="dark">深色</el-radio>
                  <el-radio label="eye_care">护眼</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="个人信息" name="profile">
            <el-form label-width="100px" style="max-width: 500px">
              <el-form-item label="姓名">
                <el-input v-model="userInfo.user_name" />
              </el-form-item>

              <el-form-item label="邮箱">
                <el-input v-model="userInfo.email" />
              </el-form-item>

              <el-form-item label="学习目标">
                <el-input
                  v-model="userInfo.learning_goal"
                  type="textarea"
                  :rows="3"
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="updateProfile">
                  保存个人信息
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { useSettingsStore } from '@/stores/settings'
import { userApi } from '@/api/user'

const settingsStore = useSettingsStore()
const activeTab = ref('page')
const userId = ref('')

const fontSizePercent = ref(100)
const fontMarks = { 50: '50%', 100: '100%', 150: '150%', 200: '200%' }

const pageSettings = reactive({
  font_size: '100',
  background_color: 'light'
})

const userInfo = reactive({
  user_name: '',
  email: '',
  learning_goal: ''
})

watch(fontSizePercent, () => {
  pageSettings.font_size = String(fontSizePercent.value)
  updateSettings()
})

onMounted(async () => {
  const user = await userApi.ensureUser('TOEIC learning settings')
  userId.value = user.user_id
  await loadSettings()
  await loadUserInfo()
})

async function loadSettings() {
  if (!userId.value) return
  try {
    const settings = await userApi.getPageSettings(userId.value)
    pageSettings.font_size = settings.font_size
    pageSettings.background_color = settings.background_color
    const parsed = parseInt(settings.font_size, 10)
    fontSizePercent.value = isNaN(parsed) ? 100 : Math.max(50, Math.min(200, parsed))
    settingsStore.applySettings(settings)
  } catch {
    console.error('Failed to load settings')
  }
}

async function loadUserInfo() {
  if (!userId.value) return
  try {
    const user = await userApi.getUser(userId.value)
    userInfo.user_name = user.user_name
    userInfo.email = user.email
    userInfo.learning_goal = user.learning_goal || ''
  } catch {
    console.error('Failed to load user info')
  }
}

async function updateSettings() {
  if (!userId.value) return
  try {
    await settingsStore.updatePageSettings(userId.value, {
      font_size: pageSettings.font_size,
      background_color: pageSettings.background_color
    })
    ElMessage.success('设置已保存')
  } catch {
    ElMessage.error('保存设置失败')
  }
}

async function updateProfile() {
  if (!userId.value) return
  try {
    await userApi.updateUser(userId.value, {
      user_name: userInfo.user_name,
      email: userInfo.email,
      learning_goal: userInfo.learning_goal
    })
    ElMessage.success('个人信息已保存')
  } catch {
    ElMessage.error('保存个人信息失败')
  }
}
</script>

<style scoped>
.settings-page {
  max-width: 800px;
  margin: 0 auto;
}

.font-size-control {
  display: flex;
  align-items: center;
  width: 100%;
}
</style>
