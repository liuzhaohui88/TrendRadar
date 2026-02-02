<template>
  <div class="dashboard">
    <n-grid :cols="4" :x-gap="16" :y-gap="16">
      <!-- 统计卡片 -->
      <n-gi>
        <n-card class="stat-card">
          <n-statistic label="数据源" :value="stats.sources?.total || 0">
            <template #suffix>
              <span class="enabled">/ {{ stats.sources?.enabled || 0 }} 启用</span>
            </template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card class="stat-card">
          <n-statistic label="关键词策略" :value="stats.keywords?.total || 0" />
        </n-card>
      </n-gi>
      <n-gi>
        <n-card class="stat-card">
          <n-statistic label="推送渠道" :value="stats.channels?.total || 0" />
        </n-card>
      </n-gi>
      <n-gi>
        <n-card class="stat-card">
          <n-statistic label="分发规则" :value="stats.rules?.total || 0">
            <template #suffix>
              <span class="enabled">/ {{ stats.rules?.enabled || 0 }} 启用</span>
            </template>
          </n-statistic>
        </n-card>
      </n-gi>
    </n-grid>

    <n-grid :cols="2" :x-gap="16" :y-gap="16" style="margin-top: 16px;">
      <!-- 今日推送 -->
      <n-gi>
        <n-card title="📤 今日推送">
          <n-statistic label="推送次数" :value="stats.push_today?.total || 0">
            <template #suffix>
              <n-tag type="success" size="small" style="margin-left: 8px;">
                成功 {{ stats.push_today?.success || 0 }}
              </n-tag>
            </template>
          </n-statistic>
        </n-card>
      </n-gi>

      <!-- 规则概览 -->
      <n-gi>
        <n-card title="📋 规则概览">
          <n-data-table
            :columns="ruleColumns"
            :data="rulesSummary"
            :pagination="false"
            size="small"
            :max-height="200"
          />
        </n-card>
      </n-gi>
    </n-grid>

    <!-- 最近日志 -->
    <n-card title="📝 最近推送日志" style="margin-top: 16px;">
      <n-data-table
        :columns="logColumns"
        :data="recentLogs"
        :pagination="false"
        size="small"
        :max-height="300"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NTag } from 'naive-ui'
import request from '../utils/request'

const stats = ref<any>({})
const rulesSummary = ref<any[]>([])
const recentLogs = ref<any[]>([])

const ruleColumns = [
  { title: '规则', key: 'name', width: 150 },
  {
    title: '状态',
    key: 'enabled',
    width: 80,
    render: (row: any) => h(NTag, { type: row.enabled ? 'success' : 'default', size: 'small' }, () => row.enabled ? '启用' : '停用')
  },
  { title: '模式', key: 'report_mode', width: 100 },
  { title: '渠道', key: 'channels', render: (row: any) => row.channels?.join(', ') || '-' },
]

const logColumns = [
  { title: '时间', key: 'created_at', width: 180, render: (row: any) => row.created_at?.slice(0, 19) },
  { title: '渠道', key: 'channel_name', width: 120 },
  {
    title: '状态',
    key: 'status',
    width: 80,
    render: (row: any) => h(NTag, { type: row.status === 'success' ? 'success' : 'error', size: 'small' }, () => row.status)
  },
  { title: '消息', key: 'message' },
]

const fetchData = async () => {
  try {
    const [statsRes, rulesRes, logsRes] = await Promise.all([
      request.get('/api/dashboard/stats'),
      request.get('/api/dashboard/rules-summary'),
      request.get('/api/dashboard/recent-logs'),
    ])
    stats.value = statsRes.data
    rulesSummary.value = rulesRes.data
    recentLogs.value = logsRes.data
  } catch (e) {
    console.error('Failed to fetch dashboard data', e)
  }
}

onMounted(fetchData)
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.stat-card {
  text-align: center;
}

.enabled {
  font-size: 14px;
  color: #18a058;
}
</style>
