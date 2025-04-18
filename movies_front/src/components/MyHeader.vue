<template>
  <div class="header">
    <div class="header-left">
      <div class="logo">
        <img src="@/assets/电影LOGO.svg" alt="" width="40" />
      </div>
      <router-link to="/">首页</router-link>
      <router-link to="/hot">热门</router-link>
      <router-link to="/rank">排行</router-link>
      <router-link to="/recommend">推荐</router-link>
      <router-link to="/statistics">统计</router-link>
      <router-link v-if="userStore.isSuperUser()" to="/admin">管理</router-link>
    </div>
    <div class="header-right">
      <div>
        <el-input
          v-model="searchKeyword"
          style="max-width: 600px"
          placeholder="请输入电影名称"
          class="input-with-select"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>
      <div class="avatar-container">
        <el-dropdown v-if="userStore.isLoggedIn()" trigger="hover">
          <el-avatar 
            :icon="UserFilled" 
            class="avatar logged-in" 
            :size="30" 
            :src="userStore.userInfo?.avatar"
          /> 
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="goToUserCenter">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-dropdown v-else trigger="hover">
          <el-avatar 
            :icon="UserFilled" 
            class="avatar logged-out" 
            :size="30"
          />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogin">
                <el-icon><Key /></el-icon>
                登录
              </el-dropdown-item>
              <el-dropdown-item @click="handleRegister">
                <el-icon><Plus /></el-icon>
                注册
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <div class="user-name">
        <span v-if="userStore.isLoggedIn()">{{ userStore.userInfo?.username }}</span>
        <span v-else class="not-logged">未登录</span>
      </div>
    </div>

    <!-- 登录注册弹框 -->
    <LoginDialog :visible="loginDialogVisible" @update:visible="loginDialogVisible = $event" :initial-mode="dialogMode" />
  </div>
</template>

<style lang="scss">
.header {
  margin: 0;
  display: flex;
  justify-content: space-between; // 使左右两部分分别靠左和靠右
  align-items: center; // 垂直居中对齐
  padding: 10px 100px; // 添加内边距
  color: #fff;
  background-color: #000;

  .header-left {
    display: flex;
    align-items: center;
    gap: 40px; // 使用 gap 设置子元素之间的间距

    // 设置 router-link 的默认样式
    a {
      color: white; // 字体颜色为白色
      text-decoration: none; // 去掉下划线
      font-size: 16px; // 默认字体大小
      transition: font-size 0.3s ease; // 添加字体大小变化的过渡效果
      cursor: pointer; // 设置鼠标光标为手型

      // 设置激活路由的样式（精确匹配）
      &.router-link-exact-active {
        font-size: 18px; // 激活时字体变大
        font-weight: bold; // 可以加粗
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 40px; // 使用 gap 设置子元素之间的间距
    height: 30px;

    .input-with-select {
      :deep(.el-input-group__append) {
        background-color: var(--el-color-primary);
        border-color: var(--el-color-primary);
        padding: 0 15px;
        
        .el-button {
          color: #fff;
          border: none;
          margin: 0;
          
          &:hover {
            color: #fff;
            background-color: var(--el-color-primary-light-3);
          }
        }
      }

      :deep(.el-input__wrapper) {
        background-color: rgba(255, 255, 255, 0.1);
        box-shadow: none;
        border: 1px solid transparent;

        &:hover, &.is-focus {
          background-color: rgba(255, 255, 255, 0.15);
          border-color: var(--el-color-primary);
        }

        .el-input__inner {
          color: #fff;
          &::placeholder {
            color: rgba(255, 255, 255, 0.7);
          }
        }
      }
    }

    .avatar-container {
      .avatar {
        cursor: pointer;
        transition: all 0.3s ease;

        &.logged-in {
          background-color: var(--el-color-primary);
          color: white;
          border: 2px solid white;
          
          &:hover {
            transform: scale(1.1);
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
          }
        }

        &.logged-out {
          background-color: rgba(255, 255, 255, 0.2);
          color: rgba(255, 255, 255, 0.7);
          border: 2px solid rgba(255, 255, 255, 0.3);

          &:hover {
            background-color: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
          }
        }
      }
    }

    .user-name {
      font-size: 14px;
      color: #fff;
      margin-left: -30px;

      .not-logged {
        color: rgba(255, 255, 255, 0.7);
      }
    }
  }
}

.el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.input-with-select {
  :deep(.el-input-group__append) {
    background-color: var(--el-color-primary);
    border-color: var(--el-color-primary);
    padding: 0 15px;
    
    .el-button {
      color: #fff;
      border: none;
      margin: 0;
      
      &:hover {
        color: #fff;
        background-color: var(--el-color-primary-light-3);
      }
    }
  }

  :deep(.el-input__wrapper) {
    background-color: rgba(255, 255, 255, 0.1);
    box-shadow: none;
    border: 1px solid transparent;

    &:hover, &.is-focus {
      background-color: rgba(255, 255, 255, 0.15);
      border-color: var(--el-color-primary);
    }

    .el-input__inner {
      color: #fff;
      &::placeholder {
        color: rgba(255, 255, 255, 0.7);
      }
    }
  }
}

:deep(.el-popper.el-autocomplete__popper) {
  background: rgba(45, 45, 45, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);

  .el-autocomplete-suggestion__wrap {
    background: transparent;

    .suggestion-item {
      padding: 8px 0;
      cursor: pointer;

      .title {
        color: #fff;
        font-size: 14px;
        margin-bottom: 4px;
      }

      .info {
        color: #999;
        font-size: 12px;

        span {
          margin-right: 10px;
        }
      }
    }

    li {
      background: transparent;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }

      &.highlighted {
        background: rgba(255, 255, 255, 0.15);
      }
    }
  }
}
</style>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search, UserFilled } from '@element-plus/icons-vue'
import { User, Key, Plus, SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import LoginDialog from './LoginDialog.vue'

const router = useRouter()
const userStore = useUserStore()
const searchKeyword = ref('')
const loginDialogVisible = ref(false)
const dialogMode = ref('login')

const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  console.log('执行搜索:', searchKeyword.value.trim())  // 调试日志
  router.push({
    path: '/search',
    query: { keyword: searchKeyword.value.trim() }
  })
  searchKeyword.value = ''  // 清空搜索框
}

const handleLogin = () => {
  dialogMode.value = 'login'
  loginDialogVisible.value = true
}

const handleRegister = () => {
  dialogMode.value = 'register'
  loginDialogVisible.value = true
}

const handleLogout = async () => {
  try {
    await userStore.logout()
    ElMessage.success('退出登录成功')
    // 刷新当前页面
    window.location.reload()
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}

const goToUserCenter = () => {
  router.push('/user')
}
</script>
