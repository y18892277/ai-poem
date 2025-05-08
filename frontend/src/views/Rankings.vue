<template>
  <div class="rankings-container">
    <el-card class="rankings-card">
      <template #header>
        <div class="card-header">
          <h2>诗词擂台排行榜</h2>
          <el-select v-model="selectedSeason" placeholder="选择赛季" @change="fetchRankings">
            <el-option
              v-for="season in seasons"
              :key="season.id"
              :label="season.name"
              :value="season.id"
            />
          </el-select>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="rankings"
        style="width: 100%"
        :stripe="true"
        :border="true"
      >
        <el-table-column
          type="index"
          label="排名"
          width="80"
          align="center"
        />
        <el-table-column
          prop="username"
          label="用户名"
          width="180"
        >
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="30" :src="row.avatar">{{ row.username.charAt(0) }}</el-avatar>
              <span class="username">{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="score"
          label="积分"
          width="120"
          align="center"
          sortable
        />
        <el-table-column
          prop="winRate"
          label="胜率"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-progress
              :percentage="row.winRate"
              :format="(val) => val + '%'"
              :stroke-width="10"
              :color="getWinRateColor(row.winRate)"
            />
          </template>
        </el-table-column>
        <el-table-column
          prop="totalBattles"
          label="对战场次"
          width="120"
          align="center"
        />
        <el-table-column
          prop="winCount"
          label="胜场"
          width="120"
          align="center"
        />
        <el-table-column
          prop="loseCount"
          label="负场"
          width="120"
          align="center"
        />
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 状态定义
const loading = ref(false)
const rankings = ref([])
const seasons = ref([])
const selectedSeason = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 获取排行榜数据
const fetchRankings = async () => {
  try {
    loading.value = true
    // TODO: 替换为实际的API调用
    const response = await fetch(`/api/rankings?season=${selectedSeason.value}&page=${currentPage.value}&pageSize=${pageSize.value}`)
    const data = await response.json()
    
    if (data.success) {
      rankings.value = data.rankings.map(user => ({
        ...user,
        winRate: user.totalBattles ? Math.round((user.winCount / user.totalBattles) * 100) : 0
      }))
      total.value = data.total
    } else {
      ElMessage.error('获取排行榜数据失败')
    }
  } catch (error) {
    console.error('获取排行榜数据出错：', error)
    ElMessage.error('获取排行榜数据出错')
  } finally {
    loading.value = false
  }
}

// 获取赛季列表
const fetchSeasons = async () => {
  try {
    // TODO: 替换为实际的API调用
    const response = await fetch('/api/seasons')
    const data = await response.json()
    
    if (data.success) {
      seasons.value = data.seasons
      if (seasons.value.length > 0) {
        selectedSeason.value = seasons.value[0].id
        fetchRankings()
      }
    } else {
      ElMessage.error('获取赛季数据失败')
    }
  } catch (error) {
    console.error('获取赛季数据出错：', error)
    ElMessage.error('获取赛季数据出错')
  }
}

// 根据胜率返回不同的颜色
const getWinRateColor = (winRate) => {
  if (winRate >= 80) return '#67C23A'
  if (winRate >= 60) return '#409EFF'
  if (winRate >= 40) return '#E6A23C'
  return '#F56C6C'
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchRankings()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchRankings()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchSeasons()
})
</script>

<style scoped>
.rankings-container {
  padding: 20px;
}

.rankings-card {
  min-height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  color: #606266;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 