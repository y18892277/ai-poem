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
  const fetchPoetryList = async (page = 1, pageSize = 10) => {
    try {
      loading.value = true
      const response = await fetch(`/v1/poetry/list?page=${page}&pageSize=${pageSize}`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || '获取诗词列表失败')
      }
      
      const data = await response.json()
      if (data.success) {
        poetryList.value = data.data
        totalPages.value = Math.ceil(data.total / pageSize)
        currentPage.value = page
      } else {
        throw new Error(data.message || '获取诗词列表失败')
      }
      return data
    } catch (error) {
      console.error('Failed to fetch poetry list:', error)
      ElMessage.error(error.message || '获取诗词列表失败')
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
      const response = await fetch(`/v1/poetry/list?keyword=${encodeURIComponent(query)}`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || '搜索诗词失败')
      }
      
      const data = await response.json()
      if (data.success) {
        poetryList.value = data.data
        totalPages.value = Math.ceil(data.total / 10)
        currentPage.value = 1
      } else {
        throw new Error(data.message || '搜索诗词失败')
      }
      return data
    } catch (error) {
      console.error('Failed to search poetry:', error)
      ElMessage.error(error.message || '搜索诗词失败')
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
      
      if (filters.keyword) queryParams.append('keyword', filters.keyword)
      if (filters.dynasty) queryParams.append('dynasty', filters.dynasty)
      if (filters.type) queryParams.append('type', filters.type)
      
      const response = await fetch(`/v1/poetry/list?${queryParams}`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || '高级搜索失败')
      }
      
      const data = await response.json()
      if (data.success) {
        poetryList.value = data.data
        totalPages.value = Math.ceil(data.total / 10)
        currentPage.value = 1
      } else {
        throw new Error(data.message || '高级搜索失败')
      }
      return data
    } catch (error) {
      console.error('Failed to perform advanced search:', error)
      ElMessage.error(error.message || '高级搜索失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取收藏列表
  const fetchFavorites = async () => {
    try {
      loading.value = true
      const response = await fetch('/v1/poetry/favorites')
      if (!response.ok) throw new Error('获取收藏列表失败')
      const data = await response.json()
      if (data.success) {
        favorites.value = data.data
      } else {
        throw new Error(data.message || '获取收藏列表失败')
      }
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
      const response = await fetch(`/v1/poetry/${poetryId}/favorite`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('添加收藏失败')
      const data = await response.json()
      if (data.success) {
        await fetchFavorites()
        ElMessage.success('添加收藏成功')
        return true
      } else {
        throw new Error(data.message || '添加收藏失败')
      }
    } catch (error) {
      console.error('Failed to add favorite:', error)
      ElMessage.error('添加收藏失败')
      return false
    }
  }

  // 取消收藏
  const removeFavorite = async (poetryId) => {
    try {
      const response = await fetch(`/v1/poetry/${poetryId}/favorite`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('取消收藏失败')
      const data = await response.json()
      if (data.success) {
        await fetchFavorites()
        ElMessage.success('取消收藏成功')
        return true
      } else {
        throw new Error(data.message || '取消收藏失败')
      }
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