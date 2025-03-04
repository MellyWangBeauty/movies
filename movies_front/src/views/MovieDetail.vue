<template>
  <div class="movie-detail" v-if="movie">
    <div class="movie-header">
      <div class="movie-poster">
        <img :src="movie.cover_image" :alt="movie.title">
      </div>
      <div class="movie-info">
        <h1 class="movie-title">{{ movie.title }}</h1>
        <div class="movie-meta">
          <span class="rating">豆瓣评分：{{ movie.rating }}</span>
          <span class="duration" v-if="movie.duration">片长：{{ movie.duration }}分钟</span>
          <span class="year">年份：{{ movie.years }}</span>
          <span class="country">制片国家：{{ movie.country }}</span>
        </div>
        <div class="movie-crew">
          <p class="director">导演：{{ movie.director_description }}</p>
          <p class="actors" v-if="movie.actors">主演：{{ formatActors }}</p>
          <p class="leader" v-else>主演：{{ movie.leader }}</p>
        </div>
        <div class="movie-tags">
          <span class="tag-label">类型：</span>
          <span class="tag" v-for="tag in movieTags" :key="tag">{{ tag }}</span>
        </div>
        <div class="movie-description">
          <h3>剧情简介</h3>
          <p>{{ movie.plot || movie.description }}</p>
        </div>
      </div>
    </div>
    
    <!-- 短评区域 -->
    <div class="movie-comments" v-if="hasComments">
      <h2>精选短评 ({{ movieComments.length }}条)</h2>
      <div class="comments-grid">
        <div class="comment-card" v-for="(comment, index) in movieComments" :key="index">
          <div class="comment-header">
            <span class="comment-index">短评 {{ index + 1 }}</span>
          </div>
          <p class="comment-content">{{ comment }}</p>
        </div>
      </div>
    </div>

    <!-- 用户评分 -->
    <div class="user-review-section">
      <h2>我的评价</h2>
      
      <!-- 评分组件 -->
      <div class="rating-box">
        <span class="rating-label">评分：</span>
        <el-rate
          v-model="userRating"
          :colors="['#ffd04b', '#ffd04b', '#ffd04b']"
          :show-score="true"
          score-template="{value}分"
          @change="handleRatingChange"
        />
      </div>

      <!-- 影评输入框 -->
      <div class="review-box">
        <span class="review-label">影评：</span>
        <el-input
          v-model="userReview"
          type="textarea"
          :rows="4"
          placeholder="写下你的观后感..."
          :maxlength="500"
          show-word-limit
        />
      </div>

      <!-- 提交按钮 -->
      <div class="submit-box">
        <el-button 
          type="primary" 
          :loading="submitting"
          @click="submitReview"
        >
          发布评价
        </el-button>
      </div>
    </div>
  </div>
  <div v-else class="loading">
    <el-skeleton :rows="10" animated />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const movie = ref(null)

const movieTags = computed(() => {
  if (!movie.value?.tags) return []
  return movie.value.tags.split('/')
})

const formatActors = computed(() => {
  if (!movie.value?.actors) return ''
  return movie.value.actors.replace(/\|/g, '、')
})

const movieComments = computed(() => {
  if (!movie.value) return []
  const comments = [
    movie.value.comment1,
    movie.value.comment2,
    movie.value.comment3,
    movie.value.comment4,
    movie.value.comment5
  ]
  // 过滤掉null、undefined和空字符串
  return comments.filter(comment => comment && comment.trim() !== '')
})

const hasComments = computed(() => {
  return movieComments.value.length > 0
})

// 新增评分和评论相关的响应式变量
const userRating = ref(0)
const userReview = ref('')
const submitting = ref(false)
const userStore = useUserStore()

const handleRatingChange = (value) => {
  if (!userStore.isLoggedIn()) {
    ElMessage.warning('请先登录后再评分')
    userRating.value = 0
    return
  }
}

const submitReview = async () => {
  if (!userStore.isLoggedIn()) {
    ElMessage.warning('请先登录后再发表评价')
    return
  }

  if (userRating.value === 0) {
    ElMessage.warning('请先给出评分')
    return
  }

  if (!userReview.value.trim()) {
    ElMessage.warning('请输入影评内容')
    return
  }

  try {
    submitting.value = true
    // 直接从 userStore.token 获取 token
    const token = userStore.token
    const response = await axios.post(`/api/reviews/${route.params.id}`, {
      rating: userRating.value,
      content: userReview.value
    }, {
      headers: {
        'Authorization': `Bearer ${token}`  // 添加token到请求头
      }
    })

    ElMessage.success('评价发布成功')
    userRating.value = 0
    userReview.value = ''
    await fetchReview()
  } catch (error) {
    console.error('提交评价失败:', error)
    if (error.response?.status === 401) {
      ElMessage.error('请先登录后再评价')
      // 可以在这里添加跳转到登录页面的逻辑
      // router.push('/login')
    } else if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('评价发布失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

const fetchReview = async () => {
  try {
    const token = userStore.token
    const response = await axios.get(`/api/reviews/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    // 检查是否有评论数据
    if (response.data) {
      // 只设置一次评分和评论
      userRating.value = response.data.rating
      userReview.value = response.data.content
    } else {
      // 如果没有评论数据，重置为初始状态
      userRating.value = 0
      userReview.value = ''
      reviews.value = null
      totalReviews.value = 0
    }
  } catch (error) {
    console.error('获取评论列表失败:', error)
    if (error.response?.status === 401) {
      console.log('用户未登录')
      // 重置表单
      userRating.value = 0
      userReview.value = ''
    }
  }
}

const fetchMovieDetail = async () => {
  try {
    const response = await axios.get(`/api/movies/${route.params.id}`)
    movie.value = response.data
  } catch (error) {
    console.error('Error fetching movie details:', error)
  }
}

onMounted(() => {
  fetchMovieDetail()
  fetchReview()
})
</script>

<style lang="scss" scoped>
.movie-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 100px;
  color: #fff;
}

.movie-header {
  display: flex;
  gap: 30px;
  margin-bottom: 40px;

  @media (max-width: 768px) {
    flex-direction: column;
  }
}

.movie-poster {
  flex-shrink: 0;
  width: 300px;
  height: 450px;
  
  @media (max-width: 768px) {
    width: 100%;
    height: auto;
    max-width: 300px;
    margin: 0 auto;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }
}

.movie-info {
  flex: 1;
}

.movie-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #fff;
}

.movie-meta {
  margin-bottom: 20px;

  span {
    margin-right: 20px;
    color: #ccc;
  }
}

.rating {
  color: #ffd04b;
  font-weight: bold;
}

.movie-crew {
  margin-bottom: 20px;

  p {
    margin: 10px 0;
    color: #ccc;
  }
}

.movie-tags {
  margin-bottom: 30px;

  .tag-label {
    color: #ccc;
    margin-right: 10px;
  }

  .tag {
    display: inline-block;
    padding: 4px 12px;
    margin: 0 8px 8px 0;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    color: #fff;
    font-size: 14px;
  }
}

.movie-description {
  color: #fff;

  h3 {
    margin-bottom: 15px;
    font-size: 20px;
  }

  p {
    line-height: 1.6;
    color: #ccc;
  }
}

.movie-comments {
  margin-top: 40px;
  
  h2 {
    font-size: 24px;
    margin-bottom: 20px;
    color: #fff;
  }
  
  .comments-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
  
  .comment-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 20px;
    
    .comment-header {
      margin-bottom: 10px;
      
      .comment-index {
        color: var(--el-color-primary);
        font-size: 14px;
      }
    }
    
    .comment-content {
      color: #ccc;
      line-height: 1.6;
      margin: 0;
      font-size: 15px;
      text-indent: 2em;
    }
  }
}

.loading {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.user-review-section {
  margin-top: 40px;
  
  h2 {
    font-size: 24px;
    color: #fff;
    margin-bottom: 20px;
  }

  .rating-box {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    
    .rating-label {
      color: #fff;
      margin-right: 10px;
    }
  }

  .review-box {
    margin-bottom: 20px;
    
    .review-label {
      display: block;
      color: #fff;
      margin-bottom: 10px;
    }
  }

  .submit-box {
    text-align: right;
    margin-bottom: 30px;
  }

  .all-reviews {
    .reviews-list {
      .review-item {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;

        .review-header {
          display: flex;
          align-items: flex-start;
          margin-bottom: 15px;

          .review-info {
            margin-left: 12px;
            flex: 1;

            .reviewer-name {
              color: #fff;
              font-size: 16px;
              display: block;
              margin-bottom: 4px;
            }

            .review-meta {
              display: flex;
              align-items: center;
              gap: 10px;

              .review-date {
                color: #909399;
                font-size: 14px;
              }
            }
          }
        }

        .review-content {
          color: #fff;
          line-height: 1.6;
        }
      }
    }
  }
}

:deep(.el-textarea__inner) {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;

  &:focus {
    border-color: var(--el-color-primary);
  }
}

:deep(.el-divider) {
  background-color: rgba(255, 255, 255, 0.1);
  margin: 30px 0;
}
</style> 