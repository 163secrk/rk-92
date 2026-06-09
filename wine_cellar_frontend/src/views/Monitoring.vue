<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">恒温监控</h2>
      <div class="header-actions">
        <el-button type="primary" @click="simulateReading">
          <el-icon><Cpu /></el-icon>
          模拟传感器读数
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="monitoring-header">
      <el-col :span="8" v-for="cellar in cellars" :key="cellar.id">
        <el-card class="cellar-card card-shadow" :class="`status-${cellar.current_status}`" @click="selectCellar(cellar)">
          <div class="cellar-card-header">
            <div>
              <h3 class="cellar-name">{{ cellar.name }}</h3>
              <p class="cellar-location">{{ cellar.location }}</p>
            </div>
            <el-badge :value="cellar.alert_count" class="item" :type="cellar.alert_count > 0 ? 'danger' : 'info'">
              <div :class="['status-badge', `status-${cellar.current_status}`]">
                {{ getStatusText(cellar.current_status) }}
              </div>
            </el-badge>
          </div>
          <div class="cellar-readings">
            <div class="reading-item">
              <div class="reading-label">温度</div>
              <div class="reading-value temp">
                <el-icon :size="20"><Odometer /></el-icon>
                {{ cellar.current_temp }}°C
              </div>
              <div class="reading-range">{{ cellar.optimal_temp_min }} - {{ cellar.optimal_temp_max }}°C</div>
            </div>
            <div class="reading-item">
              <div class="reading-label">湿度</div>
              <div class="reading-value humidity">
                <el-icon :size="20"><Watermelon /></el-icon>
                {{ cellar.current_humidity }}%
              </div>
              <div class="reading-range">{{ cellar.optimal_humidity_min }} - {{ cellar.optimal_humidity_max }}%</div>
            </div>
          </div>
          <div class="gauge-row">
            <div class="gauge-container">
              <v-chart :option="getTempGaugeOption(cellar)" autoresize />
            </div>
            <div class="gauge-container">
              <v-chart :option="getHumidityGaugeOption(cellar)" autoresize />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" v-if="selectedCellar">
      <el-col :span="16">
        <el-card class="card-shadow">
          <template #header>
            <div class="card-header">
              <span>{{ selectedCellar.name }} - 温湿度趋势</span>
              <el-radio-group v-model="historyRange" size="small" @change="loadHistory">
                <el-radio-button :value="6">6小时</el-radio-button>
                <el-radio-button :value="24">24小时</el-radio-button>
                <el-radio-button :value="72">3天</el-radio-button>
                <el-radio-button :value="168">7天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div style="height: 400px;">
            <v-chart :option="historyChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="card-shadow">
          <template #header>
            <span>告警记录</span>
          </template>
          <div class="alert-list">
            <div v-if="alerts.length === 0" class="empty-state">
              <el-icon :size="48" color="#d1d5db"><CircleCheck /></el-icon>
              <p>暂无告警记录</p>
            </div>
            <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="`severity-${alert.severity}`">
              <div class="alert-icon">
                <el-icon v-if="alert.severity === 'critical'" :size="24" color="#dc2626"><Warning /></el-icon>
                <el-icon v-else :size="24" color="#f59e0b"><InfoFilled /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.alert_type_display }}</div>
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-time">{{ formatTime(alert.created_at) }}</div>
              </div>
              <div class="alert-actions">
                <el-tag v-if="alert.status === 'active'" type="danger" size="small">未处理</el-tag>
                <el-tag v-else-if="alert.status === 'acknowledged'" type="warning" size="small">已确认</el-tag>
                <el-tag v-else type="success" size="small">已解决</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { getCellars, getCellarHistory, getAlerts, simulateReading as apiSimulateReading } from '@/api/monitoring'

const cellars = ref([])
const selectedCellar = ref(null)
const historyData = ref([])
const alerts = ref([])
const historyRange = ref(24)

const historyChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['温度', '湿度'],
    top: 0
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: historyData.value.map(d => dayjs(d.timestamp).format('MM-DD HH:mm'))
  },
  yAxis: [
    {
      type: 'value',
      name: '温度(°C)',
      position: 'left'
    },
    {
      type: 'value',
      name: '湿度(%)',
      position: 'right'
    }
  ],
  series: [
    {
      name: '温度',
      type: 'line',
      smooth: true,
      yAxisIndex: 0,
      data: historyData.value.map(d => d.temperature),
      itemStyle: { color: '#ef4444' },
      areaStyle: { color: 'rgba(239, 68, 68, 0.1)' }
    },
    {
      name: '湿度',
      type: 'line',
      smooth: true,
      yAxisIndex: 1,
      data: historyData.value.map(d => d.humidity),
      itemStyle: { color: '#3b82f6' },
      areaStyle: { color: 'rgba(59, 130, 246, 0.1)' }
    }
  ]
}))

function getTempGaugeOption(cellar) {
  return {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 30,
      radius: '100%',
      center: ['50%', '75%'],
      axisLine: {
        lineStyle: {
          width: 12,
          color: [
            [0.3, '#ef4444'],
            [0.5, '#f59e0b'],
            [0.7, '#22c55e'],
            [0.9, '#f59e0b'],
            [1, '#ef4444']
          ]
        }
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '60%',
        width: 8,
        offsetCenter: [0, '-10%'],
        itemStyle: { color: '#ef4444' }
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      title: { show: false },
      detail: {
        fontSize: 20,
        fontWeight: 'bold',
        offsetCenter: [0, '-10%'],
        valueAnimation: true,
        formatter: '{value}°C',
        color: '#1f2937'
      },
      data: [{ value: cellar.current_temp || 0 }]
    }]
  }
}

function getHumidityGaugeOption(cellar) {
  return {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      radius: '100%',
      center: ['50%', '75%'],
      axisLine: {
        lineStyle: {
          width: 12,
          color: [
            [0.4, '#f59e0b'],
            [0.8, '#22c55e'],
            [1, '#f59e0b']
          ]
        }
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '60%',
        width: 8,
        offsetCenter: [0, '-10%'],
        itemStyle: { color: '#3b82f6' }
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      title: { show: false },
      detail: {
        fontSize: 20,
        fontWeight: 'bold',
        offsetCenter: [0, '-10%'],
        valueAnimation: true,
        formatter: '{value}%',
        color: '#1f2937'
      },
      data: [{ value: cellar.current_humidity || 0 }]
    }]
  }
}

function getStatusText(status) {
  const map = { normal: '运行正常', warning: '注意警告', critical: '异常告警', unknown: '未知' }
  return map[status] || status
}

function formatTime(time) {
  return dayjs(time).format('MM-DD HH:mm:ss')
}

function selectCellar(cellar) {
  selectedCellar.value = cellar
  loadHistory()
  loadAlerts()
}

async function loadCellars() {
  try {
    const data = await getCellars()
    cellars.value = data.results || data || []
    if (cellars.value.length > 0 && !selectedCellar.value) {
      selectCellar(cellars.value[0])
    }
  } catch (e) {
    console.error(e)
  }
}

async function loadHistory() {
  if (!selectedCellar.value) return
  try {
    const data = await getCellarHistory(selectedCellar.value.id, historyRange.value)
    historyData.value = data.results || data || []
  } catch (e) {
    console.error(e)
  }
}

async function loadAlerts() {
  if (!selectedCellar.value) return
  try {
    const data = await getAlerts({ cellar: selectedCellar.value.id })
    alerts.value = data.results || data || []
  } catch (e) {
    console.error(e)
  }
}

async function simulateReading() {
  if (!selectedCellar.value) {
    ElMessage.warning('请先选择一个酒窖')
    return
  }
  try {
    await apiSimulateReading(selectedCellar.value.id)
    ElMessage.success('已模拟传感器读数')
    refreshData()
  } catch (e) {
    console.error(e)
  }
}

async function refreshData() {
  await loadCellars()
  if (selectedCellar.value) {
    loadHistory()
    loadAlerts()
  }
}

onMounted(() => {
  loadCellars()
})
</script>

<style scoped>
.monitoring-header {
  margin-bottom: 24px;
}

.cellar-card {
  border-radius: 16px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cellar-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 32px -8px rgba(0, 0, 0, 0.15);
}

.cellar-card.status-normal {
  border-color: #22c55e;
}

.cellar-card.status-warning {
  border-color: #f59e0b;
}

.cellar-card.status-critical {
  border-color: #ef4444;
}

.cellar-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.cellar-name {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.cellar-location {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.status-normal {
  background: #dcfce7;
  color: #166534;
}

.status-badge.status-warning {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.status-critical {
  background: #fee2e2;
  color: #991b1b;
}

.cellar-readings {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.reading-item {
  text-align: center;
}

.reading-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}

.reading-value {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.reading-value.temp {
  color: #ef4444;
}

.reading-value.humidity {
  color: #3b82f6;
}

.reading-range {
  font-size: 12px;
  color: #9ca3af;
}

.gauge-row {
  display: flex;
  gap: 16px;
}

.gauge-container {
  flex: 1;
  height: 120px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.alert-list {
  max-height: 400px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f9fafb;
  border-left: 4px solid #d1d5db;
}

.alert-item.severity-critical {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.alert-item.severity-warning {
  background: #fefce8;
  border-left-color: #f59e0b;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.alert-message {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}

.alert-time {
  font-size: 12px;
  color: #9ca3af;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #9ca3af;
}

.empty-state p {
  margin-top: 12px;
}
</style>
