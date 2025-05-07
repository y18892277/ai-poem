<template>
  <div class="nav-header">
    <el-menu
      :default-active="activeIndex"
      mode="horizontal"
      router
      class="nav-menu"
    >
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/battle">对战</el-menu-item>
      <el-menu-item index="/rankings">排行榜</el-menu-item>
      <el-menu-item index="/poetry">诗词库</el-menu-item>
      
      <div class="nav-right">
        <template v-if="isLoggedIn">
          <el-menu-item index="/profile">
            <el-avatar :size="32" :src="userInfo?.avatar">
              {{ username.charAt(0).toUpperCase() }}
            </el-avatar>
            <span class="username">{{ username }}</span>
          </el-menu-item>
          <el-menu-item @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出
          </el-menu-item>
        </template>
        <template v-else>
          <el-menu-item index="/login">登录</el-menu-item>
          <el-menu-item index="/register">注册</el-menu-item>
        </template>
      </div>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeIndex = computed(() => route.path)
const isLoggedIn = computed(() => userStore.isLoggedIn)
const username = computed(() => userStore.username)
const userInfo = computed(() => userStore.userInfo)

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('退出成功')
  router.push('/login')
}
</script>

<style scoped>
.nav-header {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-menu {
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
}

.nav-right {
  display: flex;
  align-items: center;
}

.username {
  margin-left: 8px;
}

.el-avatar {
  background-color: #409EFF;
  color: #fff;
  font-weight: bold;
}
</style> 