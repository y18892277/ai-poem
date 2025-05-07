<template>
  <div class="battle-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="battle-card">
          <template #header>
            <div class="battle-header">
              <h2>诗词接龙对战</h2>
              <el-button type="primary" @click="startNewBattle" :loading="loading">
                开始新对战
              </el-button>
            </div>
          </template>
          
          <div class="battle-content">
            <div v-if="currentPoetry" class="poetry-display">
              <h3>当前诗句</h3>
              <p class="poetry-text">{{ currentPoetry.content }}</p>
              <p class="poetry-info">
                {{ currentPoetry.dynasty }} · {{ currentPoetry.author }} · {{ currentPoetry.title }}
              </p>
            </div>
            
            <div class="input-area">
              <el-input
                v-model="userInput"
                type="textarea"
                :rows="3"
                placeholder="请输入接龙诗句"
                :disabled="!currentPoetry"
              />
              <el-button
                type="primary"
                @click="submitPoetry"
                :disabled="!currentPoetry || !userInput"
                :loading="submitting"
              >
                提交
              </el-button>
            </div>
            
            <div v-if="battleHistory.length > 0" class="battle-history">
              <h3>对战历史</h3>
              <el-timeline>
                <el-timeline-item
                  v-for="(item, index) in battleHistory"
                  :key="index"
                  :type="item.type"
                  :color="item.color"
                >
                  <p class="history-text">{{ item.content }}</p>
                  <p class="history-info">{{ item.info }}</p>
                </el-timeline-item>
              </el-timeline>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stats-card">
          <template #header>
            <h3>对战统计</h3>
          </template>
          
          <div class="stats-content">
            <div class="stat-item">
              <span class="stat-label">当前得分</span>
              <span class="stat-value">{{ currentScore }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">连胜次数</span>
              <span class="stat-value">{{ winStreak }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最高得分</span>
              <span class="stat-value">{{ highScore }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getRandomPoetry, checkPoetryChain, createBattle, updateBattle } from '@/api/battle'

const loading = ref(false)
const submitting = ref(false)
const currentPoetry = ref(null)
const userInput = ref('')
const battleHistory = ref([])
const currentScore = ref(0)
const winStreak = ref(0)
const highScore = ref(0)
const currentBattleId = ref(null)

const startNewBattle = async () => {
  try {
    loading.value = true
    const battle = await createBattle()
    currentBattleId.value = battle.id
    await getNewPoetry()
    battleHistory.value = []
    currentScore.value = 0
    winStreak.value = 0
  } catch (error) {
    console.error('Failed to start battle:', error)
  } finally {
    loading.value = false
  }
}

const getNewPoetry = async () => {
  try {
    const poetry = await getRandomPoetry()
    currentPoetry.value = poetry
    userInput.value = ''
  } catch (error) {
    console.error('Failed to get poetry:', error)
  }
}

const submitPoetry = async () => {
  if (!currentPoetry.value || !userInput.value) return
  
  try {
    submitting.value = true
    const { can_chain, chain_type } = await checkPoetryChain(
      currentPoetry.value.content,
      userInput.value
    )
    
    if (can_chain) {
      const score = calculateScore(chain_type)
      currentScore.value += score
      winStreak.value++
      
      if (currentScore.value > highScore.value) {
        highScore.value = currentScore.value
      }
      
      battleHistory.value.unshift({
        type: 'success',
        color: '#67C23A',
        content: userInput.value,
        info: `接龙成功！${chain_type}，得分：${score}`
      })
      
      await updateBattle(currentBattleId.value, {
        score: currentScore.value,
        status: 'win'
      })
      
      await getNewPoetry()
    } else {
      winStreak.value = 0
      battleHistory.value.unshift({
        type: 'danger',
        color: '#F56C6C',
        content: userInput.value,
        info: '接龙失败，请重试'
      })
    }
  } catch (error) {
    console.error('Failed to submit poetry:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

const calculateScore = (chainType) => {
  const baseScore = 10
  const streakBonus = Math.min(winStreak.value, 5)
  const typeBonus = chainType === '首尾字接龙' ? 2 : 1
  return baseScore * typeBonus * (1 + streakBonus * 0.2)
}

onMounted(() => {
  startNewBattle()
})
</script>

<style scoped>
.battle-container {
  padding: 20px;
}

.battle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.battle-header h2 {
  margin: 0;
}

.battle-content {
  margin-top: 20px;
}

.poetry-display {
  text-align: center;
  margin-bottom: 30px;
}

.poetry-text {
  font-size: 24px;
  color: #303133;
  margin: 10px 0;
}

.poetry-info {
  color: #909399;
  font-size: 14px;
}

.input-area {
  margin: 20px 0;
  text-align: center;
}

.input-area .el-button {
  margin-top: 10px;
}

.battle-history {
  margin-top: 30px;
}

.history-text {
  font-size: 16px;
  margin: 5px 0;
}

.history-info {
  color: #909399;
  font-size: 14px;
}

.stats-content {
  padding: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}
</style> 