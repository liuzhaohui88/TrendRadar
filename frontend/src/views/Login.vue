<template>
  <div class="login-container">
    <!-- 动态背景 -->
    <div class="bg-animation">
      <div class="star" v-for="i in 50" :key="i" :style="getStarStyle(i)"></div>
    </div>

    <div class="login-content">
      <div class="header">
        <div class="logo-box">
          <span class="icon">📡</span>
        </div>
        <div class="title-group">
          <span class="title">TrendRadar</span>
          <span class="subtitle">Nina Intelligence Center</span>
        </div>
      </div>

      <n-card class="login-card" :bordered="false">
        <div class="card-header">
          <h3>身份验证</h3>
          <p>请输入凭证以访问系统</p>
        </div>

        <n-form ref="formRef" :model="formValue" :rules="rules" size="large">
          <n-form-item path="username" :show-label="false">
            <n-input
              v-model:value="formValue.username"
              placeholder="Username"
              class="custom-input"
            >
              <template #prefix>
                <n-icon :component="PersonOutline" />
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password" :show-label="false">
            <n-input
              v-model:value="formValue.password"
              type="password"
              show-password-on="mousedown"
              placeholder="Password"
              class="custom-input"
              @keydown.enter="handleLogin"
            >
              <template #prefix>
                <n-icon :component="LockClosedOutline" />
              </template>
            </n-input>
          </n-form-item>

          <n-form-item>
            <n-button type="primary" block :loading="loading" @click="handleLogin" class="login-btn">
              LOGIN SYSTEM
            </n-button>
          </n-form-item>
        </n-form>
      </n-card>

      <div class="footer">
        <span>TrendRadar Nina v5.5</span>
        <span class="separator">|</span>
        <span>Secure Connection</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { PersonOutline, LockClosedOutline } from '@vicons/ionicons5'
import request from '../utils/request'

const router = useRouter()
const message = useMessage()
const loading = ref(false)

const formValue = reactive({
  username: '',
  password: ''
})

const rules = {
  username: { required: true, message: '请输入账号', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' }
}

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await request.post('/api/login', formValue)
    const { access_token } = res.data
    localStorage.setItem('token', access_token)
    message.success('Access Granted')
    router.push('/')
  } catch (err: any) {
    message.error(err.response?.data?.detail || 'Access Denied')
  } finally {
    loading.value = false
  }
}

const getStarStyle = (i: number) => ({
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  animationDelay: `${Math.random() * 5}s`,
  opacity: Math.random()
})
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%);
  overflow: hidden;
  position: relative;
}

.bg-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 10px white;
  animation: twinkle 3s infinite ease-in-out;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

.login-content {
  position: relative;
  z-index: 1;
  width: 380px;
}

.header {
  margin-bottom: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.logo-box {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #18a058 0%, #0d5c2e 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  box-shadow: 0 10px 20px rgba(24, 160, 88, 0.3);
  margin-bottom: 16px;
}

.title-group .title {
  display: block;
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 1px;
}

.title-group .subtitle {
  display: block;
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-top: 4px;
}

.login-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  padding: 10px;
}

.card-header {
  text-align: center;
  margin-bottom: 24px;
}

.card-header h3 {
  color: #fff;
  margin: 0 0 8px 0;
  font-size: 18px;
}

.card-header p {
  color: rgba(255,255,255,0.5);
  margin: 0;
  font-size: 13px;
}

.login-btn {
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  border-radius: 8px;
  background: linear-gradient(90deg, #18a058 0%, #0d7a3e 100%);
  border: none;
  margin-top: 10px;
  transition: all 0.3s;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(24, 160, 88, 0.4);
}

.footer {
  margin-top: 30px;
  color: rgba(255,255,255,0.3);
  font-size: 12px;
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style>
