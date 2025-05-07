import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getSeasonRankings } from '@/api/battle'
import { ElMessage } from 'element-plus'

export const useSeasonStore = defineStore('season', () => {
  const currentSeason = ref(null)
  const seasonList = ref([])
  const rankings = ref([])
  const loading = ref(false)

  // 计算属性
  const isSeasonActive = computed(() => {
    if (!currentSeason.value) return false
    const now = new Date()
    return now >= new Date(currentSeason.value.start_time) && 
           now <= new Date(currentSeason.value.end_time)
  })

  // 获取赛季列表
  const fetchSeasonList = async () => {
    try {
      loading.value = true
      const response = await fetch('/api/v1/season/list')
      if (!response.ok) throw new Error('获取赛季列表失败')
      const data = await response.json()
      seasonList.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch season list:', error)
      ElMessage.error('获取赛季列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取当前赛季
  const fetchCurrentSeason = async () => {
    try {
      loading.value = true
      const response = await fetch('/api/v1/season/current')
      if (!response.ok) throw new Error('获取当前赛季失败')
      const data = await response.json()
      currentSeason.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch current season:', error)
      ElMessage.error('获取当前赛季失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取赛季排行榜
  const fetchRankings = async (seasonId, limit = 10) => {
    try {
      loading.value = true
      const data = await getSeasonRankings(seasonId, limit)
      rankings.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch rankings:', error)
      ElMessage.error('获取排行榜失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 设置当前赛季
  const setCurrentSeason = (season) => {
    currentSeason.value = season
  }

  return {
    currentSeason,
    seasonList,
    rankings,
    loading,
    isSeasonActive,
    fetchSeasonList,
    fetchCurrentSeason,
    fetchRankings,
    setCurrentSeason
  }
}) 