<template>
  <div class="keywords-page">
    <n-card>
      <template #header>
        <n-space justify="space-between" align="center">
          <span>关键词策略</span>
          <n-button type="primary" @click="showModal = true">+ 添加策略</n-button>
        </n-space>
      </template>

      <n-data-table
        :columns="columns"
        :data="groups"
        :loading="loading"
        :pagination="{ pageSize: 20 }"
      />
    </n-card>

    <!-- 编辑弹窗 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="editId ? '编辑策略' : '添加策略'" style="width: 600px;">
      <n-form :model="formData" label-placement="left" label-width="100">
        <n-form-item label="策略名称">
          <n-input v-model:value="formData.name" placeholder="如：AI相关、股票资讯" />
        </n-form-item>
        <n-form-item label="关键词">
          <n-dynamic-tags v-model:value="formData.keywords" />
          <template #feedback>多个关键词，命中任意一个即匹配</template>
        </n-form-item>
        <n-form-item label="必须包含">
          <n-dynamic-tags v-model:value="formData.must_include" />
          <template #feedback>必须同时包含这些词</template>
        </n-form-item>
        <n-form-item label="排除词">
          <n-dynamic-tags v-model:value="formData.exclude" />
          <template #feedback>包含这些词则过滤掉</template>
        </n-form-item>
        <n-form-item label="优先级">
          <n-input-number v-model:value="formData.priority" :min="0" :max="100" />
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
const groups = ref<any[]>([])
const editId = ref<number | null>(null)

const formData = ref({
  name: '',
  keywords: [] as string[],
  must_include: [] as string[],
  exclude: [] as string[],
  priority: 0,
  enabled: true
})

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name', width: 150 },
  { title: '关键词', key: 'keywords', render: (row: any) => row.keywords?.slice(0, 5).join(', ') + (row.keywords?.length > 5 ? '...' : '') },
  { title: '优先级', key: 'priority', width: 80 },
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
    const res = await request.get('/api/keywords/')
    groups.value = res.data
  } finally {
    loading.value = false
  }
}

const handleEdit = (row: any) => {
  editId.value = row.id
  formData.value = {
    name: row.name,
    keywords: [...(row.keywords || [])],
    must_include: [...(row.must_include || [])],
    exclude: [...(row.exclude || [])],
    priority: row.priority || 0,
    enabled: row.enabled
  }
  showModal.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    if (editId.value) {
      await request.put(`/api/keywords/${editId.value}`, formData.value)
      message.success('保存成功')
    } else {
      await request.post('/api/keywords/', formData.value)
      message.success('添加成功')
    }
    showModal.value = false
    editId.value = null
    formData.value = { name: '', keywords: [], must_include: [], exclude: [], priority: 0, enabled: true }
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
    content: `确定要删除策略 "${row.name}" 吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      await request.delete(`/api/keywords/${row.id}`)
      message.success('删除成功')
      fetchData()
    }
  })
}

onMounted(fetchData)
</script>
