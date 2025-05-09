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
    return now >= new Date(currentSeason.value.start_date) && 
           now <= new Date(currentSeason.value.end_date)
  })

  // 获取赛季列表
  const fetchSeasonList = async () => {
    try {
      loading.value = true
      const response = await fetch('/api/v1/seasons')
      if (!response.ok) throw new Error('获取赛季列表失败')
      const data = await response.json()
      seasonList.value = Array.isArray(data) ? data : (data.data || [])
      return seasonList.value
    } catch (error) {
      console.error('Failed to fetch season list:', error)
      ElMessage.error(error.message || '获取赛季列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取当前赛季 (now fetches all and filters)
  const fetchCurrentSeason = async () => {
    try {
      loading.value = true
      // Call fetchSeasonList to ensure seasonList is populated and get all seasons
      const allSeasons = seasonList.value.length ? seasonList.value : await fetchSeasonList()
      
      const activeSeason = allSeasons.find(season => season.status === 'active')
      
      if (activeSeason) {
        currentSeason.value = activeSeason
      } else {
        currentSeason.value = null // Or handle as needed, e.g., pick the latest if none active
        console.warn('No active season found.')
        // Optionally, if no active season, pick the most recent one based on start_date or id
        if (allSeasons.length > 0) {
            // Example: pick the one with the largest ID or latest start_date
            // currentSeason.value = [...allSeasons].sort((a, b) => b.id - a.id)[0]
        }
      }
      return currentSeason.value
    } catch (error) {
      console.error('Failed to fetch and determine current season:', error)
      ElMessage.error(error.message || '获取当前赛季失败')
      currentSeason.value = null
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取赛季排行榜
  const fetchRankings = async (seasonId, limit = 10) => {
    try {
      loading.value = true
      // Ensure getSeasonRankings API call is correct and handles token if needed
      const data = await getSeasonRankings(seasonId, limit) 
      rankings.value = data.rankings || data // Adjust if response structure is { success: bool, rankings: [] }
      return rankings.value
    } catch (error) {
      console.error('Failed to fetch rankings:', error)
      ElMessage.error(error.message || '获取排行榜失败')
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