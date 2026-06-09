<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-button text @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        酒品详情
      </h2>
      <div class="header-actions">
        <el-button type="primary" @click="valuateWine" :loading="valuating">
          <el-icon><TrendCharts /></el-icon>
          智能估值
        </el-button>
        <el-button @click="editWine">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
      </div>
    </div>

    <div v-if="wine" class="detail-content">
      <el-row :gutter="24">
        <el-col :span="8">
          <el-card class="card-shadow info-card">
            <div class="wine-avatar">
              <el-icon :size="120" color="#d1d5db"><Star /></el-icon>
            </div>
            <h2 class="wine-name">{{ wine.name }}</h2>
            <p class="wine-chateau">{{ wine.chateau }}</p>
            <div class="wine-tags">
              <el-tag size="large">{{ wine.category_display }}</el-tag>
              <el-tag size="large" type="info">{{ wine.vintage }}</el-tag>
              <el-tag size="large" :type="getMaturityType(wine.maturity)">{{ wine.maturity_display }}</el-tag>
              <el-tag size="large" type="success">{{ wine.status_display }}</el-tag>
            </div>
            <div class="price-section">
              <div class="price-item">
                <div class="price-label">当前估值</div>
                <div class="price-value current">¥{{ formatNumber(wine.current_value) }}</div>
              </div>
              <div class="price-item">
                <div class="price-label">购买价格</div>
                <div class="price-value">¥{{ formatNumber(wine.purchase_price) }}</div>
              </div>
              <div class="price-item">
                <div class="price-label">升值率</div>
                <div class="price-value" :class="wine.appreciation_rate >= 0 ? 'positive' : 'negative'">
                  {{ wine.appreciation_rate?.toFixed(2) }}%
                </div>
              </div>
            </div>
            <div class="total-section">
              <div>
                <span>总价值</span>
                <span class="total-value">¥{{ formatNumber(wine.total_value) }}</span>
              </div>
              <div>
                <span>总收益</span>
                <span class="profit-value" :class="wine.total_profit >= 0 ? 'positive' : 'negative'">
                  ¥{{ formatNumber(wine.total_profit) }}
                </span>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-card class="card-shadow">
            <template #header>
              <span>基本信息</span>
            </template>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="产区">
                {{ wine.country }} · {{ wine.region }}
              </el-descriptions-item>
              <el-descriptions-item label="葡萄品种">
                {{ wine.grape_variety }}
              </el-descriptions-item>
              <el-descriptions-item label="酒精度">
                {{ wine.alcohol_content }}%
              </el-descriptions-item>
              <el-descriptions-item label="容量">
                {{ wine.bottle_size }}L
              </el-descriptions-item>
              <el-descriptions-item label="数量">
                {{ wine.quantity }}瓶
              </el-descriptions-item>
              <el-descriptions-item label="酒窖位置">
                {{ wine.cellar_location }}
              </el-descriptions-item>
              <el-descriptions-item label="购买日期">
                {{ wine.purchase_date }}
              </el-descriptions-item>
              <el-descriptions-item label="适饮期">
                {{ wine.drinking_window_start }} - {{ wine.drinking_window_end }}年
              </el-descriptions-item>
              <el-descriptions-item label="估值日期">
                {{ wine.last_valuation_date }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card class="card-shadow notes-card">
            <template #header>
              <span>品鉴笔记</span>
            </template>
            <p>{{ wine.tasting_notes || '暂无品鉴笔记' }}</p>
          </el-card>

          <el-card class="card-shadow notes-card">
            <template #header>
              <span>存储笔记</span>
            </template>
            <p>{{ wine.storage_notes || '暂无存储笔记' }}</p>
          </el-card>

          <el-card class="card-shadow">
            <template #header>
              <div class="card-header">
                <span>估值历史</span>
                <el-button type="primary" size="small" @click="valuateWine" :loading="valuating">
                  重新估值
                </el-button>
              </div>
            </template>
            <div style="height: 300px;">
              <v-chart :option="valuationChartOption" autoresize />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getWine, valuateWine as apiValuateWine, getWineValuationHistory } from '@/api/collection'

const route = useRoute()
const router = useRouter()

const wine = ref(null)
const valuationHistory = ref([])
const valuating = ref(false)

const valuationChartOption = computed(() => {
  const data = [...valuationHistory.value].reverse()
  return {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>估值: ¥{c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.valuation_date)
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [{
      type: 'line',
      smooth: true,
      data: data.map(d => d.value),
      itemStyle: { color: '#667eea' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0)' }
          ]
        }
      }
    }]
  }
})

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}

function getMaturityType(maturity) {
  const map = {
    cellared: 'info',
    drinking: 'success',
    peak: 'danger',
    declining: 'warning'
  }
  return map[maturity] || ''
}

function editWine() {
  ElMessage.info('编辑功能开发中')
}

async function valuateWine() {
  if (!wine.value) return
  valuating.value = true
  try {
    await apiValuateWine(wine.value.id)
    ElMessage.success('估值完成')
    await loadWine()
    await loadValuationHistory()
  } catch (e) {
    console.error(e)
  } finally {
    valuating.value = false
  }
}

async function loadWine() {
  try {
    wine.value = await getWine(route.params.id)
  } catch (e) {
    console.error(e)
  }
}

async function loadValuationHistory() {
  try {
    valuationHistory.value = await getWineValuationHistory(route.params.id)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadWine()
  loadValuationHistory()
})
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 12px;
}

.info-card {
  text-align: center;
}

.wine-avatar {
  padding: 40px 0;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  margin-bottom: 20px;
}

.wine-name {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.wine-chateau {
  font-size: 15px;
  color: #6b7280;
  margin: 0 0 16px 0;
}

.wine-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.price-section {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
  border-top: 1px solid #f3f4f6;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 20px;
}

.price-item {
  text-align: center;
}

.price-label {
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 6px;
}

.price-value {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.price-value.current {
  color: #667eea;
  font-size: 22px;
}

.price-value.positive {
  color: #22c55e;
}

.price-value.negative {
  color: #ef4444;
}

.total-section {
  display: flex;
  justify-content: space-around;
}

.total-section > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: #6b7280;
}

.total-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.profit-value.positive {
  font-size: 20px;
  font-weight: 700;
  color: #22c55e;
}

.profit-value.negative {
  font-size: 20px;
  font-weight: 700;
  color: #ef4444;
}

.notes-card {
  margin-top: 24px;
}

.notes-card :deep(.el-descriptions) {
  margin-bottom: 0;
}

.notes-card p {
  line-height: 1.8;
  color: #4b5563;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
