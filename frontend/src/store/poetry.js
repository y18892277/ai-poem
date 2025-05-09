import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getPoetryList, getPoetryDetail } from '../api/poetry'

export const usePoetryStore = defineStore('poetry', () => {
  const poetryList = ref([])
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
      // Ensure only known and valid parameters are sent for the list view
      const requestParams = {
        page,
        pageSize: 10,
      };
      if (params.keyword && typeof params.keyword === 'string' && params.keyword.trim() !== '') {
        requestParams.keyword = params.keyword.trim();
      }
      if (params.dynasty && typeof params.dynasty === 'string' && params.dynasty.trim() !== '') {
        requestParams.dynasty = params.dynasty.trim();
      }
      if (params.type && typeof params.type === 'string' && params.type.trim() !== '') {
        requestParams.type = params.type.trim();
      }
      // Only add wordCount if it's a positive number.
      // Backend should ideally handle null/0 as "don't filter".
      if (params.wordCount && typeof params.wordCount === 'number' && params.wordCount > 0) { 
        requestParams.wordCount = params.wordCount;
      }

      const response = await getPoetryList(requestParams) // Use the cleaned requestParams
      
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
    resetSearch
  }
}) 