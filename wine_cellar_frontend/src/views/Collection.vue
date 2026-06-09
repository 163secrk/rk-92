<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">藏品估值</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索酒品名称、酒庄..."
          style="width: 300px;"
          clearable
          @keyup.enter="handleSearch"
          @clear="loadWines"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterCategory" placeholder="类型" clearable style="width: 140px;" @change="loadWines">
          <el-option v-for="cat in categories" :key="cat.value" :label="cat.label" :value="cat.value" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 140px;" @change="loadWines">
          <el-option v-for="st in statusOptions" :key="st.value" :label="st.label" :value="st.value" />
        </el-select>
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加酒品
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="stats-summary">
      <el-col :span="6">
        <div class="summary-card">
          <div class="summary-label">总藏品价值</div>
          <div class="summary-value primary">¥{{ formatNumber(stats.total_value) }}</div>
          <div class="summary-change positive">+{{ stats.appreciation_rate?.toFixed(2) }}% 总升值</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="summary-card">
          <div class="summary-label">总投入成本</div>
          <div class="summary-value">¥{{ formatNumber(stats.total_cost) }}</div>
          <div class="summary-change">累计 {{ formatNumber(stats.total_profit) }} 元收益</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="summary-card">
          <div class="summary-label">藏品总数</div>
          <div class="summary-value">{{ stats.total_bottles }} 瓶</div>
          <div class="summary-change">{{ wines?.length || 0 }} 个品种</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="summary-card">
          <div class="summary-label">巅峰期酒品</div>
          <div class="summary-value success">{{ maturityStats.peak || 0 }} 瓶</div>
          <div class="summary-change">适饮期 {{ maturityStats.drinking || 0 }} 瓶</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="wine-grid">
      <el-col :span="6" v-for="wine in wines" :key="wine.id">
        <el-card class="wine-card card-shadow" @click="viewDetail(wine.id)">
          <div class="wine-header">
            <div class="wine-category">
              <el-tag size="small" :type="getCategoryType(wine.category)">{{ wine.category_display }}</el-tag>
            </div>
            <div class="wine-maturity">
              <el-tag size="small" :type="getMaturityType(wine.maturity)">{{ wine.maturity_display }}</el-tag>
            </div>
          </div>
          <div class="wine-image">
            <el-icon :size="64" color="#d1d5db"><Star /></el-icon>
          </div>
          <div class="wine-info">
            <h3 class="wine-name">{{ wine.name }}</h3>
            <p class="wine-chateau">{{ wine.chateau }}</p>
            <p class="wine-region">{{ wine.country }} · {{ wine.region }} · {{ wine.vintage }}</p>
          </div>
          <div class="wine-prices">
            <div class="price-item">
              <div class="price-label">当前估值</div>
              <div class="price-value current">¥{{ formatNumber(wine.current_value) }}</div>
            </div>
            <div class="price-item">
              <div class="price-label">升值率</div>
              <div class="price-value" :class="wine.appreciation_rate >= 0 ? 'positive' : 'negative'">
                {{ wine.appreciation_rate?.toFixed(1) }}%
              </div>
            </div>
            <div class="price-item">
              <div class="price-label">数量</div>
              <div class="price-value">{{ wine.quantity }}瓶</div>
            </div>
          </div>
          <div class="wine-total">
            <span>总价值</span>
            <span class="total-value">¥{{ formatNumber(wine.total_value) }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-pagination
      v-if="pagination.total > 0"
      class="pagination"
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :page-sizes="[12, 24, 48]"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="loadWines"
      @current-change="loadWines"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getWines, searchWines as apiSearchWines, getCollectionOverview, getMaturityDistribution } from '@/api/collection'

const router = useRouter()

const wines = ref([])
const stats = reactive({
  total_value: 0,
  total_cost: 0,
  total_profit: 0,
  total_bottles: 0,
  appreciation_rate: 0
})
const maturityStats = reactive({})
const searchKeyword = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const pagination = reactive({
  page: 1,
  pageSize: 12,
  total: 0
})

const categories = [
  { value: 'red', label: '红葡萄酒' },
  { value: 'white', label: '白葡萄酒' },
  { value: 'rose', label: '桃红葡萄酒' },
  { value: 'sparkling', label: '起泡酒' },
  { value: 'dessert', label: '甜酒' },
  { value: 'fortified', label: '加强酒' },
]

const statusOptions = [
  { value: 'cellared', label: '窖藏中' },
  { value: 'drinking', label: '适饮期' },
  { value: 'peak', label: '巅峰期' },
  { value: 'declining', label: '衰退期' },
  { value: 'mortgaged', label: '已抵押' },
]

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}

function getCategoryType(category) {
  const map = {
    red: 'danger',
    white: 'success',
    rose: 'warning',
    sparkling: 'info',
    dessert: '',
    fortified: 'danger'
  }
  return map[category] || ''
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

function viewDetail(id) {
  router.push(`/collection/${id}`)
}

function showAddDialog() {
  router.push('/collection/new')
}

async function loadWines() {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filterCategory.value) params.category = filterCategory.value
    if (filterStatus.value) params.status = filterStatus.value

    const data = await getWines(params)
    wines.value = data.results || data
    pagination.total = data.count || data.length
  } catch (e) {
    console.error(e)
  }
}

async function handleSearch() {
  if (!searchKeyword.value) {
    loadWines()
    return
  }
  try {
    wines.value = await apiSearchWines(searchKeyword.value)
    pagination.total = wines.value.length
  } catch (e) {
    console.error(e)
  }
}

async function loadStats() {
  try {
    const data = await getCollectionOverview()
    Object.assign(stats, data)
  } catch (e) {
    console.error(e)
  }
}

async function loadMaturityStats() {
  try {
    const data = await getMaturityDistribution()
    Object.assign(maturityStats, data)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadWines()
  loadStats()
  loadMaturityStats()
})
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 12px;
}

.stats-summary {
  margin-bottom: 24px;
}

.summary-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.summary-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.summary-value.primary {
  color: #667eea;
}

.summary-value.success {
  color: #22c55e;
}

.summary-change {
  font-size: 13px;
  color: #9ca3af;
}

.summary-change.positive {
  color: #22c55e;
}

.wine-grid {
  margin-bottom: 24px;
}

.wine-card {
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.wine-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.15);
}

.wine-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.wine-image {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 120px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 8px;
  margin-bottom: 16px;
}

.wine-info {
  margin-bottom: 16px;
}

.wine-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.wine-chateau {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.wine-region {
  font-size: 12px;
  color: #9ca3af;
  margin: 0;
}

.wine-prices {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-top: 1px solid #f3f4f6;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 12px;
}

.price-item {
  text-align: center;
}

.price-label {
  font-size: 11px;
  color: #9ca3af;
  margin-bottom: 4px;
}

.price-value {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.price-value.current {
  color: #667eea;
}

.price-value.positive {
  color: #22c55e;
}

.price-value.negative {
  color: #ef4444;
}

.wine-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #6b7280;
}

.total-value {
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
}

.pagination {
  display: flex;
  justify-content: center;
}
</style>
