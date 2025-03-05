<template>
  <div class="user-center">
    <!-- <el-card class="user-info">
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
    </el-card> -->

    <!-- <el-card class="user-stats">
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
    </el-card> -->

    <div class="charts-container">
      <!-- 电影标签分布 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>观影标签分布</span>
          </div>
        </template>
        <div ref="tagsPieChart" class="chart"></div>
      </el-card>

      <!-- 电影年份分布 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>观影年份分布</span>
          </div>
        </template>
        <div ref="yearsBarChart" class="chart"></div>
      </el-card>

      <!-- 电影地区分布 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>观影地区分布</span>
          </div>
        </template>
        <div ref="countryBarChart" class="chart"></div>
      </el-card>
    </div>

    <!-- 用户评分电影列表 -->
    <el-card class="movie-reviews">
      <template #header>
        <div class="card-header">
          <span>我的影评</span>
        </div>
      </template>
      <el-table :data="userReviews" style="width: 100%">
        <el-table-column prop="movie_title" label="电影" width="200">
          <template #default="scope">
            <router-link 
              :to="'/movie/' + scope.row.movie_id" 
              class="movie-link"
            >
              {{ scope.row.movie_title }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="rating" label="评分" width="120">
          <template #default="scope">
            <el-rate
              v-model="scope.row.rating"
              disabled
              show-score
              text-color="#ff9900"
            />
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评价" />
        <el-table-column prop="created_at" label="评价时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 数据分析图表 -->
    
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import * as echarts from 'echarts'
import axios from 'axios'

const userStore = useUserStore()
const isEditing = ref(false)
const formRef = ref(null)
const userReviews = ref([])

// ECharts 实例引用
const tagsPieChart = ref(null)
const yearsBarChart = ref(null)
const countryBarChart = ref(null)

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

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取用户评论数据
const fetchUserReviews = async () => {
  try {
    const response = await axios.get('/api/reviews/users/me/reviews')
    userReviews.value = response.data
    await nextTick()
    initCharts(response.data)
  } catch (error) {
    console.error('获取用户评论失败:', error)
    ElMessage.error('获取评论数据失败')
  }
}

// 初始化图表
const initCharts = (reviews) => {
  // 处理数据
  const tagsData = processTagsData(reviews)
  const yearsData = processYearsData(reviews)
  const countryData = processCountryData(reviews)

  // 初始化饼图
  const pieChart = echarts.init(tagsPieChart.value)
  pieChart.setOption({
    title: {
      text: '电影标签分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: '65%',
      data: tagsData,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })

  // 初始化年份柱状图
  const yearsChart = echarts.init(yearsBarChart.value)
  yearsChart.setOption({
    title: {
      text: '年份分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: yearsData.map(item => item.name)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: yearsData.map(item => item.value),
      type: 'bar'
    }]
  })

  // 初始化地区横向柱状图
  const countryChart = echarts.init(countryBarChart.value)
  countryChart.setOption({
    title: {
      text: '地区分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    yAxis: {
      type: 'value'
    },
    xAxis: {
      type: 'category',
      data: countryData.map(item => item.name)
    },
    series: [{
      data: countryData.map(item => item.value),
      type: 'bar'
    }]
  })

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    pieChart.resize()
    yearsChart.resize()
    countryChart.resize()
  })
}

// 处理标签数据
const processTagsData = (reviews) => {
  const tagsCount = {}
  reviews.forEach(review => {
    const tags = review.tags.split('/')
    tags.forEach(tag => {
      tagsCount[tag] = (tagsCount[tag] || 0) + 1
    })
  })
  return Object.entries(tagsCount).map(([name, value]) => ({ name, value }))
}

// 处理年份数据
const processYearsData = (reviews) => {
  const yearsCount = {}
  reviews.forEach(review => {
    const year = review.year
    yearsCount[year] = (yearsCount[year] || 0) + 1
  })
  return Object.entries(yearsCount)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => a.name - b.name)
}

// 处理地区数据
const processCountryData = (reviews) => {
  const countryCount = {}
  reviews.forEach(review => {
    const country = review.country
    countryCount[country] = (countryCount[country] || 0) + 1
  })
  return Object.entries(countryCount)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
}

onMounted(() => {
  initForm()
  fetchUserReviews()
})
</script>

<style lang="scss" scoped>
.user-center {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.user-info {
  margin-bottom: 20px;
}

.movie-reviews {
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

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.chart-card {
  .chart {
    height: 300px;
  }
}

.movie-link {
  color: var(--el-color-primary);
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
}

:deep(.el-table) {
  background-color: transparent;
  
  .el-table__header-wrapper {
    th {
      background-color: var(--el-color-primary-light-9);
    }
  }
  
  .el-table__body-wrapper {
    tr {
      background-color: transparent;
      
      &:hover > td {
        background-color: var(--el-color-primary-light-9);
      }
    }
  }
}
</style> 