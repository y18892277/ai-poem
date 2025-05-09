import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getRankings, getSeasons, createSeason } from '../api/rankings'
import { ElMessage } from 'element-plus'

export const useRankingsStore = defineStore('rankings', () => {
  // 状态
  const rankings = ref([])
  const seasons = ref([])
  const currentSeason = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0
  })

  // 计算属性
  const sortedRankings = computed(() => {
    return rankings.value.sort((a, b) => b.score - a.score)
  })

  const currentSeasonName = computed(() => {
    return currentSeason.value?.name || '当前赛季'
  })

  // 方法
  const fetchRankings = async (seasonId = null) => {
    try {
      loading.value = true
      error.value = null
      const { data, total } = await getRankings({
        seasonId,
        page: pagination.value.page,
        pageSize: pagination.value.pageSize
      })
      rankings.value = data
      pagination.value.total = total
    } catch (err) {
      error.value = '获取排行榜数据失败'
      console.error('获取排行榜失败:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchSeasons = async () => {
    try {
      const data = await getSeasons()
      seasons.value = data
      if (data.length > 0) {
        currentSeason.value = data[0]
      }
    } catch (err) {
      console.error('获取赛季列表失败:', err)
    }
  }

  const addNewSeason = async (seasonData) => {
    try {
      const newSeason = await createSeason(seasonData)
      seasons.value.unshift(newSeason)
      currentSeason.value = newSeason
      return newSeason
    } catch (err) {
      console.error('创建新赛季失败:', err)
      throw err
    }
  }

  const setCurrentSeason = (season) => {
    currentSeason.value = season
    fetchRankings(season?.id)
  }

  const updatePagination = (newPagination) => {
    pagination.value = { ...pagination.value, ...newPagination }
    fetchRankings(currentSeason.value?.id)
  }

  return {
    // 状态
    rankings,
    seasons,
    currentSeason,
    loading,
    error,
    pagination,
    
    // 计算属性
    sortedRankings,
    currentSeasonName,
    
    // 方法
    fetchRankings,
    fetchSeasons,
    addNewSeason,
    setCurrentSeason,
    updatePagination
  }
}) 