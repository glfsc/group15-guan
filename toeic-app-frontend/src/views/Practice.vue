<template>
  <Layout>
    <div class="practice-page">
      <el-card class="welcome-card animate-fade-in-up">
        <div class="welcome-decoration">
          <div class="deco-circle deco-circle-1"></div>
          <div class="deco-circle deco-circle-2"></div>
          <div class="deco-circle deco-circle-3"></div>
        </div>
        <h1 class="welcome-title">欢迎使用托业学习应用</h1>
        <p class="welcome-subtitle">选择练习类型，开始提升你的英语能力</p>
        
        <el-row :gutter="24" style="margin-top: 40px">
          <el-col :span="12">
            <el-card shadow="hover" class="practice-card listening-card animate-fade-in-up" @click="goToListening" style="animation-delay: 0.1s">
              <div class="card-icon-wrapper listening-icon-bg">
                <el-icon :size="48" color="#fff"><Headset /></el-icon>
              </div>
              <h3>听力练习</h3>
              <p>提高听力理解能力，适应托业考试听力题型</p>
              <div class="card-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover" class="practice-card grammar-card animate-fade-in-up" @click="goToGrammar" style="animation-delay: 0.2s">
              <div class="card-icon-wrapper grammar-icon-bg">
                <el-icon :size="48" color="#fff"><Document /></el-icon>
              </div>
              <h3>语法练习</h3>
              <p>巩固语法知识，掌握托业考试核心语法点</p>
              <div class="card-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import Layout from '@/components/Layout.vue'

const router = useRouter()

function goToListening() {
  router.push('/listening')
}

function goToGrammar() {
  router.push('/grammar')
}
</script>

<style scoped>
.practice-page {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  padding: 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
  background: var(--bg-card, #fff);
  border: none;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.welcome-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
}

.deco-circle-1 {
  width: 300px;
  height: 300px;
  background: #409eff;
  top: -100px;
  right: -50px;
  animation: pulse 6s ease-in-out infinite;
}

.deco-circle-2 {
  width: 200px;
  height: 200px;
  background: #67c23a;
  bottom: -60px;
  left: -40px;
  animation: pulse 8s ease-in-out infinite 2s;
}

.deco-circle-3 {
  width: 150px;
  height: 150px;
  background: #e6a23c;
  top: 50%;
  left: 50%;
  animation: pulse 10s ease-in-out infinite 4s;
}

.welcome-title {
  font-size: 32px;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  color: var(--text-secondary, #909399);
  font-size: 16px;
}

.practice-card {
  cursor: pointer;
  padding: 32px 24px;
  text-align: center;
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  border-radius: 16px;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
  background: var(--bg-card, #fff);
}

.practice-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.6s ease;
}

.practice-card:hover::before {
  left: 100%;
}

.practice-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.listening-card:hover {
  border-color: #409eff;
}

.grammar-card:hover {
  border-color: #67c23a;
}

.card-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  transition: transform 0.3s ease;
}

.practice-card:hover .card-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.listening-icon-bg {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.3);
}

.grammar-icon-bg {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  box-shadow: 0 8px 24px rgba(103, 194, 58, 0.3);
}

.practice-card h3 {
  margin: 0 0 10px;
  font-size: 22px;
  color: var(--text-primary, #333);
}

.practice-card p {
  color: var(--text-secondary, #909399);
  margin: 0;
}

.card-arrow {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0;
  transition: all 0.3s ease;
  color: #409eff;
  font-size: 20px;
}

.practice-card:hover .card-arrow {
  opacity: 1;
  right: 16px;
}
</style>
