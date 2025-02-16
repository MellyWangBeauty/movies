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
    </div>
    <div class="header-right">
      <div>
        <el-input
          v-model="input3"
          style="max-width: 600px"
          placeholder="请输入关键字"
          class="input-with-select"
        >
          <template #append>
            <el-button :icon="Search" />
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
    </div>

    <!-- 登录注册弹框 -->
    <LoginDialog v-model:visible="loginDialogVisible" :initial-mode="dialogMode" />
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

    .search-input {
      width: 240px;
      height: 25px;
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
  }
}

.el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>

<script setup>
import { ref } from "vue";
import { UserFilled, User, SwitchButton, Key, Plus } from "@element-plus/icons-vue";
import { Search } from "@element-plus/icons-vue";
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import LoginDialog from './LoginDialog.vue'

const router = useRouter()
const userStore = useUserStore()
const loginDialogVisible = ref(false)
const input3 = ref('')
const dialogMode = ref('login')

const goToUserCenter = () => {
  router.push('/user-center')
}

const handleLogout = async () => {
  try {
    await userStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.message || '退出登录失败')
  }
}

const handleLogin = () => {
  dialogMode.value = 'login'
  loginDialogVisible.value = true
}

const handleRegister = () => {
  dialogMode.value = 'register'
  loginDialogVisible.value = true
}
</script>
