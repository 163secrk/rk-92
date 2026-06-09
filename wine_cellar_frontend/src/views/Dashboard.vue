<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">总览仪表盘</h2>
      <el-button type="primary" @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <div class="stat-card-label">藏品总价值</div>
          <div class="stat-card-value">¥{{ formatNumber(collectionStats.total_value) }}</div>
          <div class="stat-trend positive">
            <el-icon><TrendCharts /></el-icon>
            升值率 {{ collectionStats.appreciation_rate?.toFixed(2) }}%
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <div class="stat-card-label">藏品总数</div>
          <div class="stat-card-value">{{ collectionStats.total_bottles }} 瓶</div>
          <div class="stat-trend">
            总投入 ¥{{ formatNumber(collectionStats.total_cost) }}
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <div class="stat-card-label">进行中贷款</div>
          <div class="stat-card-value">{{ mortgageStats.active_loans }} 笔</div>
          <div class="stat-trend">
            余额 ¥{{ formatNumber(mortgageStats.total_remaining) }}
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
          <div class="stat-card-label">当前告警</div>
          <div class="stat-card-value">{{ alertStats.active }} 条</div>
          <div class="stat-trend" :class="{ 'negative': alertStats.critical > 0 }">
            严重 {{ alertStats.critical }} · 警告 {{ alertStats.warning }}
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="16">
        <el-card class="chart-card card-shadow">
          <template #header>
            <div class="card-header">
              <span>酒窖温湿度监控</span>
              <el-select v-model="selectedCellar" size="small" @change="loadHistory">
                <el-option v-for="c in cellars" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </div>
          </template>
          <div class="chart-container" style="height: 350px;">
            <v-chart :option="tempChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card card-shadow">
          <template #header>
            <span>藏品类型分布</span>
          </template>
          <div class="chart-container" style="height: 350px;">
            <v-chart :option="categoryChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card card-shadow">
          <template #header>
            <span>酒窖状态</span>
          </template>
          <div class="cellar-list">
            <div v-for="cellar in cellars" :key="cellar.id" class="cellar-item">
              <div class="cellar-info">
                <div class="cellar-name">{{ cellar.name }}</div>
                <div class="cellar-location">{{ cellar.location }}</div>
              </div>
              <div class="cellar-stats">
                <div class="temp-display">
                  <el-icon :size="16" :color="getTempColor(cellar)"><Odometer /></el-icon>
                  <span>{{ cellar.current_temp }}°C</span>
                </div>
                <div class="humidity-display">
                  <el-icon :size="16" :color="getHumidityColor(cellar)"><Watermelon /></el-icon>
                  <span>{{ cellar.current_humidity }}%</span>
                </div>
              </div>
              <div :class="['status-tag', `status-${cellar.current_status}`]">
                {{ getStatusText(cellar.current_status) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card card-shadow">
          <template #header>
            <span>高价值藏品 TOP 5</span>
          </template>
          <el-table :data="collectionStats.top_wines" stripe>
            <el-table-column prop="name" label="名称" show-overflow-tooltip />
            <el-table-column prop="vintage" label="年份" width="80" />
            <el-table-column label="当前价值" width="140">
              <template #default="{ row }">
                <span class="price">¥{{ formatNumber(row.current_value) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="升值率" width="100">
              <template #default="{ row }">
                <el-tag :type="row.appreciation_rate >= 0 ? 'success' : 'danger'" size="small">
                  {{ row.appreciation_rate?.toFixed(1) }}%
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="24">
        <el-card class="chart-card card-shadow">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon :size="20" color="#f59e0b" style="margin-right: 8px;"><Warning /></el-icon>
                <span>藏酒到期提醒</span>
                <el-tag type="warning" size="small" style="margin-left: 12px;">
                  即将过期 {{ expiryStats.expiring_soon_count }} 瓶
                </el-tag>
                <el-tag type="danger" size="small" style="margin-left: 8px;">
                  已过期 {{ expiryStats.expired_count }} 瓶
                </el-tag>
              </div>
              <div class="header-right">
                <span style="font-size: 13px; color: #6b7280; margin-right: 8px;">阈值:</span>
                <el-select v-model="expiryThreshold" size="small" style="width: 100px;" @change="loadExpiryAlerts">
                  <el-option :label="1 + ' 年'" :value="1" />
                  <el-option :label="2 + ' 年'" :value="2" />
                  <el-option :label="3 + ' 年'" :value="3" />
                </el-select>
              </div>
            </div>
          </template>
          <div v-if="expiryStats.expired.length > 0" class="expiry-section">
            <div class="section-title expired-title">
              <el-icon :size="16"><CircleClose /></el-icon>
              <span>已过期酒品</span>
            </div>
            <div class="expiry-list">
              <div v-for="wine in expiryStats.expired" :key="'exp-' + wine.id" class="expiry-item expired">
                <div class="wine-basic">
                  <div class="wine-name">{{ wine.name }}</div>
                  <div class="wine-meta">{{ wine.chateau }} · {{ wine.vintage }} · {{ wine.quantity }}瓶</div>
                </div>
                <div class="wine-expiry">
                  <el-tag type="danger" size="small">已过期</el-tag>
                  <span class="expiry-years">超过 {{ Math.abs(wine.years_until_expiry) }} 年</span>
                </div>
                <div class="wine-value">
                  <span class="value-label">适饮期</span>
                  <span class="value-text">{{ wine.drinking_window_start }} - {{ wine.drinking_window_end }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="expiryStats.expiring_soon.length > 0" class="expiry-section">
            <div class="section-title expiring-title">
              <el-icon :size="16"><Clock /></el-icon>
              <span>即将过期酒品</span>
            </div>
            <div class="expiry-list">
              <div v-for="wine in expiryStats.expiring_soon" :key="'soon-' + wine.id" class="expiry-item expiring">
                <div class="wine-basic">
                  <div class="wine-name">{{ wine.name }}</div>
                  <div class="wine-meta">{{ wine.chateau }} · {{ wine.vintage }} · {{ wine.quantity }}瓶</div>
                </div>
                <div class="wine-expiry">
                  <el-tag type="warning" size="small">即将过期</el-tag>
                  <span class="expiry-years">剩余 {{ wine.years_until_expiry }} 年</span>
                </div>
                <div class="wine-value">
                  <span class="value-label">适饮期</span>
                  <span class="value-text">{{ wine.drinking_window_start }} - {{ wine.drinking_window_end }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="expiryStats.expired.length === 0 && expiryStats.expiring_soon.length === 0" class="empty-state">
            <el-icon :size="48" color="#10b981"><CircleCheck /></el-icon>
            <div class="empty-text">所有酒品状态良好，暂无过期风险</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { getCollectionOverview, getExpiryAlerts } from '@/api/collection'
import { getCellars, getCellarHistory, getAlertStats } from '@/api/monitoring'
import { getMortgageStats } from '@/api/mortgage'

const loading = ref(false)
const collectionStats = reactive({
  total_value: 0,
  total_bottles: 0,
  total_cost: 0,
  appreciation_rate: 0,
  top_wines: [],
  by_category: {}
})
const mortgageStats = reactive({
  active_loans: 0,
  total_remaining: 0
})
const alertStats = reactive({
  active: 0,
  warning: 0,
  critical: 0
})
const cellars = ref([])
const selectedCellar = ref(null)
const historyData = ref([])
const expiryStats = reactive({
  expiring_soon_count: 0,
  expired_count: 0,
  expiring_soon: [],
  expired: []
})
const expiryThreshold = ref(1)

const tempChartOption = computed(() => ({
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
    data: historyData.value.map(d => d.timestamp?.split('T')[1]?.slice(0, 5) || '')
  },
  yAxis: [
    {
      type: 'value',
      name: '温度(°C)',
      position: 'left',
      axisLabel: {
        formatter: '{value}°C'
      }
    },
    {
      type: 'value',
      name: '湿度(%)',
      position: 'right',
      axisLabel: {
        formatter: '{value}%'
      }
    }
  ],
  series: [
    {
      name: '温度',
      type: 'line',
      smooth: true,
      yAxisIndex: 0,
      data: historyData.value.map(d => d.temperature),
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0)' }
          ]
        }
      },
      lineStyle: {
        color: '#667eea',
        width: 2
      },
      itemStyle: { color: '#667eea' }
    },
    {
      name: '湿度',
      type: 'line',
      smooth: true,
      yAxisIndex: 1,
      data: historyData.value.map(d => d.humidity),
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(67, 233, 123, 0.3)' },
            { offset: 1, color: 'rgba(67, 233, 123, 0)' }
          ]
        }
      },
      lineStyle: {
        color: '#43e97b',
        width: 2
      },
      itemStyle: { color: '#43e97b' }
    }
  ]
}))

const categoryChartOption = computed(() => {
  const categoryNames = {
    red: '红葡萄酒',
    white: '白葡萄酒',
    rose: '桃红葡萄酒',
    sparkling: '起泡酒',
    dessert: '甜酒',
    fortified: '加强酒'
  }
  const data = Object.entries(collectionStats.by_category || {}).map(([key, value]) => ({
    name: categoryNames[key] || key,
    value: value.count || 0
  }))
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}瓶 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: data,
        color: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#feca57']
      }
    ]
  }
})

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}

function getStatusText(status) {
  const map = { normal: '正常', warning: '警告', critical: '异常', unknown: '未知' }
  return map[status] || status
}

function getTempColor(cellar) {
  if (!cellar.current_temp) return '#6b7280'
  if (cellar.current_temp < (cellar.optimal_temp_min + cellar.optimal_temp_max) / 2) return '#4facfe'
  if (cellar.current_temp > (cellar.optimal_temp_min + cellar.optimal_temp_max) / 2 + 1) return '#f5576c'
  return '#43e97b'
}

function getHumidityColor(cellar) {
  if (!cellar.current_humidity) return '#6b7280'
  if (cellar.current_humidity < (cellar.optimal_humidity_min + cellar.optimal_humidity_max) / 2) return '#feca57'
  return '#43e97b'
}

async function loadCollectionStats() {
  try {
    const data = await getCollectionOverview()
    Object.assign(collectionStats, data)
  } catch (e) {
    console.error(e)
  }
}

async function loadCellars() {
  try {
    const data = await getCellars()
    cellars.value = data.results || data || []
    if (cellars.value.length > 0 && !selectedCellar.value) {
      selectedCellar.value = cellars.value[0].id
      loadHistory()
    }
  } catch (e) {
    console.error(e)
  }
}

async function loadHistory() {
  if (!selectedCellar.value) return
  try {
    const data = await getCellarHistory(selectedCellar.value, 24)
    historyData.value = data.results || data || []
  } catch (e) {
    console.error(e)
  }
}

async function loadAlertStatsData() {
  try {
    const data = await getAlertStats()
    Object.assign(alertStats, data)
  } catch (e) {
    console.error(e)
  }
}

async function loadMortgageStats() {
  try {
    const data = await getMortgageStats()
    Object.assign(mortgageStats, data)
  } catch (e) {
    console.error(e)
  }
}

async function loadExpiryAlerts() {
  try {
    const data = await getExpiryAlerts(expiryThreshold.value)
    Object.assign(expiryStats, data)
  } catch (e) {
    console.error(e)
  }
}

async function refreshData() {
  loading.value = true
  await Promise.all([
    loadCollectionStats(),
    loadCellars(),
    loadAlertStatsData(),
    loadMortgageStats(),
    loadExpiryAlerts()
  ])
  loading.value = false
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  padding: 24px;
  border-radius: 16px;
  color: white;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.stat-card-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.stat-card-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.stat-trend {
  font-size: 13px;
  opacity: 0.85;
  display: flex;
  align-items: center;
  gap: 4px;
  position: relative;
  z-index: 1;
}

.stat-trend.positive {
  color: #a7f3d0;
}

.stat-trend.negative {
  color: #fecaca;
}

.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 12px;
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cellar-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cellar-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.cellar-item:hover {
  background: #f3f4f6;
  transform: translateX(4px);
}

.cellar-info {
  flex: 1;
}

.cellar-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.cellar-location {
  font-size: 13px;
  color: #6b7280;
}

.cellar-stats {
  display: flex;
  gap: 24px;
  margin-right: 20px;
}

.temp-display,
.humidity-display {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: 15px;
}

.price {
  font-weight: 600;
  color: #667eea;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.expiry-section {
  margin-bottom: 24px;
}

.expiry-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}

.expired-title {
  color: #ef4444;
}

.expiring-title {
  color: #f59e0b;
}

.expiry-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.expiry-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 10px;
  border-left: 4px solid transparent;
  transition: all 0.3s ease;
}

.expiry-item:hover {
  background: #f3f4f6;
  transform: translateX(4px);
}

.expiry-item.expired {
  border-left-color: #ef4444;
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.05) 0%, #f9fafb 100%);
}

.expiry-item.expiring {
  border-left-color: #f59e0b;
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.05) 0%, #f9fafb 100%);
}

.wine-basic {
  flex: 1;
}

.wine-basic .wine-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.wine-basic .wine-meta {
  font-size: 13px;
  color: #6b7280;
}

.wine-expiry {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  margin: 0 24px;
  min-width: 100px;
}

.expiry-years {
  font-size: 12px;
  color: #6b7280;
}

.wine-value {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 120px;
}

.value-label {
  font-size: 11px;
  color: #9ca3af;
  margin-bottom: 2px;
}

.value-text {
  font-size: 13px;
  font-weight: 500;
  color: #4b5563;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-text {
  margin-top: 12px;
  font-size: 15px;
  color: #6b7280;
}
</style>
