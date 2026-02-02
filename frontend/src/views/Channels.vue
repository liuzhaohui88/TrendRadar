<template>
  <div class="channels-page">
    <n-card>
      <template #header>
        <n-space justify="space-between" align="center">
          <span>推送渠道</span>
          <n-button type="primary" @click="openCreate">+ 添加渠道</n-button>
        </n-space>
      </template>

      <n-data-table
        :columns="columns"
        :data="channels"
        :loading="loading"
        :pagination="{ pageSize: 20 }"
      />
    </n-card>

    <!-- 编辑弹窗 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="editId ? '编辑渠道' : '添加渠道'" style="width: 550px;">
      <n-form :model="formData" label-placement="left" label-width="100">
        <n-form-item label="渠道名称">
          <n-input v-model:value="formData.name" placeholder="如：飞书-产品群" />
        </n-form-item>
        <n-form-item label="渠道类型">
          <n-select v-model:value="formData.type" :options="typeOptions" @update:value="handleTypeChange" />
        </n-form-item>

        <!-- 根据类型动态显示配置字段 -->
        <template v-if="formData.type === 'feishu' || formData.type === 'dingtalk' || formData.type === 'wework' || formData.type === 'slack'">
          <n-form-item label="Webhook URL">
            <n-input v-model:value="formData.config.webhook_url" placeholder="https://..." />
          </n-form-item>
        </template>

        <template v-if="formData.type === 'telegram'">
          <n-form-item label="Bot Token">
            <n-input v-model:value="formData.config.bot_token" placeholder="123456:ABC..." />
          </n-form-item>
          <n-form-item label="Chat ID">
            <n-input v-model:value="formData.config.chat_id" placeholder="-100123456789" />
          </n-form-item>
        </template>

        <template v-if="formData.type === 'n8n'">
          <n-form-item label="Webhook URL">
            <n-input v-model:value="formData.config.webhook_url" placeholder="n8n webhook URL" />
          </n-form-item>
        </template>

        <template v-if="formData.type === 'dify'">
          <n-form-item label="API URL">
            <n-input v-model:value="formData.config.api_url" placeholder="Dify API URL" />
          </n-form-item>
          <n-form-item label="API Key">
            <n-input v-model:value="formData.config.api_key" placeholder="app-xxx" type="password" show-password-on="click" />
          </n-form-item>
        </template>

        <template v-if="formData.type === 'bark'">
          <n-form-item label="Bark URL">
            <n-input v-model:value="formData.config.url" placeholder="https://api.day.app/your_key" />
          </n-form-item>
        </template>

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
const channels = ref<any[]>([])
const editId = ref<number | null>(null)

const formData = ref({
  name: '',
  type: 'feishu',
  config: {} as Record<string, any>,
  enabled: true
})

const typeOptions = [
  { label: '飞书', value: 'feishu' },
  { label: '钉钉', value: 'dingtalk' },
  { label: '企业微信', value: 'wework' },
  { label: 'Telegram', value: 'telegram' },
  { label: 'n8n', value: 'n8n' },
  { label: 'Dify', value: 'dify' },
  { label: 'Bark', value: 'bark' },
  { label: 'Slack', value: 'slack' },
  { label: '通用 Webhook', value: 'generic' },
]

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name' },
  { title: '类型', key: 'type', width: 100, render: (row: any) => h(NTag, { size: 'small' }, () => typeOptions.find(t => t.value === row.type)?.label || row.type) },
  { title: '状态', key: 'enabled', width: 80, render: (row: any) => h(NTag, { type: row.enabled ? 'success' : 'default', size: 'small' }, () => row.enabled ? '启用' : '停用') },
  {
    title: '操作',
    key: 'actions',
    width: 200,
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
    const res = await request.get('/api/channels/')
    channels.value = res.data
  } finally {
    loading.value = false
  }
}

const handleTypeChange = () => {
  formData.value.config = {}
}

const openCreate = () => {
  editId.value = null
  formData.value = { name: '', type: 'feishu', config: {}, enabled: true }
  showModal.value = true
}

const handleEdit = (row: any) => {
  editId.value = row.id
  formData.value = {
    name: row.name,
    type: row.type,
    config: { ...row.config },
    enabled: row.enabled
  }
  showModal.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    if (editId.value) {
      await request.put(`/api/channels/${editId.value}`, formData.value)
      message.success('保存成功')
    } else {
      await request.post('/api/channels/', formData.value)
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
    const res = await request.post(`/api/channels/${row.id}/test`)
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
    content: `确定要删除渠道 "${row.name}" 吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      await request.delete(`/api/channels/${row.id}`)
      message.success('删除成功')
      fetchData()
    }
  })
}

onMounted(fetchData)
</script>
