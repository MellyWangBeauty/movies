<template>
  <div class="admin-container">
    <h1 style="text-align: center; color: #fff; padding-top: 20px">用户管理</h1>
    
    <table class="users-table">
      <thead>
        <tr>
          <th>用户ID</th>
          <th>用户名</th>
          <th>邮箱</th>
          <th>注册时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.email }}</td>
          <td>{{ formatDate(user.created_at) }}</td>
          <td class="actions">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(user)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(user)"
            >
              删除
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleViewReviews(user)"
            >
              查看评论
            </el-button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- 编辑用户信息对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户信息"
      width="30%"
    >
      <el-form 
        ref="editFormRef" 
        :model="editForm" 
        :rules="editRules" 
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit">确认</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 用户评论对话框 -->
    <el-dialog
      v-model="reviewsDialogVisible"
      :title="`${currentUser?.username} 的评论`"
      width="70%"
      class="reviews-dialog"
    >
      <div v-if="userReviews.length === 0" class="no-reviews">
        该用户暂无评论
      </div>
      <table v-else class="reviews-table">
        <thead>
          <tr>
            <th style="width: 15%">电影</th>
            <th style="width: 45%; text-align: left;">评论内容</th>
            <th style="width: 10%">评分</th>
            <th style="width: 20%">评论时间</th>
            <th style="width: 10%">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="review in userReviews" :key="review.id">
            <td>{{ review.movie_title }}</td>
            <td style="text-align: left;">{{ review.content }}</td>
            <td>
              <el-rate
                v-model="review.rating"
                disabled
                text-color="#ff9900"
              />
            </td>
            <td>{{ formatDate(review.created_at) }}</td>
            <td>
              <el-button
                type="danger"
                size="small"
                @click="handleDeleteReview(review)"
              >
                删除
              </el-button>
            </td>
          </tr>
        </tbody>
      </table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()
const users = ref([])
const editDialogVisible = ref(false)
const reviewsDialogVisible = ref(false)
const userReviews = ref([])
const currentUser = ref(null)

// 表单校验规则
const editRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 编辑表单
const editForm = reactive({
  id: '',
  username: '',
  email: ''
})

// 编辑表单引用
const editFormRef = ref(null)

// 页面加载时获取用户列表
onMounted(async () => {
  // 检查是否为管理员
  if (!userStore.isSuperUser()) {
    ElMessage.error('无权访问此页面')
    router.push('/')
    return
  }
  
  await fetchUsers()
})

// 获取所有用户
const fetchUsers = async () => {
  try {
    // 使用管理员API
    const response = await axios.get('/api/admin/users')
    users.value = response.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
    console.error(error)
  }
}

// 编辑用户
const handleEdit = (user) => {
  Object.assign(editForm, { ...user })
  editDialogVisible.value = true
}

// 提交编辑
const submitEdit = async () => {
  try {
    await editFormRef.value.validate()
    
    // 使用管理员API
    await axios.put(`/api/admin/users/${editForm.id}`, {
      username: editForm.username,
      email: editForm.email
    })
    
    ElMessage.success('编辑成功')
    editDialogVisible.value = false
    await fetchUsers()
  } catch (error) {
    ElMessage.error('编辑失败')
    console.error(error)
  }
}

// 删除用户
const handleDelete = (user) => {
  ElMessageBox.confirm(
    `确定要删除用户 ${user.username} 吗？此操作不可恢复！`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // 使用管理员API
      await axios.delete(`/api/admin/users/${user.id}`)
      ElMessage.success('删除成功')
      await fetchUsers()
    } catch (error) {
      console.error('删除用户错误:', error)
      // 显示更详细的错误信息
      const errorMsg = error.response?.data?.detail || '删除失败'
      ElMessage.error(`删除失败: ${errorMsg}`)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 查看用户评论
const handleViewReviews = async (user) => {
  currentUser.value = user
  try {
    // 使用管理员API
    const response = await axios.get(`/api/admin/users/${user.id}/reviews`)
    userReviews.value = response.data
    reviewsDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取用户评论失败')
    console.error(error)
  }
}

// 删除评论
const handleDeleteReview = (review) => {
  ElMessageBox.confirm(
    '确定要删除此评论吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // 使用管理员API
      await axios.delete(`/api/admin/reviews/${review.id}`)
      ElMessage.success('评论删除成功')
      // 重新获取评论列表
      const response = await axios.get(`/api/admin/users/${currentUser.value.id}/reviews`)
      userReviews.value = response.data
    } catch (error) {
      ElMessage.error('删除评论失败')
      console.error(error)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style lang="scss" scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 20px 20px;
  color: #fff;
  background-color: rgba(255, 255, 255, 0.02);
  width: 100%;
  box-sizing: border-box;
}

h1 {
  margin-bottom: 20px;
  font-size: 24px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

.no-reviews {
  text-align: center;
  padding: 20px;
  color: #999;
}

// 用户表格样式
.users-table {
  width: 96%;
  margin: 20px auto;
  border-collapse: collapse;
  border-radius: 12px;
  max-width: 1200px;
  text-align: center;

  thead {
    background-color: rgba(255, 255, 255, 0.03);
    color: #fff;

    th {
      padding: 10px;
      border-bottom: 2px solid rgba(255, 255, 255, 0.1);
      text-align: center;
    }
  }

  tbody {
    tr {
      background-color: rgba(255, 255, 255, 0.03);
      color: #fff;

      &:hover {
        background-color: rgba(70, 70, 70, 0.7);
      }

      td {
        padding: 10px;
        text-align: center;
      }
    }
  }

  .actions {
    display: flex;
    justify-content: center;
    gap: 8px;
  }
}

// 为评论表格添加特殊样式
.reviews-table {
  width: 96%;
  margin: 20px auto;
  border-collapse: collapse;
  border-radius: 12px;
  max-width: 1200px;
  text-align: center;
  
  thead {
    background-color: rgba(40, 40, 45, 0.8); // 更深的表头背景
    color: #fff;

    th {
      padding: 10px;
      border-bottom: 2px solid rgba(60, 60, 70, 0.5); // 更深的边框颜色
      text-align: center;
    }
  }

  tbody {
    tr {
      background-color: rgba(30, 30, 35, 0.8); // 更深的行背景
      color: #fff;

      &:hover {
        background-color: rgba(50, 50, 60, 0.8); // 更深的悬停颜色
      }

      td {
        padding: 10px;
        text-align: center;
        border-bottom: 1px solid rgba(60, 60, 70, 0.3); // 添加单元格底部边框
      }
    }
    
    // 交替行颜色
    tr:nth-child(even) {
      background-color: rgba(35, 35, 40, 0.8); // 偶数行稍浅一点
    }
  }

  .actions {
    display: flex;
    justify-content: center;
    gap: 8px;
  }
}

// 深色对话框样式
:deep(.reviews-dialog) {
  .el-dialog {
    background-color: rgba(25, 25, 30, 0.95);
    border: 1px solid rgba(60, 60, 70, 0.5);
    
    .el-dialog__header {
      color: #fff;
      border-bottom: 1px solid rgba(60, 60, 70, 0.5);
      padding-left: 30px;
      
      .el-dialog__title {
        color: #fff;
        font-size: 18px;
      }
    }
    
    .el-dialog__body {
      color: #fff;
      padding: 20px;
    }
    
    .el-dialog__headerbtn .el-dialog__close {
      color: #fff;
    }
  }
}
</style> 