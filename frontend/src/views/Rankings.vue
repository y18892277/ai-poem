<template>
  <div class="rankings-container">
    <el-card class="rankings-card">
      <template #header>
        <div class="card-header">
          <h2>诗词擂台排行榜</h2>
          <div class="header-actions">
            <el-select v-model="selectedSeason" placeholder="选择赛季" @change="fetchRankings" style="margin-right: 10px;">
              <el-option
                v-for="season in seasons"
                :key="season.id"
                :label="season.name"
                :value="season.id"
              />
            </el-select>
            <el-button type="primary" @click="handleCreateNewSeason">创建新赛季</el-button>
          </div>
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
    const response = await fetch(`/api/v1/rankings?season=${selectedSeason.value}&page=${currentPage.value}&pageSize=${pageSize.value}`)
    const data = await response.json()
    
    if (data.success) {
      rankings.value = data.rankings
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
    const response = await fetch('/api/v1/seasons'); 
    if (!response.ok) {
      throw new Error(`获取赛季数据失败: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    
    if (Array.isArray(data)) {
      seasons.value = data;
      if (seasons.value.length > 0) {
        const activeSeason = seasons.value.find(s => s.status === 'active');
        if (activeSeason) {
            selectedSeason.value = activeSeason.id;
        } else if (seasons.value.length > 0) {
            selectedSeason.value = seasons.value[0].id;
        }
        if (selectedSeason.value) {
            fetchRankings();
        }
      } else {
        ElMessage.info('暂无赛季数据');
      }
    } else {
      console.error('获取到的赛季数据格式不正确:', data);
      ElMessage.error('获取到的赛季数据格式不正确');
    }
  } catch (error) {
    console.error('获取赛季数据出错 (catch block)：', error);
    ElMessage.error(error.message || '获取赛季数据时发生网络或解析错误');
  }
};

// 新增：创建新赛季的处理函数
const handleCreateNewSeason = async () => {
  try {
    loading.value = true; // 可以用一个独立的loading状态，或者共用
    const response = await fetch('/api/v1/seasons', {
      method: 'POST',
      headers: {
        // 如果需要认证，请添加 Authorization header
        // 'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      // body: JSON.stringify({}) // POST请求通常需要body，但此接口设计为不需要
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: '创建新赛季失败，请稍后再试' }));
      throw new Error(errorData.detail || `创建新赛季失败: ${response.status}`);
    }

    const newSeason = await response.json();
    ElMessage.success(`新赛季 "${newSeason.name}" 创建成功并已激活！`);
    
    // 刷新赛季列表并选中新赛季
    await fetchSeasons(); // fetchSeasons 内部会自动选中 active 的赛季
    // selectedSeason.value = newSeason.id; // fetchSeasons 应该会处理这个
    // fetchRankings(); // fetchSeasons 内部在选中赛季后会调用 fetchRankings

  } catch (error) {
    console.error('创建新赛季出错：', error);
    ElMessage.error(error.message || '创建新赛季时发生错误');
  } finally {
    loading.value = false;
  }
};

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

.header-actions {
  display: flex;
  align-items: center;
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