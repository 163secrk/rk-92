<template>
  <div class="login-container">
    <div class="login-bg"></div>
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="48" color="#667eea"><Star /></el-icon>
        </div>
        <h1 class="title">臻品酒窖管理系统</h1>
        <p class="subtitle">高端私人酒窖 · 智能恒温监控 · 专业藏品估值</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>默认账号: admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Star } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: 'admin',
  password: 'admin123'
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  if (!loginFormRef.value) return
  try {
    await loginFormRef.value.validate()
    loading.value = true
    await userStore.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%);
}

.login-bg::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 50%);
  animation: rotate 30s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.login-card {
  position: relative;
  z-index: 1;
  width: 420px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px -5px rgba(102, 126, 234, 0.5);
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
}

.login-form {
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  margin-top: 8px;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(102, 126, 234, 0.5);
}

.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.login-footer p {
  color: #9ca3af;
  font-size: 13px;
}
</style>
