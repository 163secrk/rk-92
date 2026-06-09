<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">名酒抵押管理</h2>
      <div class="header-actions">
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 160px;" @change="loadApplications">
          <el-option v-for="st in statusOptions" :key="st.value" :label="st.label" :value="st.value" />
        </el-select>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建申请
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <div class="stat-label">申请总数</div>
          <div class="stat-value">{{ stats.total_applications }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
          <div class="stat-label">进行中贷款</div>
          <div class="stat-value">{{ stats.active_loans }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <div class="stat-label">贷款余额</div>
          <div class="stat-value">¥{{ formatNumber(stats.total_remaining) }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <div class="stat-label">累计放款</div>
          <div class="stat-value">¥{{ formatNumber(stats.total_loan_amount) }}</div>
        </div>
      </el-col>
    </el-row>

    <el-card class="card-shadow">
      <el-table :data="applications" stripe @row-click="viewDetail">
        <el-table-column prop="id" label="申请编号" width="100" />
        <el-table-column prop="applicant_name" label="申请人" width="100" />
        <el-table-column prop="applicant_phone" label="联系电话" width="130" />
        <el-table-column label="申请金额" width="140">
          <template #default="{ row }">
            ¥{{ formatNumber(row.loan_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="批准金额" width="140">
          <template #default="{ row }">
            <span v-if="row.approved_amount">¥{{ formatNumber(row.approved_amount) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="loan_term_months" label="期限" width="80">
          <template #default="{ row }">
            {{ row.loan_term_months }}月
          </template>
        </el-table-column>
        <el-table-column prop="interest_rate" label="利率" width="80">
          <template #default="{ row }">
            {{ row.interest_rate }}%
          </template>
        </el-table-column>
        <el-table-column label="抵押率" width="100">
          <template #default="{ row }">
            <span v-if="row.ltv_ratio">{{ row.ltv_ratio.toFixed(1) }}%</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click.stop="viewDetail(row)">
              查看详情
            </el-button>
            <template v-if="row.status === 'draft'">
              <el-button type="primary" size="small" link @click.stop="submitApplication(row)">
                提交
              </el-button>
            </template>
            <template v-if="row.status === 'submitted'">
              <el-button type="warning" size="small" link @click.stop="startReview(row)">
                开始审核
              </el-button>
            </template>
            <template v-if="row.status === 'reviewing'">
              <el-button type="success" size="small" link @click.stop="showApproveDialog(row)">
                批准
              </el-button>
              <el-button type="danger" size="small" link @click.stop="showRejectDialog(row)">
                拒绝
              </el-button>
            </template>
            <template v-if="row.status === 'approved'">
              <el-button type="primary" size="small" link @click.stop="disburse(row)">
                放款
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadApplications"
        @current-change="loadApplications"
      />
    </el-card>

    <el-dialog v-model="createDialogVisible" title="新建抵押申请" width="600px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="申请人">
          <el-input v-model="createForm.applicant_name" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="createForm.applicant_id" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="createForm.applicant_phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="createForm.applicant_email" />
        </el-form-item>
        <el-form-item label="贷款金额">
          <el-input-number v-model="createForm.loan_amount" :min="0" :step="10000" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="贷款期限">
          <el-select v-model="createForm.loan_term_months" style="width: 100%;">
            <el-option :value="3" label="3个月" />
            <el-option :value="6" label="6个月" />
            <el-option :value="12" label="12个月" />
            <el-option :value="24" label="24个月" />
            <el-option :value="36" label="36个月" />
          </el-select>
        </el-form-item>
        <el-form-item label="年利率">
          <el-input-number v-model="createForm.interest_rate" :min="0" :max="30" :step="0.1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="贷款用途">
          <el-input v-model="createForm.purpose" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createApplication">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="approveDialogVisible" title="批准贷款" width="500px">
      <el-form label-width="100px">
        <el-form-item label="批准金额">
          <el-input-number v-model="approveForm.approved_amount" :min="0" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="approveForm.review_notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="approveApplication">确认批准</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="rejectDialogVisible" title="拒绝贷款" width="500px">
      <el-form label-width="100px">
        <el-form-item label="拒绝原因">
          <el-input v-model="rejectForm.review_notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="rejectApplication">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getApplications, getMortgageStats, createApplication as apiCreateApplication,
  submitApplication as apiSubmitApplication, startReview as apiStartReview,
  approveApplication as apiApproveApplication, rejectApplication as apiRejectApplication,
  disburseApplication as apiDisburseApplication
} from '@/api/mortgage'

const router = useRouter()

const applications = ref([])
const stats = reactive({
  total_applications: 0,
  active_loans: 0,
  total_remaining: 0,
  total_loan_amount: 0
})
const filterStatus = ref('')
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const createDialogVisible = ref(false)
const approveDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const currentApplication = ref(null)

const createForm = reactive({
  applicant_name: '',
  applicant_id: '',
  applicant_phone: '',
  applicant_email: '',
  loan_amount: 0,
  loan_term_months: 12,
  interest_rate: 4.8,
  purpose: ''
})

const approveForm = reactive({
  approved_amount: 0,
  review_notes: ''
})

const rejectForm = reactive({
  review_notes: ''
})

const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'submitted', label: '已提交' },
  { value: 'reviewing', label: '审核中' },
  { value: 'approved', label: '已批准' },
  { value: 'rejected', label: '已拒绝' },
  { value: 'active', label: '还款中' },
  { value: 'completed', label: '已结清' },
  { value: 'defaulted', label: '已违约' },
  { value: 'liquidated', label: '已处置' },
]

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}

function getStatusType(status) {
  const map = {
    draft: 'info',
    submitted: '',
    reviewing: 'warning',
    approved: 'success',
    rejected: 'danger',
    active: 'primary',
    completed: 'success',
    defaulted: 'danger',
    liquidated: 'info'
  }
  return map[status] || ''
}

function viewDetail(row) {
  router.push(`/mortgage/${row.id}`)
}

function showCreateDialog() {
  Object.assign(createForm, {
    applicant_name: '',
    applicant_id: '',
    applicant_phone: '',
    applicant_email: '',
    loan_amount: 0,
    loan_term_months: 12,
    interest_rate: 4.8,
    purpose: ''
  })
  createDialogVisible.value = true
}

async function createApplication() {
  try {
    await apiCreateApplication(createForm)
    ElMessage.success('申请创建成功')
    createDialogVisible.value = false
    loadApplications()
  } catch (e) {
    console.error(e)
  }
}

async function submitApplication(row) {
  try {
    await apiSubmitApplication(row.id)
    ElMessage.success('已提交申请')
    loadApplications()
  } catch (e) {
    console.error(e)
  }
}

async function startReview(row) {
  try {
    await apiStartReview(row.id)
    ElMessage.success('已开始审核')
    loadApplications()
  } catch (e) {
    console.error(e)
  }
}

function showApproveDialog(row) {
  currentApplication.value = row
  approveForm.approved_amount = row.loan_amount
  approveForm.review_notes = ''
  approveDialogVisible.value = true
}

async function approveApplication() {
  if (!currentApplication.value) return
  try {
    await apiApproveApplication(currentApplication.value.id, approveForm)
    ElMessage.success('已批准申请')
    approveDialogVisible.value = false
    loadApplications()
  } catch (e) {
    console.error(e)
  }
}

function showRejectDialog(row) {
  currentApplication.value = row
  rejectForm.review_notes = ''
  rejectDialogVisible.value = true
}

async function rejectApplication() {
  if (!currentApplication.value) return
  try {
    await apiRejectApplication(currentApplication.value.id, rejectForm)
    ElMessage.success('已拒绝申请')
    rejectDialogVisible.value = false
    loadApplications()
  } catch (e) {
    console.error(e)
  }
}

async function disburse(row) {
  ElMessageBox.confirm('确认放款？此操作将生成还款计划。', '确认', {
    confirmButtonText: '确认放款',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await apiDisburseApplication(row.id)
      ElMessage.success('已成功放款')
      loadApplications()
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {})
}

async function loadApplications() {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filterStatus.value) params.status = filterStatus.value

    const data = await getApplications(params)
    applications.value = data.results || data
    pagination.total = data.count || data.length
  } catch (e) {
    console.error(e)
  }
}

async function loadStats() {
  try {
    const data = await getMortgageStats()
    Object.assign(stats, data)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadApplications()
  loadStats()
})
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  padding: 24px;
  border-radius: 12px;
  color: white;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
