<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">品鉴活动</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索品鉴会名称、主题..."
          style="width: 300px;"
          clearable
          @keyup.enter="handleSearch"
          @clear="loadEvents"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 140px;" @change="loadEvents">
          <el-option v-for="st in statusOptions" :key="st.value" :label="st.label" :value="st.value" />
        </el-select>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          创建品鉴会
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="stats-summary">
      <el-col :span="6">
        <div class="summary-card">
          <div class="summary-label">总活动数</div>
          <div class="summary-value primary">{{ stats.total_events || 0 }}</div>
          <div class="summary-change">已完成 {{ stats.completed_events || 0 }} 场</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="summary-card">
          <div class="summary-label">进行中</div>
          <div class="summary-value success">{{ stats.ongoing_events || 0 }}</div>
          <div class="summary-change">待开始 {{ stats.upcoming_events || 0 }} 场</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="summary-card">
          <div class="summary-label">总参与人次</div>
          <div class="summary-value">{{ stats.total_attendees || 0 }}</div>
          <div class="summary-change">品鉴笔记 {{ stats.total_notes || 0 }} 篇</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="summary-card">
          <div class="summary-label">平均评分</div>
          <div class="summary-value warning">{{ stats.avg_overall_rating || 0 }}</div>
          <div class="summary-change">满分 5.0</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="event-grid">
      <el-col :span="8" v-for="event in events" :key="event.id">
        <el-card class="event-card card-shadow" @click="viewDetail(event.id)">
          <div class="event-header">
            <el-tag :type="getStatusType(event.status)" size="small">{{ event.status_display }}</el-tag>
            <div class="event-date">
              <el-icon><Calendar /></el-icon>
              <span>{{ formatDate(event.event_date) }}</span>
            </div>
          </div>
          <h3 class="event-name">{{ event.name }}</h3>
          <p class="event-theme">{{ event.theme }}</p>
          <div class="event-info">
            <div class="info-item">
              <el-icon><Location /></el-icon>
              <span>{{ event.location }}</span>
            </div>
            <div class="info-item">
              <el-icon><User /></el-icon>
              <span>{{ event.organizer }}</span>
            </div>
          </div>
          <div class="event-stats">
            <div class="stat-item">
              <el-icon><WineGlass /></el-icon>
              <span>{{ event.wine_count }} 款酒</span>
            </div>
            <div class="stat-item">
              <el-icon><UserFilled /></el-icon>
              <span>{{ event.checked_in_count }}/{{ event.max_attendees }} 人</span>
            </div>
            <div class="stat-item">
              <el-icon><Star /></el-icon>
              <span>{{ event.average_rating || '-' }}</span>
            </div>
          </div>
          <div class="event-progress">
            <el-progress 
              :percentage="Math.round(event.checked_in_count / event.max_attendees * 100)" 
              :stroke-width="8"
              :show-text="false"
            />
            <div class="progress-text">
              报名 {{ event.registered_count }} 人 · 已签到 {{ event.checked_in_count }} 人
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-pagination
      v-if="pagination.total > 0"
      class="pagination"
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :page-sizes="[9, 18, 36]"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="loadEvents"
      @current-change="loadEvents"
    />

    <el-dialog v-model="createDialogVisible" title="创建品鉴会" width="600px" :close-on-click-modal="false">
      <el-form :model="eventForm" :rules="eventRules" ref="eventFormRef" label-width="100px">
        <el-form-item label="品鉴会名称" prop="name">
          <el-input v-model="eventForm.name" placeholder="请输入品鉴会名称" />
        </el-form-item>
        <el-form-item label="主题" prop="theme">
          <el-input v-model="eventForm.theme" placeholder="请输入主题" />
        </el-form-item>
        <el-form-item label="活动时间" prop="event_date">
          <el-date-picker
            v-model="eventForm.event_date"
            type="datetime"
            placeholder="选择活动时间"
            style="width: 100%;"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="地点" prop="location">
          <el-input v-model="eventForm.location" placeholder="请输入地点" />
        </el-form-item>
        <el-form-item label="主办方" prop="organizer">
          <el-input v-model="eventForm.organizer" placeholder="请输入主办方" />
        </el-form-item>
        <el-form-item label="最大人数" prop="max_attendees">
          <el-input-number v-model="eventForm.max_attendees" :min="1" :max="200" />
        </el-form-item>
        <el-form-item label="品鉴酒品">
          <el-select v-model="eventForm.wines" multiple filterable placeholder="选择酒品" style="width: 100%;">
            <el-option v-for="wine in wineOptions" :key="wine.id" :label="`${wine.name} ${wine.vintage}`" :value="wine.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="eventForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="eventForm.notes" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateEvent">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTastingEvents, getTastingOverview, createTastingEvent } from '@/api/tasting'
import { getWines } from '@/api/collection'

const router = useRouter()

const events = ref([])
const stats = reactive({})
const searchKeyword = ref('')
const filterStatus = ref('')
const pagination = reactive({
  page: 1,
  pageSize: 9,
  total: 0
})

const createDialogVisible = ref(false)
const eventFormRef = ref(null)
const eventForm = reactive({
  name: '',
  theme: '',
  event_date: '',
  location: '',
  organizer: '',
  max_attendees: 20,
  wines: [],
  description: '',
  notes: ''
})
const eventRules = {
  name: [{ required: true, message: '请输入品鉴会名称', trigger: 'blur' }],
  theme: [{ required: true, message: '请输入主题', trigger: 'blur' }],
  event_date: [{ required: true, message: '请选择活动时间', trigger: 'change' }],
  location: [{ required: true, message: '请输入地点', trigger: 'blur' }],
  organizer: [{ required: true, message: '请输入主办方', trigger: 'blur' }],
  max_attendees: [{ required: true, message: '请输入最大人数', trigger: 'blur' }]
}

const wineOptions = ref([])

const statusOptions = [
  { value: 'upcoming', label: '待开始' },
  { value: 'ongoing', label: '进行中' },
  { value: 'completed', label: '已结束' },
  { value: 'cancelled', label: '已取消' }
]

function getStatusType(status) {
  const map = {
    upcoming: 'info',
    ongoing: 'success',
    completed: '',
    cancelled: 'danger'
  }
  return map[status] || ''
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function viewDetail(id) {
  router.push(`/tasting/${id}`)
}

function showCreateDialog() {
  eventForm.name = ''
  eventForm.theme = ''
  eventForm.event_date = ''
  eventForm.location = ''
  eventForm.organizer = ''
  eventForm.max_attendees = 20
  eventForm.wines = []
  eventForm.description = ''
  eventForm.notes = ''
  createDialogVisible.value = true
  loadWineOptions()
}

async function loadWineOptions() {
  try {
    const data = await getWines({ page_size: 100 })
    wineOptions.value = data.results || data
  } catch (e) {
    console.error(e)
  }
}

async function handleCreateEvent() {
  if (!eventFormRef.value) return
  await eventFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await createTastingEvent(eventForm)
        ElMessage.success('品鉴会创建成功')
        createDialogVisible.value = false
        loadEvents()
        loadStats()
      } catch (e) {
        console.error(e)
      }
    }
  })
}

async function loadEvents() {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filterStatus.value) params.status = filterStatus.value

    const data = await getTastingEvents(params)
    events.value = data.results || data
    pagination.total = data.count || data.length
  } catch (e) {
    console.error(e)
  }
}

async function handleSearch() {
  if (!searchKeyword.value) {
    loadEvents()
    return
  }
  try {
    const data = await getTastingEvents()
    const allEvents = data.results || data
    const keyword = searchKeyword.value.toLowerCase()
    events.value = allEvents.filter(e =>
      e.name.toLowerCase().includes(keyword) ||
      e.theme.toLowerCase().includes(keyword) ||
      e.location.toLowerCase().includes(keyword)
    )
    pagination.total = events.value.length
  } catch (e) {
    console.error(e)
  }
}

async function loadStats() {
  try {
    const data = await getTastingOverview()
    Object.assign(stats, data)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadEvents()
  loadStats()
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

.summary-value.warning {
  color: #f59e0b;
}

.summary-change {
  font-size: 13px;
  color: #9ca3af;
}

.event-grid {
  margin-bottom: 24px;
}

.event-card {
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.event-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.15);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.event-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6b7280;
}

.event-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.event-theme {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 16px 0;
}

.event-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}

.event-stats {
  display: flex;
  justify-content: space-around;
  padding: 12px 0;
  border-top: 1px solid #f3f4f6;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6b7280;
}

.event-progress {
  margin-top: 8px;
}

.progress-text {
  font-size: 12px;
  color: #9ca3af;
  text-align: center;
  margin-top: 4px;
}

.pagination {
  display: flex;
  justify-content: center;
}
</style>
