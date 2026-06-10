<template>
  <div class="page-container">
    <div v-if="event" class="detail-content">
      <div class="detail-header">
        <div>
          <div class="header-top">
            <el-tag :type="getStatusType(event.status)" size="large">{{ event.status_display }}</el-tag>
            <span class="event-date">
              <el-icon><Calendar /></el-icon>
              {{ formatDateTime(event.event_date) }}
            </span>
          </div>
          <h1 class="event-title">{{ event.name }}</h1>
          <p class="event-subtitle">{{ event.theme }}</p>
        </div>
        <div class="header-actions">
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <el-button type="primary" @click="showCheckInDialog">
            <el-icon><UserFilled /></el-icon>
            人员签到
          </el-button>
          <el-button type="success" @click="showNoteDialog">
            <el-icon><EditPen /></el-icon>
            品鉴笔记
          </el-button>
        </div>
      </div>

      <el-row :gutter="20" class="info-section">
        <el-col :span="16">
          <el-card class="info-card card-shadow">
            <div class="card-title">活动信息</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="地点">
                <span><el-icon><Location /></el-icon> {{ event.location }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="主办方">
                <span><el-icon><User /></el-icon> {{ event.organizer }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="创建人">{{ event.created_by_name }}</el-descriptions-item>
              <el-descriptions-item label="最大人数">{{ event.max_attendees }} 人</el-descriptions-item>
              <el-descriptions-item label="报名人数">{{ event.registered_count }} 人</el-descriptions-item>
              <el-descriptions-item label="签到人数">{{ event.checked_in_count }} 人</el-descriptions-item>
              <el-descriptions-item label="平均评分">
                <el-rate :model-value="event.average_rating" disabled show-score text-color="#667eea" />
              </el-descriptions-item>
              <el-descriptions-item label="笔记数量">{{ eventNotes.length }} 篇</el-descriptions-item>
              <el-descriptions-item label="描述" :span="2">
                <p v-if="event.description" class="description-text">{{ event.description }}</p>
                <span v-else class="text-muted">暂无描述</span>
              </el-descriptions-item>
              <el-descriptions-item label="备注" :span="2">
                <p v-if="event.notes" class="description-text">{{ event.notes }}</p>
                <span v-else class="text-muted">暂无备注</span>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card class="info-card card-shadow" v-if="eventStats && eventStats.wine_stats.length > 0">
            <div class="card-title">酒品评分统计</div>
            <el-table :data="eventStats.wine_stats" stripe>
              <el-table-column prop="wine_name" label="酒品名称" />
              <el-table-column prop="wine_vintage" label="年份" width="80" />
              <el-table-column prop="note_count" label="评分次数" width="100" align="center" />
              <el-table-column label="颜色评分" width="120" align="center">
                <template #default="{ row }">
                  <el-rate :model-value="row.avg_color" disabled show-score />
                </template>
              </el-table-column>
              <el-table-column label="香气评分" width="120" align="center">
                <template #default="{ row }">
                  <el-rate :model-value="row.avg_aroma" disabled show-score />
                </template>
              </el-table-column>
              <el-table-column label="口感评分" width="120" align="center">
                <template #default="{ row }">
                  <el-rate :model-value="row.avg_taste" disabled show-score />
                </template>
              </el-table-column>
              <el-table-column label="余味评分" width="120" align="center">
                <template #default="{ row }">
                  <el-rate :model-value="row.avg_finish" disabled show-score />
                </template>
              </el-table-column>
              <el-table-column label="综合评分" width="140" align="center">
                <template #default="{ row }">
                  <el-rate :model-value="row.avg_overall" disabled show-score text-color="#667eea" />
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <el-card class="info-card card-shadow">
            <div class="card-title">
              <span>品鉴笔记</span>
              <el-tag size="small" type="info">{{ eventNotes.length }} 篇</el-tag>
            </div>
            <el-empty v-if="eventNotes.length === 0" description="暂无品鉴笔记" />
            <div v-else class="notes-list">
              <div v-for="note in eventNotes" :key="note.id" class="note-item">
                <div class="note-header">
                  <div class="note-user">
                    <el-avatar :size="40" icon="UserFilled" />
                    <div>
                      <div class="note-user-name">{{ note.attendee_name }}</div>
                      <div class="note-wine">{{ note.wine_name }} {{ note.wine_vintage }}</div>
                    </div>
                  </div>
                  <div class="note-rating">
                    <el-rate :model-value="note.overall_rating" disabled show-score text-color="#667eea" />
                    <div class="note-time">{{ formatDateTime(note.created_at) }}</div>
                  </div>
                </div>
                <div class="note-ratings-detail">
                  <div class="rating-item">
                    <span class="rating-label">颜色</span>
                    <el-rate :model-value="note.color_rating" disabled />
                    <span class="rating-value">{{ note.color_rating }}分</span>
                  </div>
                  <div class="rating-item">
                    <span class="rating-label">香气</span>
                    <el-rate :model-value="note.aroma_rating" disabled />
                    <span class="rating-value">{{ note.aroma_rating }}分</span>
                  </div>
                  <div class="rating-item">
                    <span class="rating-label">口感</span>
                    <el-rate :model-value="note.taste_rating" disabled />
                    <span class="rating-value">{{ note.taste_rating }}分</span>
                  </div>
                  <div class="rating-item">
                    <span class="rating-label">余味</span>
                    <el-rate :model-value="note.finish_rating" disabled />
                    <span class="rating-value">{{ note.finish_rating }}分</span>
                  </div>
                </div>
                <el-button type="primary" link @click="showNoteDetail(note)" style="padding: 0;">查看详情</el-button>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="info-card card-shadow">
            <div class="card-title">
              <span>品鉴酒品</span>
              <el-tag size="small" type="info">{{ event.wine_list?.length || 0 }} 款</el-tag>
            </div>
            <el-empty v-if="!event.wine_list || event.wine_list.length === 0" description="暂无酒品" />
            <div v-else class="wine-list">
              <div v-for="wine in event.wine_list" :key="wine.id" class="wine-item">
                <div class="wine-info">
                  <div class="wine-name">{{ wine.name }}</div>
                  <div class="wine-meta">{{ wine.chateau }} · {{ wine.vintage }}</div>
                </div>
                <el-tag :type="getCategoryType(wine.category)" size="small">{{ wine.category_display }}</el-tag>
              </div>
            </div>
          </el-card>

          <el-card class="info-card card-shadow">
            <div class="card-title">
              <span>签到人员</span>
              <el-tag size="small" type="success">{{ checkedInAttendees.length }}/{{ attendees.length }}</el-tag>
            </div>
            <div class="attendees-filter">
              <el-radio-group v-model="attendeeFilter" size="small" @change="filterAttendees">
                <el-radio-button value="all">全部</el-radio-button>
                <el-radio-button value="checked">已签到</el-radio-button>
                <el-radio-button value="unchecked">未签到</el-radio-button>
              </el-radio-group>
            </div>
            <el-empty v-if="filteredAttendees.length === 0" description="暂无人员" />
            <div v-else class="attendees-list">
              <div v-for="attendee in filteredAttendees" :key="attendee.id" class="attendee-item">
                <div class="attendee-info">
                  <div class="attendee-name">{{ attendee.name }}</div>
                  <div class="attendee-meta" v-if="attendee.company">{{ attendee.company }} · {{ attendee.position }}</div>
                  <div class="attendee-meta" v-else>{{ attendee.phone }}</div>
                </div>
                <div v-if="attendee.checked_in" class="attendee-status checked">
                  <el-icon><CircleCheck /></el-icon>
                  <span>{{ formatTime(attendee.check_in_time) }}</span>
                </div>
                <div v-else class="attendee-status unchecked">
                  <el-icon><Clock /></el-icon>
                  <span>待签到</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="checkInDialogVisible" title="人员签到" width="500px">
      <el-form :model="checkInForm" label-width="100px">
        <el-form-item label="手机号">
          <el-input v-model="checkInForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="checkInForm.name" placeholder="请输入姓名" />
        </el-form-item>
      </el-form>
      <div class="dialog-tip">
        <el-icon><InfoFilled /></el-icon>
        <span>输入手机号或姓名即可签到，未报名人员将自动添加</span>
      </div>
      <template #footer>
        <el-button @click="checkInDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCheckIn">确认签到</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="noteDialogVisible" title="提交品鉴笔记" width="700px" :close-on-click-modal="false">
      <el-form :model="noteForm" :rules="noteRules" ref="noteFormRef" label-width="100px">
        <el-form-item label="品鉴人" prop="attendee">
          <el-select v-model="noteForm.attendee" filterable placeholder="选择已签到人员" style="width: 100%;">
            <el-option 
              v-for="a in checkedInAttendees" 
              :key="a.id" 
              :label="`${a.name}${a.company ? ' - ' + a.company : ''}`" 
              :value="a.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="品鉴酒品" prop="wine">
          <el-select v-model="noteForm.wine" filterable placeholder="选择酒品" style="width: 100%;">
            <el-option 
              v-for="w in event?.wine_list" 
              :key="w.id" 
              :label="`${w.name} ${w.vintage}`" 
              :value="w.id" 
            />
          </el-select>
        </el-form-item>

        <div class="rating-section">
          <div class="rating-section-title">多维度评分（1-5分）</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="颜色评分" prop="color_rating">
                <el-rate v-model="noteForm.color_rating" :max="5" show-score text-color="#667eea" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="香气评分" prop="aroma_rating">
                <el-rate v-model="noteForm.aroma_rating" :max="5" show-score text-color="#667eea" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="口感评分" prop="taste_rating">
                <el-rate v-model="noteForm.taste_rating" :max="5" show-score text-color="#667eea" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="余味评分" prop="finish_rating">
                <el-rate v-model="noteForm.finish_rating" :max="5" show-score text-color="#667eea" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="note-preview">
          <div class="preview-label">综合评分</div>
          <el-rate :model-value="calculateOverall()" disabled show-score text-color="#667eea" />
        </div>

        <el-form-item label="颜色描述">
          <el-input v-model="noteForm.color_notes" type="textarea" :rows="2" placeholder="如：深宝石红色、略带紫色光泽..." />
        </el-form-item>
        <el-form-item label="香气描述">
          <el-input v-model="noteForm.aroma_notes" type="textarea" :rows="2" placeholder="如：黑加仑、紫罗兰、橡木桶香气..." />
        </el-form-item>
        <el-form-item label="口感描述">
          <el-input v-model="noteForm.taste_notes" type="textarea" :rows="2" placeholder="如：单宁柔顺、酸度平衡、酒体饱满..." />
        </el-form-item>
        <el-form-item label="余味描述">
          <el-input v-model="noteForm.finish_notes" type="textarea" :rows="2" placeholder="如：余味悠长、果香持久..." />
        </el-form-item>
        <el-form-item label="综合评价">
          <el-input v-model="noteForm.general_notes" type="textarea" :rows="3" placeholder="请输入综合评价..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitNote">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="noteDetailVisible" title="品鉴笔记详情" width="600px">
      <div v-if="selectedNote">
        <div class="detail-note-header">
          <div class="detail-note-user">
            <el-avatar :size="50" icon="UserFilled" />
            <div>
              <div class="detail-note-name">{{ selectedNote.attendee_name }}</div>
              <div class="detail-note-wine">{{ selectedNote.wine_name }} {{ selectedNote.wine_vintage }}</div>
            </div>
          </div>
          <el-rate :model-value="selectedNote.overall_rating" disabled show-score text-color="#667eea" />
        </div>

        <el-descriptions :column="2" border class="detail-ratings">
          <el-descriptions-item label="颜色评分">
            <el-rate :model-value="selectedNote.color_rating" disabled show-score />
          </el-descriptions-item>
          <el-descriptions-item label="香气评分">
            <el-rate :model-value="selectedNote.aroma_rating" disabled show-score />
          </el-descriptions-item>
          <el-descriptions-item label="口感评分">
            <el-rate :model-value="selectedNote.taste_rating" disabled show-score />
          </el-descriptions-item>
          <el-descriptions-item label="余味评分">
            <el-rate :model-value="selectedNote.finish_rating" disabled show-score />
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-notes-section">
          <div v-if="selectedNote.color_notes" class="note-section">
            <div class="note-section-title">颜色描述</div>
            <p>{{ selectedNote.color_notes }}</p>
          </div>
          <div v-if="selectedNote.aroma_notes" class="note-section">
            <div class="note-section-title">香气描述</div>
            <p>{{ selectedNote.aroma_notes }}</p>
          </div>
          <div v-if="selectedNote.taste_notes" class="note-section">
            <div class="note-section-title">口感描述</div>
            <p>{{ selectedNote.taste_notes }}</p>
          </div>
          <div v-if="selectedNote.finish_notes" class="note-section">
            <div class="note-section-title">余味描述</div>
            <p>{{ selectedNote.finish_notes }}</p>
          </div>
          <div v-if="selectedNote.general_notes" class="note-section">
            <div class="note-section-title">综合评价</div>
            <p>{{ selectedNote.general_notes }}</p>
          </div>
        </div>

        <div class="detail-footer">
          <span class="text-muted">提交时间：{{ formatDateTime(selectedNote.created_at) }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  getTastingEvent, 
  checkInEvent, 
  getEventAttendees, 
  getEventNotes, 
  getEventStats,
  createTastingNote 
} from '@/api/tasting'

const route = useRoute()
const router = useRouter()

const event = ref(null)
const attendees = ref([])
const eventNotes = ref([])
const eventStats = ref(null)

const checkInDialogVisible = ref(false)
const checkInForm = reactive({
  phone: '',
  name: ''
})

const noteDialogVisible = ref(false)
const noteDetailVisible = ref(false)
const noteFormRef = ref(null)
const selectedNote = ref(null)
const noteForm = reactive({
  attendee: '',
  wine: '',
  color_rating: 3,
  aroma_rating: 3,
  taste_rating: 3,
  finish_rating: 3,
  color_notes: '',
  aroma_notes: '',
  taste_notes: '',
  finish_notes: '',
  general_notes: ''
})
const noteRules = {
  attendee: [{ required: true, message: '请选择品鉴人', trigger: 'change' }],
  wine: [{ required: true, message: '请选择品鉴酒品', trigger: 'change' }],
  color_rating: [{ required: true, message: '请评分', trigger: 'change' }],
  aroma_rating: [{ required: true, message: '请评分', trigger: 'change' }],
  taste_rating: [{ required: true, message: '请评分', trigger: 'change' }],
  finish_rating: [{ required: true, message: '请评分', trigger: 'change' }]
}

const attendeeFilter = ref('all')

const checkedInAttendees = computed(() => {
  return attendees.value.filter(a => a.checked_in)
})

const filteredAttendees = computed(() => {
  if (attendeeFilter.value === 'checked') {
    return attendees.value.filter(a => a.checked_in)
  } else if (attendeeFilter.value === 'unchecked') {
    return attendees.value.filter(a => !a.checked_in)
  }
  return attendees.value
})

function getStatusType(status) {
  const map = {
    upcoming: 'info',
    ongoing: 'success',
    completed: '',
    cancelled: 'danger'
  }
  return map[status] || ''
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

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function calculateOverall() {
  const total = noteForm.color_rating + noteForm.aroma_rating + noteForm.taste_rating + noteForm.finish_rating
  return Math.round(total / 4 * 10) / 10
}

function goBack() {
  router.push('/tasting')
}

function showCheckInDialog() {
  checkInForm.phone = ''
  checkInForm.name = ''
  checkInDialogVisible.value = true
}

function showNoteDialog() {
  if (checkedInAttendees.value.length === 0) {
    ElMessage.warning('请先完成人员签到')
    return
  }
  if (!event.value?.wine_list || event.value.wine_list.length === 0) {
    ElMessage.warning('当前品鉴会没有添加酒品')
    return
  }
  noteForm.attendee = ''
  noteForm.wine = ''
  noteForm.color_rating = 3
  noteForm.aroma_rating = 3
  noteForm.taste_rating = 3
  noteForm.finish_rating = 3
  noteForm.color_notes = ''
  noteForm.aroma_notes = ''
  noteForm.taste_notes = ''
  noteForm.finish_notes = ''
  noteForm.general_notes = ''
  noteDialogVisible.value = true
}

function showNoteDetail(note) {
  selectedNote.value = note
  noteDetailVisible.value = true
}

function filterAttendees() {
}

async function handleCheckIn() {
  if (!checkInForm.phone && !checkInForm.name) {
    ElMessage.warning('请输入手机号或姓名')
    return
  }
  try {
    await checkInEvent(route.params.id, checkInForm)
    ElMessage.success('签到成功')
    checkInDialogVisible.value = false
    loadEventData()
  } catch (e) {
    console.error(e)
  }
}

async function handleSubmitNote() {
  if (!noteFormRef.value) return
  await noteFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await createTastingNote({
          ...noteForm,
          event: route.params.id
        })
        ElMessage.success('品鉴笔记提交成功')
        noteDialogVisible.value = false
        loadEventData()
      } catch (e) {
        console.error(e)
      }
    }
  })
}

async function loadEvent() {
  try {
    event.value = await getTastingEvent(route.params.id)
  } catch (e) {
    console.error(e)
  }
}

async function loadAttendees() {
  try {
    attendees.value = await getEventAttendees(route.params.id)
  } catch (e) {
    console.error(e)
  }
}

async function loadNotes() {
  try {
    eventNotes.value = await getEventNotes(route.params.id)
  } catch (e) {
    console.error(e)
  }
}

async function loadStats() {
  try {
    eventStats.value = await getEventStats(route.params.id)
  } catch (e) {
    console.error(e)
  }
}

async function loadEventData() {
  await Promise.all([
    loadEvent(),
    loadAttendees(),
    loadNotes(),
    loadStats()
  ])
}

onMounted(() => {
  loadEventData()
})
</script>

<style scoped>
.detail-header {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.event-date {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  font-size: 14px;
}

.event-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.event-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.info-section {
  margin-bottom: 24px;
}

.info-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: none;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.description-text {
  color: #4b5563;
  line-height: 1.6;
  margin: 0;
}

.text-muted {
  color: #9ca3af;
}

.wine-list {
  max-height: 300px;
  overflow-y: auto;
}

.wine-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.wine-item:last-child {
  border-bottom: none;
}

.wine-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
}

.wine-meta {
  font-size: 12px;
  color: #9ca3af;
}

.attendees-filter {
  margin-bottom: 16px;
}

.attendees-list {
  max-height: 400px;
  overflow-y: auto;
}

.attendee-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.attendee-item:last-child {
  border-bottom: none;
}

.attendee-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
}

.attendee-meta {
  font-size: 12px;
  color: #9ca3af;
}

.attendee-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.attendee-status.checked {
  color: #22c55e;
}

.attendee-status.unchecked {
  color: #f59e0b;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.note-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.note-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.note-user-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.note-wine {
  font-size: 12px;
  color: #6b7280;
}

.note-rating {
  text-align: right;
}

.note-time {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.note-ratings-detail {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
}

.rating-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.rating-label {
  font-size: 12px;
  color: #6b7280;
}

.rating-value {
  font-size: 12px;
  color: #667eea;
  font-weight: 500;
}

.dialog-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #eff6ff;
  border-radius: 8px;
  color: #2563eb;
  font-size: 13px;
}

.rating-section {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.rating-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
}

.note-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  border-radius: 8px;
  margin-bottom: 16px;
}

.preview-label {
  font-size: 14px;
  font-weight: 500;
  color: #4338ca;
}

.detail-note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-note-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-note-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.detail-note-wine {
  font-size: 13px;
  color: #6b7280;
}

.detail-ratings {
  margin-bottom: 20px;
}

.detail-notes-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.note-section {
  background: #f9fafb;
  padding: 12px;
  border-radius: 8px;
}

.note-section-title {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 8px;
}

.note-section p {
  margin: 0;
  color: #374151;
  line-height: 1.6;
}

.detail-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
  text-align: right;
}
</style>
