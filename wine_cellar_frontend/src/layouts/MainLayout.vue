<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <el-icon :size="32" color="#667eea"><Star /></el-icon>
        <span class="logo-text">臻品酒窖</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="transparent"
        text-color="#6b7280"
        active-text-color="#667eea"
        class="menu"
      >
        <template v-if="userStore.isAdmin">
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>总览仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/monitoring">
            <el-icon><Monitor /></el-icon>
            <span>恒温监控</span>
          </el-menu-item>
          <el-menu-item index="/collection">
            <el-icon><Goods /></el-icon>
            <span>藏品估值</span>
          </el-menu-item>
          <el-menu-item index="/tasting">
            <el-icon><WineGlass /></el-icon>
            <span>品鉴活动</span>
          </el-menu-item>
          <el-menu-item index="/mortgage">
            <el-icon><Money /></el-icon>
            <span>名酒抵押</span>
          </el-menu-item>
          <el-menu-item index="/sales">
            <el-icon><ShoppingCart /></el-icon>
            <span>销售管理</span>
          </el-menu-item>
        </template>
        <template v-else>
          <el-menu-item index="/sales">
            <el-icon><ShoppingCart /></el-icon>
            <span>我的订单</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-badge :value="alertCount" class="alert-badge" v-if="alertCount > 0 && userStore.isAdmin">
            <el-button type="primary" text @click="showAlerts">
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">{{ displayName }}</span>
              <el-tag v-if="userStore.isCustomer" size="small" type="success" style="margin-left: 4px;">
                客户
              </el-tag>
              <el-icon><CaretBottom /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <el-drawer v-model="alertDrawerVisible" title="告警通知" size="400px">
      <el-table :data="activeAlerts" stripe>
        <el-table-column prop="alert_type_display" label="类型" width="100" />
        <el-table-column prop="severity_display" label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'critical' ? 'danger' : 'warning'">
              {{ row.severity_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cellar_name" label="酒窖" />
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="acknowledge(row.id)">确认</el-button>
            <el-button size="small" type="success" link @click="resolve(row.id)">解决</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getActiveAlerts, getAlertStats, acknowledgeAlert, resolveAlert } from '@/api/monitoring'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const alertDrawerVisible = ref(false)
const alertCount = ref(0)
const activeAlerts = ref([])

const displayName = computed(() => {
  if (userStore.isCustomer && userStore.userInfo.name) {
    return userStore.userInfo.name
  }
  return userStore.userInfo.username || '用户'
})

const adminPageTitleMap = {
  '/dashboard': '总览仪表盘',
  '/monitoring': '恒温监控',
  '/collection': '藏品估值',
  '/tasting': '品鉴活动',
  '/mortgage': '名酒抵押',
  '/sales': '销售管理'
}

const customerPageTitleMap = {
  '/sales': '我的订单'
}

const currentPageTitle = computed(() => {
  const path = route.path.split('/').slice(0, 2).join('/')
  if (userStore.isAdmin) {
    return adminPageTitleMap[path] || '未知页面'
  }
  return customerPageTitleMap[path] || '未知页面'
})

async function loadAlertStats() {
  try {
    const stats = await getAlertStats()
    alertCount.value = stats.active
  } catch (e) {
    console.error(e)
  }
}

async function showAlerts() {
  alertDrawerVisible.value = true
  try {
    activeAlerts.value = await getActiveAlerts()
  } catch (e) {
    console.error(e)
  }
}

async function acknowledge(id) {
  try {
    await acknowledgeAlert(id)
    ElMessage.success('已确认告警')
    showAlerts()
    loadAlertStats()
  } catch (e) {
    console.error(e)
  }
}

async function resolve(id) {
  try {
    await resolveAlert(id)
    ElMessage.success('已解决告警')
    showAlerts()
    loadAlertStats()
  } catch (e) {
    console.error(e)
  }
}

function handleCommand(command) {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    }).catch(() => {})
  }
}

onMounted(() => {
  loadAlertStats()
  setInterval(loadAlertStats, 30000)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
  border-right: none;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
}

.menu {
  border-right: none;
  margin-top: 16px;
}

.menu :deep(.el-menu-item) {
  height: 52px;
  line-height: 52px;
  margin: 4px 12px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
}

.menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.menu :deep(.el-icon) {
  margin-right: 12px;
  font-size: 18px;
}

.header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.username {
  font-weight: 500;
  color: #374151;
}

.main-content {
  background-color: #f5f7fa;
  padding: 0;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.alert-badge {
  margin-right: 8px;
}
</style>
