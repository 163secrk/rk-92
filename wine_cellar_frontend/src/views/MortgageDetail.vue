<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-button text @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        抵押申请详情
      </h2>
      <div class="header-actions" v-if="application">
        <template v-if="application.status === 'draft'">
          <el-button type="primary" @click="handleSubmitApplication">提交申请</el-button>
        </template>
        <template v-if="application.status === 'submitted'">
          <el-button type="warning" @click="handleStartReview">开始审核</el-button>
        </template>
        <template v-if="application.status === 'reviewing'">
          <el-button type="success" @click="showApproveDialog">批准</el-button>
          <el-button type="danger" @click="showRejectDialog">拒绝</el-button>
        </template>
        <template v-if="application.status === 'approved'">
          <el-button type="primary" @click="disburse">放款</el-button>
        </template>
      </div>
    </div>

    <div v-if="application" class="detail-content">
      <el-row :gutter="24">
        <el-col :span="8">
          <el-card class="card-shadow">
            <div class="status-header" :class="`status-${application.status}`">
              <el-tag size="large" :type="getStatusType(application.status)">
                {{ application.status_display }}
              </el-tag>
              <span class="application-id">#{{ application.id }}</span>
            </div>
            <div class="applicant-info">
              <h3>{{ application.applicant_name }}</h3>
              <p><el-icon><Phone /></el-icon> {{ application.applicant_phone }}</p>
              <p><el-icon><Message /></el-icon> {{ application.applicant_email }}</p>
              <p><el-icon><Postcard /></el-icon> {{ application.applicant_id }}</p>
            </div>
            <div class="loan-summary">
              <div class="summary-item">
                <div class="label">申请金额</div>
                <div class="value">¥{{ formatNumber(application.loan_amount) }}</div>
              </div>
              <div class="summary-item" v-if="application.approved_amount">
                <div class="label">批准金额</div>
                <div class="value primary">¥{{ formatNumber(application.approved_amount) }}</div>
              </div>
              <div class="summary-item">
                <div class="label">期限</div>
                <div class="value">{{ application.loan_term_months }}个月</div>
              </div>
              <div class="summary-item">
                <div class="label">年利率</div>
                <div class="value">{{ application.interest_rate }}%</div>
              </div>
              <div class="summary-item" v-if="application.ltv_ratio">
                <div class="label">抵押率</div>
                <div class="value">{{ application.ltv_ratio.toFixed(1) }}%</div>
              </div>
              <div class="summary-item" v-if="application.collateral_value">
                <div class="label">抵押品估值</div>
                <div class="value">¥{{ formatNumber(application.collateral_value) }}</div>
              </div>
              <div class="summary-item" v-if="application.remaining_amount">
                <div class="label">剩余本金</div>
                <div class="value warning">¥{{ formatNumber(application.remaining_amount) }}</div>
              </div>
              <div class="summary-item" v-if="application.total_paid">
                <div class="label">已还金额</div>
                <div class="value success">¥{{ formatNumber(application.total_paid) }}</div>
              </div>
            </div>
          </el-card>

          <el-card class="card-shadow purpose-card">
            <template #header>
              <span>贷款用途</span>
            </template>
            <p>{{ application.purpose }}</p>
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-card class="card-shadow">
            <template #header>
              <div class="card-header">
                <span>抵押品列表</span>
                <el-button type="primary" size="small" @click="showAddCollateralDialog" :disabled="!canAddCollateral">
                  <el-icon><Plus /></el-icon>
                  添加抵押品
                </el-button>
              </div>
            </template>
            <el-table :data="application.collaterals" stripe>
              <el-table-column prop="wine_name" label="酒品名称" />
              <el-table-column prop="wine_vintage" label="年份" width="80" />
              <el-table-column prop="quantity" label="数量(瓶)" width="100" />
              <el-table-column label="单价">
                <template #default="{ row }">
                  ¥{{ formatNumber(row.unit_value) }}
                </template>
              </el-table-column>
              <el-table-column label="总价值">
                <template #default="{ row }">
                  ¥{{ formatNumber(row.total_value) }}
                </template>
              </el-table-column>
              <el-table-column prop="storage_location" label="存放位置" width="120" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.released ? 'info' : 'success'" size="small">
                    {{ row.released ? '已解押' : '抵押中' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button size="small" type="danger" link :disabled="row.released || !canAddCollateral" @click="removeCollateral(row)">
                    移除
                  </el-button>
                  <el-button size="small" type="primary" link :disabled="!row.released" @click="releaseCollateral(row)">
                    解押
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <el-card class="card-shadow schedule-card" v-if="application.schedules && application.schedules.length > 0">
            <template #header>
              <span>还款计划</span>
            </template>
            <el-table :data="application.schedules" stripe>
              <el-table-column prop="payment_number" label="期数" width="70" />
              <el-table-column prop="due_date" label="还款日" width="120" />
              <el-table-column label="应还本金">
                <template #default="{ row }">
                  ¥{{ formatNumber(row.principal_amount) }}
                </template>
              </el-table-column>
              <el-table-column label="应还利息">
                <template #default="{ row }">
                  ¥{{ formatNumber(row.interest_amount) }}
                </template>
              </el-table-column>
              <el-table-column label="应还总额">
                <template #default="{ row }">
                  ¥{{ formatNumber(row.total_amount) }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.paid ? 'success' : 'warning'" size="small">
                    {{ row.paid ? '已还' : '待还' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="还款日期" width="120">
                <template #default="{ row }">
                  {{ row.paid_date || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" v-if="application.status === 'active'">
                <template #default="{ row }">
                  <el-button size="small" type="primary" link :disabled="row.paid" @click="showPaymentDialog(row)">
                    还款
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="addCollateralDialogVisible" title="添加抵押品" width="600px">
      <el-form label-width="100px">
        <el-form-item label="选择酒品">
          <el-select v-model="collateralForm.wine_id" filterable placeholder="请选择酒品" style="width: 100%;">
            <el-option v-for="wine in availableWines" :key="wine.id" :label="`${wine.name} ${wine.vintage}`" :value="wine.id">
              <span>{{ wine.name }} {{ wine.vintage }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                ¥{{ formatNumber(wine.current_value) }}/瓶 · 库存{{ wine.quantity }}瓶
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="collateralForm.quantity" :min="1" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addCollateralDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addCollateral">添加</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="paymentDialogVisible" title="确认还款" width="400px">
      <div v-if="currentSchedule" class="payment-info">
        <p>期数：第 {{ currentSchedule.payment_number }} 期</p>
        <p>还款日：{{ currentSchedule.due_date }}</p>
        <p>应还总额：<strong>¥{{ formatNumber(currentSchedule.total_amount) }}</strong></p>
      </div>
      <el-form label-width="100px" class="payment-form">
        <el-form-item label="还款金额">
          <el-input-number v-model="paymentForm.amount" :min="0" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="还款方式">
          <el-select v-model="paymentForm.payment_method" style="width: 100%;">
            <el-option value="bank_transfer" label="银行转账" />
            <el-option value="alipay" label="支付宝" />
            <el-option value="wechat" label="微信支付" />
            <el-option value="cash" label="现金" />
          </el-select>
        </el-form-item>
        <el-form-item label="交易流水号">
          <el-input v-model="paymentForm.transaction_id" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="paymentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="recordPayment">确认还款</el-button>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getApplication, submitApplication as apiSubmitApplication, startReview as apiStartReview, approveApplication as apiApproveApplication,
  rejectApplication as apiRejectApplication, disburseApplication,
  addCollateral as apiAddCollateral, removeCollateral as apiRemoveCollateral,
  releaseCollateral, recordPayment as apiRecordPayment
} from '@/api/mortgage'
import { getWines } from '@/api/collection'

const route = useRoute()
const router = useRouter()

const application = ref(null)
const availableWines = ref([])
const addCollateralDialogVisible = ref(false)
const paymentDialogVisible = ref(false)
const approveDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const currentSchedule = ref(null)

const collateralForm = reactive({
  wine_id: null,
  quantity: 1
})

const paymentForm = reactive({
  amount: 0,
  payment_method: 'bank_transfer',
  transaction_id: ''
})

const approveForm = reactive({
  approved_amount: 0,
  review_notes: ''
})

const rejectForm = reactive({
  review_notes: ''
})

const canAddCollateral = computed(() => {
  if (!application.value) return false
  return ['draft', 'submitted', 'reviewing'].includes(application.value.status)
})

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
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

async function loadApplication() {
  try {
    application.value = await getApplication(route.params.id)
  } catch (e) {
    console.error(e)
  }
}

async function loadAvailableWines() {
  try {
    const data = await getWines({ page_size: 100 })
    availableWines.value = data.results || data
  } catch (e) {
    console.error(e)
  }
}

function showAddCollateralDialog() {
  collateralForm.wine_id = null
  collateralForm.quantity = 1
  addCollateralDialogVisible.value = true
}

async function addCollateral() {
  if (!collateralForm.wine_id) {
    ElMessage.warning('请选择酒品')
    return
  }
  try {
    await apiAddCollateral(application.value.id, collateralForm)
    ElMessage.success('添加成功')
    addCollateralDialogVisible.value = false
    loadApplication()
    loadAvailableWines()
  } catch (e) {
    console.error(e)
    ElMessage.error(e.response?.data?.detail || '添加失败，请重试')
  }
}

async function removeCollateral(row) {
  ElMessageBox.confirm('确认移除该抵押品？', '确认', {
    type: 'warning'
  }).then(async () => {
    try {
      await apiRemoveCollateral(application.value.id, { collateral_id: row.id })
      ElMessage.success('移除成功')
      loadApplication()
      loadAvailableWines()
    } catch (e) {
      console.error(e)
      ElMessage.error(e.response?.data?.detail || '移除失败，请重试')
    }
  }).catch(() => {})
}

function showPaymentDialog(row) {
  currentSchedule.value = row
  paymentForm.amount = row.total_amount
  paymentForm.transaction_id = ''
  paymentDialogVisible.value = true
}

async function recordPayment() {
  if (!currentSchedule.value) return
  try {
    await apiRecordPayment(currentSchedule.value.id, paymentForm)
    ElMessage.success('还款成功')
    paymentDialogVisible.value = false
    loadApplication()
  } catch (e) {
    console.error(e)
  }
}

async function handleSubmitApplication() {
  try {
    await apiSubmitApplication(route.params.id)
    ElMessage.success('已提交申请')
    loadApplication()
  } catch (e) {
    console.error(e)
  }
}

async function handleStartReview() {
  try {
    await apiStartReview(route.params.id)
    ElMessage.success('已开始审核')
    loadApplication()
  } catch (e) {
    console.error(e)
  }
}

function showApproveDialog() {
  approveForm.approved_amount = application.value.loan_amount
  approveForm.review_notes = ''
  approveDialogVisible.value = true
}

async function approveApplication() {
  try {
    await apiApproveApplication(route.params.id, approveForm)
    ElMessage.success('已批准申请')
    approveDialogVisible.value = false
    loadApplication()
  } catch (e) {
    console.error(e)
  }
}

function showRejectDialog() {
  rejectForm.review_notes = ''
  rejectDialogVisible.value = true
}

async function rejectApplication() {
  try {
    await apiRejectApplication(route.params.id, rejectForm)
    ElMessage.success('已拒绝申请')
    rejectDialogVisible.value = false
    loadApplication()
  } catch (e) {
    console.error(e)
  }
}

async function disburse() {
  ElMessageBox.confirm('确认放款？此操作将生成还款计划。', '确认', {
    confirmButtonText: '确认放款',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await disburseApplication(route.params.id)
      ElMessage.success('已成功放款')
      loadApplication()
    } catch (e) {
      console.error(e)
      ElMessage.error(e.response?.data?.detail || '放款失败，请重试')
      loadApplication()
    }
  }).catch(() => {})
}

onMounted(() => {
  loadApplication()
  loadAvailableWines()
})
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 12px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.application-id {
  font-size: 14px;
  color: #9ca3af;
}

.applicant-info {
  margin-bottom: 20px;
}

.applicant-info h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.applicant-info p {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  margin: 8px 0;
  font-size: 14px;
}

.loan-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.summary-item {
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.summary-item .label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 4px;
}

.summary-item .value {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.summary-item .value.primary {
  color: #667eea;
}

.summary-item .value.success {
  color: #22c55e;
}

.summary-item .value.warning {
  color: #f59e0b;
}

.purpose-card {
  margin-top: 24px;
}

.purpose-card p {
  line-height: 1.8;
  color: #4b5563;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.schedule-card {
  margin-top: 24px;
}

.payment-info {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 20px;
}

.payment-info p {
  margin: 8px 0;
}

.payment-form {
  margin-top: 16px;
}

.detail-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
