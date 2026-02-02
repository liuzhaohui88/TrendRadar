<template>
  <div class="rules-page">
    <n-card>
      <template #header>
        <n-space justify="space-between" align="center">
          <span>分发规则</span>
          <n-button type="primary" @click="openCreate">+ 添加规则</n-button>
        </n-space>
      </template>

      <n-data-table
        :columns="columns"
        :data="rules"
        :loading="loading"
        :pagination="{ pageSize: 20 }"
      />
    </n-card>

    <!-- 编辑弹窗 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="editId ? '编辑规则' : '添加规则'" style="width: 650px;">
      <n-form :model="formData" label-placement="left" label-width="100">
        <n-form-item label="规则名称">
          <n-input v-model:value="formData.name" placeholder="如：AI热点推飞书" />
        </n-form-item>
        <n-form-item label="数据源">
          <n-select v-model:value="formData.source_ids" multiple :options="sourceOptions" placeholder="选择数据源" />
        </n-form-item>
        <n-form-item label="关键词策略">
          <n-select v-model:value="formData.keyword_group_ids" multiple :options="keywordOptions" placeholder="选择关键词策略" />
        </n-form-item>
        <n-form-item label="推送渠道">
          <n-select v-model:value="formData.channel_ids" multiple :options="channelOptions" placeholder="选择推送渠道" />
        </n-form-item>
        <n-form-item label="报告模式">
          <n-select v-model:value="formData.report_mode" :options="modeOptions" />
        </n-form-item>
        <n-form-item label="执行间隔">
          <n-input-number v-model:value="formData.interval_seconds" :min="60" :step="60">
            <template #suffix>秒</template>
          </n-input-number>
        </n-form-item>
        <n-form-item label="启用">
          <n-switch v-model:value="formData.enabled" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="handleSave" :loading="saving">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NButton, NTag, NSpace, useMessage, useDialog } from 'naive-ui'
import request from '../utils/request'

const message = useMessage()
const dialog = useDialog()
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const rules = ref<any[]>([])
const editId = ref<number | null>(null)

const sourceOptions = ref<any[]>([])
const keywordOptions = ref<any[]>([])
const channelOptions = ref<any[]>([])

const modeOptions = [
  { label: '增量模式 (incremental)', value: 'incremental' },
  { label: '当前榜单 (current)', value: 'current' },
  { label: '当日汇总 (daily)', value: 'daily' },
]

const formData = ref({
  name: '',
  source_ids: [] as number[],
  keyword_group_ids: [] as number[],
  channel_ids: [] as number[],
  report_mode: 'incremental',
  interval_seconds: 600,
  enabled: true
})

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name' },
  { title: '模式', key: 'report_mode', width: 120 },
  { title: '间隔', key: 'interval_seconds', width: 80, render: (row: any) => `${row.interval_seconds}s` },
  { title: '状态', key: 'enabled', width: 80, render: (row: any) => h(NTag, { type: row.enabled ? 'success' : 'default', size: 'small' }, () => row.enabled ? '启用' : '停用') },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    render: (row: any) => h(NSpace, {}, () => [
      h(NButton, { size: 'small', type: 'info', onClick: () => handleTest(row) }, () => '测试'),
      h(NButton, { size: 'small', onClick: () => handleEdit(row) }, () => '编辑'),
      h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row) }, () => '删除'),
    ])
  }
]

const fetchData = async () => {
  loading.value = true
  try {
    const [rulesRes, sourcesRes, keywordsRes, channelsRes] = await Promise.all([
      request.get('/api/rules/'),
      request.get('/api/sources/'),
      request.get('/api/keywords/'),
      request.get('/api/channels/'),
    ])
    rules.value = rulesRes.data
    sourceOptions.value = sourcesRes.data.map((s: any) => ({ label: `${s.name} (${s.type})`, value: s.id }))
    keywordOptions.value = keywordsRes.data.map((k: any) => ({ label: k.name, value: k.id }))
    channelOptions.value = channelsRes.data.map((c: any) => ({ label: `${c.name} (${c.type})`, value: c.id }))
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editId.value = null
  formData.value = { name: '', source_ids: [], keyword_group_ids: [], channel_ids: [], report_mode: 'incremental', interval_seconds: 600, enabled: true }
  showModal.value = true
}

const handleEdit = (row: any) => {
  editId.value = row.id
  formData.value = {
    name: row.name,
    source_ids: [...(row.source_ids || [])],
    keyword_group_ids: [...(row.keyword_group_ids || [])],
    channel_ids: [...(row.channel_ids || [])],
    report_mode: row.report_mode,
    interval_seconds: row.interval_seconds,
    enabled: row.enabled
  }
  showModal.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    if (editId.value) {
      await request.put(`/api/rules/${editId.value}`, formData.value)
      message.success('保存成功')
    } else {
      await request.post('/api/rules/', formData.value)
      message.success('添加成功')
    }
    showModal.value = false
    fetchData()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

const handleTest = async (row: any) => {
  message.loading('测试中...')
  try {
    const res = await request.post(`/api/rules/${row.id}/test`)
    if (res.data.ok) {
      message.success(res.data.msg)
    } else {
      message.error(res.data.msg)
    }
  } catch (e: any) {
    message.error('测试失败')
  }
}

const handleDelete = (row: any) => {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除规则 "${row.name}" 吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      await request.delete(`/api/rules/${row.id}`)
      message.success('删除成功')
      fetchData()
    }
  })
}

onMounted(fetchData)
</script>
