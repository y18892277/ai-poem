<template>
  <div class="poetry-library">
    <el-card class="search-card">
      <div class="search-header">
        <h2>诗词库</h2>
        <div class="search-container">
          <el-input
            v-model="searchQuery"
            placeholder="搜索诗词、作者或内容"
            class="search-input"
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="showAdvancedSearch = true">
            高级搜索
          </el-button>
        </div>
      </div>
    </el-card>

    <el-dialog
      v-model="showAdvancedSearch"
      title="高级搜索"
      width="500px"
    >
      <el-form :model="advancedSearch" label-width="80px">
        <el-form-item label="朝代">
          <el-select v-model="advancedSearch.dynasty" placeholder="选择朝代">
            <el-option
              v-for="dynasty in dynasties"
              :key="dynasty"
              :label="dynasty"
              :value="dynasty"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="advancedSearch.type" placeholder="选择类型">
            <el-option
              v-for="type in types"
              :key="type"
              :label="type"
              :value="type"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="字数">
          <el-input-number
            v-model="advancedSearch.wordCount"
            :min="1"
            :max="100"
            placeholder="输入字数"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdvancedSearch = false">取消</el-button>
        <el-button type="primary" @click="handleAdvancedSearch">
          搜索
        </el-button>
      </template>
    </el-dialog>

    <el-card class="poetry-list" v-loading="loading">
      <template v-if="filteredPoetry.length > 0">
        <div v-for="poetry in filteredPoetry" :key="poetry.id" class="poetry-item">
          <div class="poetry-content">
            <h3>{{ poetry.title }}</h3>
            <p class="author">作者：{{ poetry.author }} · {{ poetry.dynasty }}</p>
            <p class="content">{{ poetry.content }}</p>
            <div class="tags">
              <el-tag v-for="tag in poetry.tags" :key="tag" size="small">
                {{ tag }}
              </el-tag>
            </div>
          </div>
          <div class="poetry-actions">
            <el-button
              :type="isFavorite(poetry.id) ? 'danger' : 'default'"
              :icon="isFavorite(poetry.id) ? 'Star' : 'StarFilled'"
              @click="toggleFavorite(poetry.id)"
            >
              {{ isFavorite(poetry.id) ? '取消收藏' : '收藏' }}
            </el-button>
          </div>
        </div>
      </template>
      <el-empty v-else description="暂无诗词" />

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="10"
          :total="totalPages * 10"
          @current-change="handlePageChange"
          layout="prev, pager, next"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { usePoetryStore } from '@/store/poetry'
import { ElMessage } from 'element-plus'
import { debounce } from 'lodash-es'

const poetryStore = usePoetryStore()
const searchQuery = ref('')
const loading = ref(false)
const showAdvancedSearch = ref(false)
const advancedSearch = ref({
  dynasty: '',
  type: '',
  wordCount: null
})

const dynasties = ['先秦', '汉', '魏晋', '南北朝', '唐', '宋', '元', '明', '清']
const types = ['诗', '词', '曲', '赋', '文']

// 计算属性
const filteredPoetry = computed(() => poetryStore.filteredPoetry)
const currentPage = computed(() => poetryStore.currentPage)
const totalPages = computed(() => poetryStore.totalPages)

// 防抖搜索
const debouncedSearch = debounce((query) => {
  if (query) {
    poetryStore.searchPoetry(query)
  } else {
    poetryStore.fetchPoetryList(1)
  }
}, 300)

// 方法
const handleSearch = () => {
  debouncedSearch(searchQuery.value)
}

const handleAdvancedSearch = () => {
  const query = {
    ...advancedSearch.value,
    keyword: searchQuery.value
  }
  poetryStore.advancedSearch(query)
  showAdvancedSearch.value = false
}

const handlePageChange = (page) => {
  poetryStore.fetchPoetryList(page)
}

const toggleFavorite = async (poetryId) => {
  if (poetryStore.isFavorite(poetryId)) {
    await poetryStore.removeFavorite(poetryId)
  } else {
    await poetryStore.addFavorite(poetryId)
  }
}

const isFavorite = (poetryId) => poetryStore.isFavorite(poetryId)

// 生命周期钩子
onMounted(async () => {
  try {
    loading.value = true
    await Promise.all([
      poetryStore.fetchPoetryList(),
      poetryStore.fetchFavorites()
    ])
  } catch (error) {
    ElMessage.error('加载诗词库失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.poetry-library {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-container {
  display: flex;
  gap: 10px;
}

.search-input {
  width: 300px;
}

.poetry-list {
  min-height: 500px;
}

.poetry-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  border-bottom: 1px solid #eee;
  transition: all 0.3s ease;
}

.poetry-item:hover {
  background-color: #f5f7fa;
}

.poetry-item:last-child {
  border-bottom: none;
}

.poetry-content {
  flex: 1;
}

.poetry-content h3 {
  margin: 0 0 10px;
  color: #303133;
}

.author {
  color: #909399;
  margin: 5px 0;
}

.content {
  color: #606266;
  margin: 10px 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.tags {
  margin-top: 10px;
}

.tags .el-tag {
  margin-right: 8px;
}

.poetry-actions {
  margin-left: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}
</style> 
</style> 