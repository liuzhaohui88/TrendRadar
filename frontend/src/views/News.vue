<template>
  <div class="news-page">
    <n-card>
      <template #header>
        <n-space justify="space-between" align="center">
          <span>新闻数据</span>
          <n-space>
            <n-input v-model:value="keyword" placeholder="搜索标题..." style="width: 200px;" @keydown.enter="fetchData" />
            <n-button @click="fetchData">搜索</n-button>
          </n-space>
        </n-space>
      </template>

      <!-- 统计 -->
      <n-space style="margin-bottom: 16px;">
        <n-tag>总数: {{ newsStats.total || 0 }}</n-tag>
        <n-tag type="success">今日: {{ newsStats.today || 0 }}</n-tag>
      </n-space>

      <n-data-table
        :columns="columns"
        :data="newsList"
        :loading="loading"
        :pagination="{ pageSize: 30 }"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NButton, NTag, NA } from 'naive-ui'
import request from '../utils/request'

const loading = ref(false)
const keyword = ref('')
const newsList = ref<any[]>([])
const newsStats = ref<any>({})

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '平台', key: 'platform_id', width: 100 },
  {
    title: '标题',
    key: 'title',
    render: (row: any) => h(NA, { href: row.url, target: '_blank' }, () => row.title)
  },
  { title: '排名', key: 'highest_rank', width: 70 },
  { title: '命中', key: 'hit_count', width: 60 },
  { title: '首次发现', key: 'first_seen_at', width: 180, render: (row: any) => row.first_seen_at?.slice(0, 19) },
]

const fetchData = async () => {
  loading.value = true
  try {
    const params: any = { limit: 100 }
    if (keyword.value) params.keyword = keyword.value

    const [newsRes, statsRes] = await Promise.all([
      request.get('/api/news/', { params }),
      request.get('/api/news/stats'),
    ])
    newsList.value = newsRes.data.items
    newsStats.value = statsRes.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>
