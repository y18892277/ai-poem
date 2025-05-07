import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

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
  const fetchPoetryList = async (page = 1, limit = 10) => {
    try {
      loading.value = true
      const response = await fetch(`/api/v1/poetry/list?page=${page}&limit=${limit}`)
      if (!response.ok) throw new Error('获取诗词列表失败')
      const data = await response.json()
      poetryList.value = data.items
      totalPages.value = data.total_pages
      currentPage.value = page
      return data
    } catch (error) {
      console.error('Failed to fetch poetry list:', error)
      ElMessage.error('获取诗词列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 搜索诗词
  const searchPoetry = async (query) => {
    try {
      loading.value = true
      searchQuery.value = query
      const response = await fetch(`/api/v1/poetry/search?q=${encodeURIComponent(query)}`)
      if (!response.ok) throw new Error('搜索诗词失败')
      const data = await response.json()
      poetryList.value = data
      return data
    } catch (error) {
      console.error('Failed to search poetry:', error)
      ElMessage.error('搜索诗词失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 高级搜索
  const advancedSearch = async (filters) => {
    try {
      loading.value = true
      searchFilters.value = filters
      const queryParams = new URLSearchParams()
      
      if (filters.keyword) queryParams.append('q', filters.keyword)
      if (filters.dynasty) queryParams.append('dynasty', filters.dynasty)
      if (filters.type) queryParams.append('type', filters.type)
      if (filters.wordCount) queryParams.append('word_count', filters.wordCount)
      
      const response = await fetch(`/api/v1/poetry/advanced-search?${queryParams}`)
      if (!response.ok) throw new Error('高级搜索失败')
      const data = await response.json()
      poetryList.value = data
      return data
    } catch (error) {
      console.error('Failed to perform advanced search:', error)
      ElMessage.error('高级搜索失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取收藏列表
  const fetchFavorites = async () => {
    try {
      loading.value = true
      const response = await fetch('/api/v1/poetry/favorites')
      if (!response.ok) throw new Error('获取收藏列表失败')
      const data = await response.json()
      favorites.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch favorites:', error)
      ElMessage.error('获取收藏列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 添加收藏
  const addFavorite = async (poetryId) => {
    try {
      const response = await fetch(`/api/v1/poetry/favorites/${poetryId}`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('添加收藏失败')
      await fetchFavorites()
      ElMessage.success('添加收藏成功')
      return true
    } catch (error) {
      console.error('Failed to add favorite:', error)
      ElMessage.error('添加收藏失败')
      return false
    }
  }

  // 取消收藏
  const removeFavorite = async (poetryId) => {
    try {
      const response = await fetch(`/api/v1/poetry/favorites/${poetryId}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('取消收藏失败')
      await fetchFavorites()
      ElMessage.success('取消收藏成功')
      return true
    } catch (error) {
      console.error('Failed to remove favorite:', error)
      ElMessage.error('取消收藏失败')
      return false
    }
  }

  // 检查是否已收藏
  const isFavorite = (poetryId) => {
    return favorites.value.some(fav => fav.id === poetryId)
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
    isFavorite,
    resetSearch
  }
}) 