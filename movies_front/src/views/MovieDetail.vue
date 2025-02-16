<template>
  <div class="movie-detail" v-if="movie">
    <div class="movie-header">
      <div class="movie-cover">
        <el-image 
          :src="movie.cover_image" 
          :alt="movie.title"
          fit="cover"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
            </div>
          </template>
        </el-image>
      </div>
      <div class="movie-info">
        <h1 class="title">{{ movie.title }}</h1>
        <div class="meta">
          <div class="rating">
            <el-rate
              v-model="movie.rating"
              disabled
              show-score
              text-color="#ff9900"
              score-template="{value}"
            />
          </div>
          <div class="release-date">
            上映日期：{{ formatDate(movie.release_date) }}
          </div>
          <div class="category">
            类型：{{ movie.category }}
          </div>
          <div class="view-count">
            浏览量：{{ movie.view_count }}
          </div>
        </div>
        <div class="description">
          <h3>剧情简介</h3>
          <p>{{ movie.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Picture } from '@element-plus/icons-vue'

const route = useRoute()
const movie = ref(null)

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 获取电影详情
const fetchMovieDetail = async () => {
  try {
    const response = await axios.get(`/api/movies/${route.params.id}`)
    movie.value = response.data
  } catch (error) {
    ElMessage.error('获取电影详情失败')
    console.error('获取电影详情失败:', error)
  }
}

onMounted(() => {
  fetchMovieDetail()
})
</script>

<style lang="scss" scoped>
.movie-detail {
  max-width: 1200px;
  margin: 30px auto;
  padding: 0 20px;
  color: #fff;

  .movie-header {
    display: flex;
    gap: 40px;

    .movie-cover {
      flex-shrink: 0;
      width: 300px;
      height: 450px;
      border-radius: 8px;
      overflow: hidden;

      .el-image {
        width: 100%;
        height: 100%;
      }

      .image-error {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f5f7fa;
        color: #909399;
        font-size: 30px;
      }
    }

    .movie-info {
      flex-grow: 1;

      .title {
        font-size: 32px;
        margin: 0 0 20px;
      }

      .meta {
        margin-bottom: 30px;

        > div {
          margin-bottom: 10px;
          font-size: 16px;
          color: rgba(255, 255, 255, 0.8);
        }

        .rating {
          margin-bottom: 20px;
        }
      }

      .description {
        h3 {
          font-size: 20px;
          margin: 0 0 15px;
        }

        p {
          font-size: 16px;
          line-height: 1.6;
          color: rgba(255, 255, 255, 0.8);
          margin: 0;
        }
      }
    }
  }
}
</style> 