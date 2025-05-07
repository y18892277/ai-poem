<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="profile-card">
          <template #header>
            <div class="profile-header">
              <h2>个人信息</h2>
              <el-button type="primary" @click="showEditDialog = true">
                编辑资料
              </el-button>
            </div>
          </template>
          
          <div class="profile-content">
            <div class="avatar-container">
              <el-avatar :size="100" :src="userInfo.avatar">
                {{ userInfo.username?.[0] }}
              </el-avatar>
            </div>
            
            <div class="user-info">
              <div class="info-item">
                <span class="label">用户名</span>
                <span class="value">{{ userInfo.username }}</span>
              </div>
              <div class="info-item">
                <span class="label">昵称</span>
                <span class="value">{{ userInfo.nickname }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱</span>
                <span class="value">{{ userInfo.email }}</span>
              </div>
              <div class="info-item">
                <span class="label">注册时间</span>
                <span class="value">{{ formatDate(userInfo.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card class="stats-card">
          <template #header>
            <h3>对战统计</h3>
          </template>
          
          <div class="stats-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="stat-box">
                  <div class="stat-value">{{ userStats.total_battles }}</div>
                  <div class="stat-label">总对战次数</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-box">
                  <div class="stat-value">{{ userStats.win_rate }}%</div>
                  <div class="stat-label">胜率</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-box">
                  <div class="stat-value">{{ userStats.highest_streak }}</div>
                  <div class="stat-label">最高连胜</div>
                </div>
              </el-col>
            </el-row>
            
            <div class="chart-container">
              <div ref="chartRef" style="width: 100%; height: 300px"></div>
            </div>
          </div>
        </el-card>
        
        <el-card class="history-card">
          <template #header>
            <div class="history-header">
              <h3>对战历史</h3>
              <el-select v-model="timeRange" placeholder="选择时间范围" @change="handleTimeRangeChange">
                <el-option label="最近一周" value="week" />
                <el-option label="最近一月" value="month" />
                <el-option label="最近三月" value="quarter" />
                <el-option label="全部" value="all" />
              </el-select>
            </div>
          </template>
          
          <el-table :data="battleHistory" style="width: 100%" v-loading="loading">
            <el-table-column prop="date" label="日期" width="180" />
            <el-table-column prop="score" label="得分" width="120" sortable />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.status === 'win' ? 'success' : 'danger'">
                  {{ row.status === 'win' ? '胜利' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="chain_type" label="接龙类型" />
            <el-table-column prop="poetry" label="诗句" show-overflow-tooltip />
          </el-table>
          
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人资料"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="editForm"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="editForm.nickname" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            action="/api/v1/user/avatar"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
          >
            <img v-if="editForm.avatar" :src="editForm.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateProfile" :loading="updating">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const userStore = useUserStore()
const loading = ref(false)
const updating = ref(false)
const showEditDialog = ref(false)
const timeRange = ref('week')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const chartRef = ref(null)
let chart = null

const userInfo = ref({
  username: '',
  nickname: '',
  email: '',
  avatar: '',
  created_at: ''
})

const userStats = ref({
  total_battles: 0,
  win_rate: 0,
  highest_streak: 0
})

const battleHistory = ref([])

const editForm = reactive({
  nickname: '',
  email: '',
  avatar: ''
})

const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const initChart = () => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    const option = {
      title: {
        text: '得分趋势'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        data: [820, 932, 901, 934, 1290, 1330, 1320],
        type: 'line',
        smooth: true
      }]
    }
    chart.setOption(option)
  }
}

const handleTimeRangeChange = () => {
  currentPage.value = 1
  fetchBattleHistory()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchBattleHistory()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchBattleHistory()
}

const handleAvatarSuccess = (response) => {
  editForm.avatar = response.url
}

const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg'
  const isPNG = file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG && !isPNG) {
    ElMessage.error('头像只能是 JPG 或 PNG 格式!')
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
  }
  return (isJPG || isPNG) && isLt2M
}

const handleUpdateProfile = async () => {
  try {
    updating.value = true
    // 调用更新个人资料的API
    await userStore.updateProfile(editForm)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    fetchUserInfo()
  } catch (error) {
    console.error('Failed to update profile:', error)
  } finally {
    updating.value = false
  }
}

const fetchUserInfo = async () => {
  try {
    const info = await userStore.getUserInfo()
    userInfo.value = info
    editForm.nickname = info.nickname
    editForm.email = info.email
    editForm.avatar = info.avatar
  } catch (error) {
    console.error('Failed to fetch user info:', error)
  }
}

const fetchBattleHistory = async () => {
  try {
    loading.value = true
    // 调用获取对战历史的API
    const response = await userStore.getBattleHistory({
      timeRange: timeRange.value,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    battleHistory.value = response.data
    total.value = response.total
  } catch (error) {
    console.error('Failed to fetch battle history:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchUserInfo()
  await fetchBattleHistory()
  initChart()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-header h2 {
  margin: 0;
}

.profile-content {
  text-align: center;
}

.avatar-container {
  margin-bottom: 20px;
}

.user-info {
  text-align: left;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin: 15px 0;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.info-item .label {
  color: #606266;
}

.info-item .value {
  font-weight: bold;
}

.stats-content {
  padding: 20px;
}

.stat-box {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  color: #909399;
}

.chart-container {
  margin-top: 30px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header h3 {
  margin: 0;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.avatar-uploader {
  text-align: center;
}

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
}
</style> 