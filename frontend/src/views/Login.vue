<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>{{ isLogin ? '登录' : '注册' }}</h2>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        @submit.prevent
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="请输入密码"
          />
        </el-form-item>
        
        <template v-if="!isLogin">
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              show-password
              placeholder="请再次输入密码"
            />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="请输入邮箱" />
          </el-form-item>
          
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="form.nickname" placeholder="请输入昵称（选填）" />
          </el-form-item>
        </template>
        
        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ isLogin ? '登录' : '注册' }}
          </el-button>
          <el-button @click="toggleMode">
            切换到{{ isLogin ? '注册' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const isLogin = ref(true)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: '',
  nickname: ''
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    if (form.confirmPassword !== '') {
      formRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePass, trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validatePass2, trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  nickname: [
    { max: 20, message: '长度不能超过20个字符', trigger: 'blur' }
  ]
}

// frontend/src/views/Login.vue
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    if (isLogin.value) {
      // 登录逻辑
      const formData = new FormData()
      formData.append('username', form.username)
      formData.append('password', form.password)

      const response = await fetch('http://localhost:8000/api/v1/token', {
        method: 'POST',
        body: new URLSearchParams(formData),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || '登录失败')
      }

      const data = await response.json()
      
      // 存储 token
      localStorage.setItem('token', data.access_token)
      
      // 获取用户信息
      const userResponse = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      })
      
      if (!userResponse.ok) {
        throw new Error('获取用户信息失败')
      }
      
      const userData = await userResponse.json()
      localStorage.setItem('userInfo', JSON.stringify(userData))
      
      ElMessage.success('登录成功')
      router.push('/')  // 确保这里使用 router.push
    } else {
      // 注册逻辑
      const { confirmPassword, ...registerData } = form
      const response = await fetch('http://localhost:8000/api/v1/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(registerData)
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || '注册失败')
      }

      ElMessage.success('注册成功，请登录')
      isLogin.value = true
      form.password = ''
      form.confirmPassword = ''
    }
  } catch (error) {
    console.error('Operation failed:', error)
    ElMessage.error(error.message || '操作失败，请重试')
  } finally {
    loading.value = false
  }
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  form.password = ''
  form.confirmPassword = ''
  form.email = ''
  form.nickname = ''
  formRef.value?.clearValidate()
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--background-color);
}

.login-card {
  width: 100%;
  max-width: 500px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: var(--text-color);
}

.el-form {
  margin-top: 20px;
}

.el-button {
  margin-right: 10px;
}
</style> 