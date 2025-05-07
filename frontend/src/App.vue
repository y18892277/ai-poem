<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <el-header>
          <nav-header />
        </el-header>
        <el-main>
          <router-view />
        </el-main>
        <el-footer>
          <nav-footer />
        </el-footer>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import NavHeader from '@/components/NavHeader.vue'
import NavFooter from '@/components/NavFooter.vue'
</script>

<style>
.app-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.el-header {
  padding: 0;
  height: auto !important;
}

.el-main {
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.el-footer {
  padding: 20px;
  text-align: center;
  color: #909399;
}
</style> 