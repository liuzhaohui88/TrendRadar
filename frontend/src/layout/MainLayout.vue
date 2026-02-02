<template>
  <n-layout class="main-layout" has-sider>
    <!-- 侧边栏 -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="logo" :class="{ collapsed }">
        <span class="icon">📡</span>
        <span v-if="!collapsed" class="text">TrendRadar</span>
      </div>

      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="currentRoute"
        @update:value="handleMenuClick"
      />

      <div class="sider-footer">
        <n-button quaternary circle @click="handleLogout">
          <template #icon>
            <n-icon><LogOutOutline /></n-icon>
          </template>
        </n-button>
      </div>
    </n-layout-sider>

    <!-- 主内容区 -->
    <n-layout>
      <n-layout-header bordered class="header">
        <div class="header-left">
          <h2>{{ currentTitle }}</h2>
        </div>
        <div class="header-right">
          <n-tag type="success" size="small">Nina v5.5</n-tag>
        </div>
      </n-layout-header>

      <n-layout-content class="content">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage, NIcon } from 'naive-ui'
import {
  StatsChartOutline,
  GlobeOutline,
  KeyOutline,
  SendOutline,
  GitBranchOutline,
  NewspaperOutline,
  LogOutOutline
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const collapsed = ref(false)

const renderIcon = (icon: any) => () => h(NIcon, null, { default: () => h(icon) })

const menuOptions = [
  { label: '仪表盘', key: 'dashboard', icon: renderIcon(StatsChartOutline) },
  { label: '数据源', key: 'sources', icon: renderIcon(GlobeOutline) },
  { label: '关键词策略', key: 'keywords', icon: renderIcon(KeyOutline) },
  { label: '推送渠道', key: 'channels', icon: renderIcon(SendOutline) },
  { label: '分发规则', key: 'rules', icon: renderIcon(GitBranchOutline) },
  { label: '新闻数据', key: 'news', icon: renderIcon(NewspaperOutline) },
]

const currentRoute = computed(() => route.name as string)

const currentTitle = computed(() => {
  const menu = menuOptions.find(m => m.key === route.name)
  return menu?.label || 'TrendRadar'
})

const handleMenuClick = (key: string) => {
  router.push({ name: key })
}

const handleLogout = () => {
  localStorage.removeItem('token')
  message.success('已登出')
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.logo .icon {
  font-size: 28px;
}

.logo .text {
  font-size: 18px;
  font-weight: 700;
  color: #18a058;
}

.logo.collapsed .text {
  display: none;
}

.sider-footer {
  position: absolute;
  bottom: 16px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
}

.header {
  height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.content {
  padding: 24px;
  background: #101014;
  min-height: calc(100vh - 64px);
}
</style>
