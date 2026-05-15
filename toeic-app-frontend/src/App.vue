<template>
  <div id="app" :class="themeClass">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

const themeClass = computed(() => {
  const bg = settingsStore.pageSettings?.background_color || 'light'
  return `theme-${bg.replace('_', '-')}`
})

onMounted(async () => {
  const userId = localStorage.getItem('userId')
  if (userId) {
    await settingsStore.loadPageSettings(userId)
  }
})
</script>

<style>
.theme-light {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-card: #ffffff;
  --bg-question: #f9f9f9;
  --bg-aside: #ffffff;
  --text-primary: #333333;
  --text-secondary: #909399;
  --border-color: #e0e0e0;
  --border-light: #ebeef5;
}

.theme-dark {
  --bg-primary: #2d2d2d;
  --bg-secondary: #1e1e1e;
  --bg-card: #363636;
  --bg-question: #333333;
  --bg-aside: #252525;
  --text-primary: #e0e0e0;
  --text-secondary: #aaaaaa;
  --border-color: #444444;
  --border-light: #3a3a3a;
}

.theme-eye-care {
  --bg-primary: #c7edcc;
  --bg-secondary: #b5e2ba;
  --bg-card: #d4f5d8;
  --bg-question: #d0f0d4;
  --bg-aside: #bde6c2;
  --text-primary: #333333;
  --text-secondary: #666666;
  --border-color: #a0d8a5;
  --border-light: #b8e4bc;
}
</style>

<style scoped>
#app {
  width: 100%;
  min-height: 100vh;
  transition: background-color 0.3s ease, color 0.3s ease;
}
</style>
