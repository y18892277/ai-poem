<template>
  <div class="home-container">
    <!-- 顶部横幅 -->
    <div class="banner">
      <div class="banner-content">
        <h1>诗词接龙擂台赛</h1>
        <p class="subtitle">传承中华文化，品味诗词之美</p>
        <el-button type="primary" size="large" @click="$router.push('/battle')">
          开始对战
        </el-button>
      </div>
    </div>

    <!-- 游戏特色 -->
    <div class="features">
      <el-row :gutter="30">
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="feature-header">
                <el-icon :size="40"><Trophy /></el-icon>
                <h3>智能对战</h3>
              </div>
            </template>
            <div class="feature-content">
              <p>基于AI的智能对战系统，让您随时随地享受诗词接龙的乐趣</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="feature-header">
                <el-icon :size="40"><Medal /></el-icon>
                <h3>排行榜</h3>
              </div>
            </template>
            <div class="feature-content">
              <p>实时更新的排行榜，展示您的实力，激励您不断进步</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="feature-header">
                <el-icon :size="40"><Collection /></el-icon>
                <h3>诗词库</h3>
              </div>
            </template>
            <div class="feature-content">
              <p>海量诗词资源，涵盖各个朝代，让您畅游诗词海洋</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 最新动态 -->
    <div class="news">
      <el-card>
        <template #header>
          <div class="news-header">
            <h2>最新动态</h2>
            <el-button text>查看更多</el-button>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="(item, index) in news"
            :key="index"
            :timestamp="item.time"
            :type="item.type"
          >
            <h4>{{ item.title }}</h4>
            <p>{{ item.content }}</p>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>

    <!-- 快速入口 -->
    <div class="quick-access">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="quick-card" @click="$router.push('/battle')">
            <div class="quick-content">
              <el-icon :size="40"><Trophy /></el-icon>
              <div class="quick-info">
                <h3>开始对战</h3>
                <p>立即开始一场精彩的诗词接龙对战</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="quick-card" @click="$router.push('/rankings')">
            <div class="quick-content">
              <el-icon :size="40"><Medal /></el-icon>
              <div class="quick-info">
                <h3>查看排行</h3>
                <p>查看最新的排行榜，了解自己的排名</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Trophy, Medal, Collection } from '@element-plus/icons-vue'

const news = ref([
  {
    time: '2024-03-15',
    type: 'primary',
    title: '2024春季赛开始',
    content: '新赛季已经开始，快来参与诗词接龙对战，赢取丰厚奖励！'
  },
  {
    time: '2024-03-10',
    type: 'success',
    title: '新功能上线',
    content: '新增AI智能对战系统，让您的对战体验更加智能和有趣。'
  },
  {
    time: '2024-03-05',
    type: 'info',
    title: '诗词库更新',
    content: '诗词库新增1000首经典诗词，让您的对战更加丰富多彩。'
  }
])
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.banner {
  background: linear-gradient(135deg, #409EFF 0%, #36D1DC 100%);
  border-radius: 8px;
  padding: 60px 40px;
  margin-bottom: 40px;
  color: white;
  text-align: center;
}

.banner-content h1 {
  font-size: 48px;
  margin: 0 0 20px;
}

.banner-content .subtitle {
  font-size: 24px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.features {
  margin-bottom: 40px;
}

.feature-card {
  height: 100%;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.feature-header h3 {
  margin: 0;
  font-size: 20px;
}

.feature-content {
  color: #606266;
  line-height: 1.6;
}

.news {
  margin-bottom: 40px;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-header h2 {
  margin: 0;
}

.quick-access {
  margin-bottom: 40px;
}

.quick-card {
  cursor: pointer;
  transition: all 0.3s;
}

.quick-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
}

.quick-info h3 {
  margin: 0 0 10px;
  font-size: 18px;
}

.quick-info p {
  margin: 0;
  color: #909399;
}
</style> 