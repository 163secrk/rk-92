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

      <el-tabs v-model="activeTab" class="login-tabs" @tab-change="handleTabChange">
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>

      <div v-show="activeTab === 'login'">
        <el-tabs v-model="loginType" class="login-type-tabs">
          <el-tab-pane label="管理员登录" name="admin" />
          <el-tab-pane label="客户登录" name="customer" />
        </el-tabs>

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
              :placeholder="loginType === 'admin' ? '请输入用户名' : '请输入手机号'"
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

        <div v-if="loginType === 'admin'" class="login-footer">
          <p>默认账号: admin / admin123</p>
        </div>
      </div>

      <div v-show="activeTab === 'register'">
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="login-form"
          @keyup.enter="handleRegister"
        >
          <el-form-item prop="name">
            <el-input
              v-model="registerForm.name"
              placeholder="请输入姓名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="phone">
            <el-input
              v-model="registerForm.phone"
              placeholder="请输入手机号"
              size="large"
              :prefix-icon="Phone"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请确认密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="registerForm.gender">
              <el-radio value="male">男</el-radio>
              <el-radio value="female">女</el-radio>
              <el-radio value="other">其他</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="registerLoading"
              @click="handleRegister"
            >
              注 册
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Star, Phone } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loginType = ref('admin')

const loginFormRef = ref()
const registerFormRef = ref()
const loading = ref(false)
const registerLoading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  name: '',
  phone: '',
  password: '',
  confirmPassword: '',
  gender: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const loginRules = computed(() => ({
  username: [{ required: true, message: loginType.value === 'admin' ? '请输入用户名' : '请输入手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}))

const registerRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

function handleTabChange() {
  loginForm.username = ''
  loginForm.password = ''
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
    ElMessage.error(e.response?.data?.detail || '登录失败，请检查账号密码')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!registerFormRef.value) return
  try {
    await registerFormRef.value.validate()
    registerLoading.value = true
    const data = {
      name: registerForm.name,
      phone: registerForm.phone,
      password: registerForm.password,
      gender: registerForm.gender
    }
    await userStore.register(data)
    ElMessage.success('注册成功')
    router.push('/dashboard')
  } catch (e) {
    console.error(e)
    ElMessage.error(e.response?.data?.error || '注册失败')
  } finally {
    registerLoading.value = false
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
  width: 460px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.logo-icon {
  width: 70px;
  height: 70px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px -5px rgba(102, 126, 234, 0.5);
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 6px;
}

.subtitle {
  font-size: 13px;
  color: #6b7280;
}

.login-tabs {
  margin-bottom: 16px;
}

.login-type-tabs {
  margin-bottom: 16px;
}

.login-form {
  margin-bottom: 16px;
}

.login-btn {
  width: 100%;
  height: 44px;
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
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.login-footer p {
  color: #9ca3af;
  font-size: 12px;
}
</style>
