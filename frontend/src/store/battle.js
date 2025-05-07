import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getRandomPoetry, checkPoetryChain, createBattle, updateBattle, getSeasonRankings } from '@/api/battle'
import { ElMessage } from 'element-plus'

export const useBattleStore = defineStore('battle', () => {
  const currentBattle = ref(null)
  const currentPoetry = ref(null)
  const battleHistory = ref([])
  const currentScore = ref(0)
  const winStreak = ref(0)
  const highScore = ref(0)
  const loading = ref(false)
  const submitting = ref(false)

  // 计算属性
  const isInBattle = computed(() => !!currentBattle.value)
  const canSubmit = computed(() => !!currentPoetry.value && !submitting.value)

  // 开始新对战
  const startNewBattle = async () => {
    try {
      loading.value = true
      const battle = await createBattle()
      currentBattle.value = battle
      await getNewPoetry()
      battleHistory.value = []
      currentScore.value = 0
      winStreak.value = 0
      return true
    } catch (error) {
      console.error('Failed to start battle:', error)
      ElMessage.error('开始对战失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取新诗句
  const getNewPoetry = async () => {
    try {
      const poetry = await getRandomPoetry()
      currentPoetry.value = poetry
      return poetry
    } catch (error) {
      console.error('Failed to get poetry:', error)
      ElMessage.error('获取诗句失败')
      throw error
    }
  }

  // 提交诗句
  const submitPoetry = async (poetry) => {
    if (!currentPoetry.value || !poetry) return false
    
    try {
      submitting.value = true
      const { can_chain, chain_type } = await checkPoetryChain(
        currentPoetry.value.content,
        poetry
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
          content: poetry,
          info: `接龙成功！${chain_type}，得分：${score}`
        })
        
        await updateBattle(currentBattle.value.id, {
          score: currentScore.value,
          status: 'win'
        })
        
        await getNewPoetry()
        return true
      } else {
        winStreak.value = 0
        battleHistory.value.unshift({
          type: 'danger',
          color: '#F56C6C',
          content: poetry,
          info: '接龙失败，请重试'
        })
        return false
      }
    } catch (error) {
      console.error('Failed to submit poetry:', error)
      ElMessage.error('提交失败，请重试')
      return false
    } finally {
      submitting.value = false
    }
  }

  // 计算得分
  const calculateScore = (chainType) => {
    const baseScore = 10
    const streakBonus = Math.min(winStreak.value, 5)
    const typeBonus = chainType === '首尾字接龙' ? 2 : 1
    return baseScore * typeBonus * (1 + streakBonus * 0.2)
  }

  // 获取赛季排行榜
  const getRankings = async (seasonId, limit = 10) => {
    try {
      const response = await getSeasonRankings(seasonId, limit)
      return response
    } catch (error) {
      console.error('Failed to get rankings:', error)
      ElMessage.error('获取排行榜失败')
      throw error
    }
  }

  // 结束对战
  const endBattle = () => {
    currentBattle.value = null
    currentPoetry.value = null
    battleHistory.value = []
    currentScore.value = 0
    winStreak.value = 0
  }

  return {
    currentBattle,
    currentPoetry,
    battleHistory,
    currentScore,
    winStreak,
    highScore,
    loading,
    submitting,
    isInBattle,
    canSubmit,
    startNewBattle,
    getNewPoetry,
    submitPoetry,
    getRankings,
    endBattle
  }
}) 