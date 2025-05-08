import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getPoetryList, getPoetryDetail, getFavorites, toggleFavorite } from '../api/poetry'

export const usePoetryStore = defineStore('poetry', () => {
  const poetryList = ref([])
  const favorites = ref([])
  const loading = ref(false)
  const searchQuery = ref('')
  const currentPage = ref(1)
  const totalPages = ref(1)
  const searchFilters = ref({
    dynasty: '',
    type: '',
    wordCount: null
  })

  // 计算属性
  const filteredPoetry = computed(() => {
    if (!searchQuery.value && !hasActiveFilters.value) return poetryList.value
    
    return poetryList.value.filter(poetry => {
      const matchesKeyword = !searchQuery.value || 
        poetry.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        poetry.content.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        poetry.author.toLowerCase().includes(searchQuery.value.toLowerCase())
      
      const matchesDynasty = !searchFilters.value.dynasty || 
        poetry.dynasty === searchFilters.value.dynasty
      
      const matchesType = !searchFilters.value.type || 
        poetry.type === searchFilters.value.type
      
      const matchesWordCount = !searchFilters.value.wordCount || 
        poetry.content.length === searchFilters.value.wordCount
      
      return matchesKeyword && matchesDynasty && matchesType && matchesWordCount
    })
  })

  const hasActiveFilters = computed(() => {
    return searchFilters.value.dynasty || 
           searchFilters.value.type || 
           searchFilters.value.wordCount
  })

  // 获取诗词列表
  const fetchPoetryList = async (page = 1, params = {}) => {
    try {
      loading.value = true
      const response = await getPoetryList({
        page,
        pageSize: 10,
        ...params
      })
      
      if (response.data.success) {
        poetryList.value = response.data.data
        totalPages.value = Math.ceil(response.data.total / 10)
        currentPage.value = page
      } else {
        throw new Error(response.data.message || '获取诗词列表失败')
      }
    } catch (error) {
      console.error('Failed to fetch poetry list:', error)
      ElMessage.error(error.message || '获取诗词列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取收藏列表
  const fetchFavorites = async () => {
    try {
      const response = await getFavorites()
      if (response.data.success) {
        favorites.value = response.data.data
      } else {
        throw new Error(response.data.message || '获取收藏列表失败')
      }
    } catch (error) {
      console.error('Failed to fetch favorites:', error)
      ElMessage.error(error.message || '获取收藏列表失败')
      throw error
    }
  }

  // 添加收藏
  const addFavorite = async (poetryId) => {
    try {
      const response = await toggleFavorite(poetryId)
      if (response.data.success) {
        const poetry = poetryList.value.find(p => p.id === poetryId)
        if (poetry) {
          favorites.value.push(poetry)
        }
        ElMessage.success('收藏成功')
        return true
      } else {
        throw new Error(response.data.message || '收藏失败')
      }
    } catch (error) {
      console.error('Failed to add favorite:', error)
      ElMessage.error(error.message || '收藏失败')
      return false
    }
  }

  // 取消收藏
  const removeFavorite = async (poetryId) => {
    try {
      const response = await toggleFavorite(poetryId)
      if (response.data.success) {
        favorites.value = favorites.value.filter(p => p.id !== poetryId)
        ElMessage.success('取消收藏成功')
        return true
      } else {
        throw new Error(response.data.message || '取消收藏失败')
      }
    } catch (error) {
      console.error('Failed to remove favorite:', error)
      ElMessage.error(error.message || '取消收藏失败')
      return false
    }
  }

  // 搜索诗词
  const searchPoetry = async (keyword) => {
    await fetchPoetryList(1, { keyword })
  }

  // 高级搜索
  const advancedSearch = async (params) => {
    await fetchPoetryList(1, params)
  }

  // 重置搜索
  const resetSearch = () => {
    searchQuery.value = ''
    searchFilters.value = {
      dynasty: '',
      type: '',
      wordCount: null
    }
    fetchPoetryList(1)
  }

  return {
    poetryList,
    favorites,
    loading,
    searchQuery,
    currentPage,
    totalPages,
    searchFilters,
    filteredPoetry,
    hasActiveFilters,
    fetchPoetryList,
    searchPoetry,
    advancedSearch,
    fetchFavorites,
    addFavorite,
    removeFavorite,
    isFavorite: (poetryId) => favorites.value.some(p => p.id === poetryId),
    resetSearch
  }
}) 