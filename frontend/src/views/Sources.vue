<template>
  <div class="sources-page">
    <n-card>
      <template #header>
        <n-space justify="space-between" align="center">
          <span>数据源列表</span>
          <n-button type="primary" @click="showModal = true">+ 添加数据源</n-button>
        </n-space>
      </template>

      <n-data-table
        :columns="columns"
        :data="sources"
        :loading="loading"
        :pagination="{ pageSize: 20 }"
      />
    </n-card>

    <!-- 编辑弹窗 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="editId ? '编辑数据源' : '添加数据源'" style="width: 500px;">
      <n-form :model="formData" label-placement="left" label-width="80">
        <n-form-item label="名称">
          <n-input v-model:value="formData.name" placeholder="数据源名称" />
        </n-form-item>
        <n-form-item label="类型">
          <n-select v-model:value="formData.type" :options="typeOptions" />
        </n-form-item>
        <n-form-item label="目标">
          <n-input v-model:value="formData.target" :placeholder="formData.type === 'platform' ? '平台ID (如 weibo)' : 'RSS URL'" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="formData.description" type="textarea" />
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
const sources = ref<any[]>([])
const editId = ref<number | null>(null)

const formData = ref({
  name: '',
  type: 'platform',
  target: '',
  description: '',
  enabled: true
})

const typeOptions = [
  { label: '热榜平台', value: 'platform' },
  { label: 'RSS 订阅', value: 'rss' }
]

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name' },
  { title: '类型', key: 'type', width: 100, render: (row: any) => h(NTag, { type: row.type === 'platform' ? 'info' : 'warning', size: 'small' }, () => row.type) },
  { title: '目标', key: 'target', ellipsis: { tooltip: true } },
  { title: '状态', key: 'enabled', width: 80, render: (row: any) => h(NTag, { type: row.enabled ? 'success' : 'default', size: 'small' }, () => row.enabled ? '启用' : '停用') },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row: any) => h(NSpace, {}, () => [
      h(NButton, { size: 'small', onClick: () => handleEdit(row) }, () => '编辑'),
      h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row) }, () => '删除'),
    ])
  }
]

const fetchData = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/sources/')
    sources.value = res.data
  } finally {
    loading.value = false
  }
}

const handleEdit = (row: any) => {
  editId.value = row.id
  formData.value = { ...row }
  showModal.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    if (editId.value) {
      await request.put(`/api/sources/${editId.value}`, formData.value)
      message.success('保存成功')
    } else {
      await request.post('/api/sources/', formData.value)
      message.success('添加成功')
    }
    showModal.value = false
    editId.value = null
    formData.value = { name: '', type: 'platform', target: '', description: '', enabled: true }
    fetchData()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = (row: any) => {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除数据源 "${row.name}" 吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      await request.delete(`/api/sources/${row.id}`)
      message.success('删除成功')
      fetchData()
    }
  })
}

onMounted(fetchData)
</script>
