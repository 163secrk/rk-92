<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-button text @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        添加酒品
      </h2>
    </div>

    <el-card class="card-shadow">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        label-position="right"
      >
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="酒品名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入酒品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="酒庄" prop="chateau">
              <el-input v-model="form.chateau" placeholder="请输入酒庄名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="国家" prop="country">
              <el-input v-model="form.country" placeholder="请输入国家" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="产区" prop="region">
              <el-input v-model="form.region" placeholder="请输入产区" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="年份" prop="vintage">
              <el-input-number v-model="form.vintage" :min="1900" :max="2030" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="类型" prop="category">
              <el-select v-model="form.category" placeholder="请选择类型" style="width: 100%;">
                <el-option v-for="cat in categories" :key="cat.value" :label="cat.label" :value="cat.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="葡萄品种" prop="grape_variety">
              <el-input v-model="form.grape_variety" placeholder="请输入葡萄品种" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="酒精度(%)" prop="alcohol_content">
              <el-input-number v-model="form.alcohol_content" :min="0" :max="100" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="容量(L)" prop="bottle_size">
              <el-input-number v-model="form.bottle_size" :min="0" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="数量(瓶)" prop="quantity">
              <el-input-number v-model="form.quantity" :min="1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="酒窖位置" prop="cellar_location">
              <el-input v-model="form.cellar_location" placeholder="请输入酒窖位置" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="购买日期" prop="purchase_date">
              <el-date-picker
                v-model="form.purchase_date"
                type="date"
                placeholder="请选择购买日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="购买价格(元)" prop="purchase_price">
              <el-input-number v-model="form.purchase_price" :min="0" :step="100" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="当前估值(元)" prop="current_value">
              <el-input-number v-model="form.current_value" :min="0" :step="100" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="适饮期开始年份" prop="drinking_window_start">
              <el-input-number v-model="form.drinking_window_start" :min="1900" :max="2100" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="适饮期结束年份" prop="drinking_window_end">
              <el-input-number v-model="form.drinking_window_end" :min="1900" :max="2100" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="品鉴笔记" prop="tasting_notes">
          <el-input v-model="form.tasting_notes" type="textarea" :rows="3" placeholder="请输入品鉴笔记" />
        </el-form-item>

        <el-form-item label="存储笔记" prop="storage_notes">
          <el-input v-model="form.storage_notes" type="textarea" :rows="3" placeholder="请输入存储笔记" />
        </el-form-item>

        <el-form-item label="图片链接" prop="image_url">
          <el-input v-model="form.image_url" placeholder="请输入图片链接(可选)" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createWine } from '@/api/collection'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const categories = [
  { value: 'red', label: '红葡萄酒' },
  { value: 'white', label: '白葡萄酒' },
  { value: 'rose', label: '桃红葡萄酒' },
  { value: 'sparkling', label: '起泡酒' },
  { value: 'dessert', label: '甜酒' },
  { value: 'fortified', label: '加强酒' },
]

const form = reactive({
  name: '',
  chateau: '',
  country: '',
  region: '',
  vintage: new Date().getFullYear(),
  category: '',
  grape_variety: '',
  alcohol_content: 13.5,
  bottle_size: 0.75,
  quantity: 1,
  purchase_date: '',
  purchase_price: 0,
  current_value: 0,
  cellar_location: '',
  drinking_window_start: new Date().getFullYear(),
  drinking_window_end: new Date().getFullYear() + 10,
  tasting_notes: '',
  storage_notes: '',
  image_url: '',
})

const rules = {
  name: [{ required: true, message: '请输入酒品名称', trigger: 'blur' }],
  chateau: [{ required: true, message: '请输入酒庄名称', trigger: 'blur' }],
  country: [{ required: true, message: '请输入国家', trigger: 'blur' }],
  region: [{ required: true, message: '请输入产区', trigger: 'blur' }],
  vintage: [{ required: true, message: '请输入年份', trigger: 'blur' }],
  category: [{ required: true, message: '请选择类型', trigger: 'change' }],
  grape_variety: [{ required: true, message: '请输入葡萄品种', trigger: 'blur' }],
  alcohol_content: [{ required: true, message: '请输入酒精度', trigger: 'blur' }],
  bottle_size: [{ required: true, message: '请输入容量', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  purchase_date: [{ required: true, message: '请选择购买日期', trigger: 'change' }],
  purchase_price: [{ required: true, message: '请输入购买价格', trigger: 'blur' }],
  current_value: [{ required: true, message: '请输入当前估值', trigger: 'blur' }],
  cellar_location: [{ required: true, message: '请输入酒窖位置', trigger: 'blur' }],
  drinking_window_start: [{ required: true, message: '请输入适饮期开始年份', trigger: 'blur' }],
  drinking_window_end: [{ required: true, message: '请输入适饮期结束年份', trigger: 'blur' }],
}

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }

  submitting.value = true
  try {
    await createWine(form)
    ElMessage.success('酒品添加成功')
    router.push('/collection')
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
</style>
