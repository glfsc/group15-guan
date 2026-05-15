<template>
  <div class="layout">
    <el-container>
      <el-aside width="200px">
        <div class="logo">
          <div class="logo-icon">T</div>
          <h2>托业学习</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          class="menu"
        >
          <el-menu-item index="/practice">
            <el-icon><Edit /></el-icon>
            <span>开始练习</span>
          </el-menu-item>
          <el-menu-item index="/listening">
            <el-icon><Headset /></el-icon>
            <span>听力练习</span>
          </el-menu-item>
          <el-menu-item index="/grammar">
            <el-icon><Document /></el-icon>
            <span>语法练习</span>
          </el-menu-item>
          <el-menu-item index="/progress">
            <el-icon><TrendCharts /></el-icon>
            <span>学习进度</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <slot />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.layout {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: var(--bg-aside, #ffffff);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.logo-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo h2 {
  margin: 0;
  color: #409eff;
  font-size: 20px;
}

.menu {
  border: none;
  background-color: transparent;
}

:deep(.el-menu-item) {
  color: var(--text-primary, #333);
}

:deep(.el-menu-item.is-active) {
  color: #409eff;
}

.el-main {
  background-color: var(--bg-secondary, #f5f5f5);
  padding: 20px;
  transition: background-color 0.3s ease;
}
</style>
