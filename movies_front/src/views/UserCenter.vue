<template>
  <div class="user-center">
    <el-card class="user-info">
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
          <el-button type="primary" @click="handleEdit">编辑</el-button>
        </div>
      </template>
      <div class="avatar-container">
        <el-avatar
          :size="100"
          :src="userStore.userInfo?.avatar"
          :icon="UserFilled"
        />
        <el-upload
          v-if="isEditing"
          class="avatar-uploader"
          action="/api/upload"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
        >
          <el-button size="small">更换头像</el-button>
        </el-upload>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :disabled="!isEditing"
        label-width="100px"
      >
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input
            v-model="form.bio"
            type="textarea"
            :rows="4"
            placeholder="写点什么吧..."
          />
        </el-form-item>
        <el-form-item v-if="isEditing">
          <el-button type="primary" @click="handleSave">保存</el-button>
          <el-button @click="cancelEdit">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="user-stats">
      <template #header>
        <div class="card-header">
          <span>我的数据</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item">
            <h3>收藏电影</h3>
            <p>{{ userStats.favorites || 0 }}</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <h3>评论数</h3>
            <p>{{ userStats.comments || 0 }}</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <h3>评分数</h3>
            <p>{{ userStats.ratings || 0 }}</p>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const isEditing = ref(false)
const formRef = ref(null)

const form = reactive({
  username: '',
  email: '',
  bio: ''
})

const userStats = reactive({
  favorites: 0,
  comments: 0,
  ratings: 0
})

// 初始化表单数据
const initForm = () => {
  const userInfo = userStore.userInfo
  if (userInfo) {
    form.username = userInfo.username
    form.email = userInfo.email
    form.bio = userInfo.bio || ''
  }
}

// 编辑个人信息
const handleEdit = () => {
  isEditing.value = true
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  initForm()
}

// 保存个人信息
const handleSave = async () => {
  try {
    await userStore.updateUserInfo(form)
    isEditing.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error(error.message || '保存失败')
  }
}

// 上传头像成功
const handleAvatarSuccess = (response) => {
  userStore.updateUserInfo({ avatar: response.url })
}

// 获取用户统计数据
const fetchUserStats = async () => {
  try {
    // TODO: 实现获取用户统计数据的API
    // const stats = await userStore.getUserStats()
    // Object.assign(userStats, stats)
  } catch (error) {
    console.error('获取用户统计数据失败:', error)
  }
}

onMounted(() => {
  initForm()
  fetchUserStats()
})
</script>

<style scoped>
.user-center {
  max-width: 1000px;
  margin: 20px auto;
  padding: 0 20px;
}

.user-info {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-container {
  text-align: center;
  margin-bottom: 20px;
}

.avatar-uploader {
  margin-top: 10px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-item h3 {
  margin: 0;
  font-size: 16px;
  color: #606266;
}

.stat-item p {
  margin: 10px 0 0;
  font-size: 24px;
  color: #409eff;
  font-weight: bold;
}
</style> 