<template>
  <div class="rank-movies">
    <div class="content">
      <h1 class="page-title">电影排行榜</h1>
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="error" class="error-container">
        <el-empty :description="error" />
      </div>
      <div v-else class="movie-grid">
        <div v-for="movie in movies" :key="movie.id" class="movie-card">
          <router-link :to="{ name: 'movie-detail', params: { id: movie.id.toString() }}">
            <el-image 
              :src="movie.cover_image" 
              :alt="movie.title"
              class="movie-cover"
              fit="cover"
            >
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <h3 class="movie-title">{{ movie.title }}</h3>
            <div class="movie-info">
              <el-rate
                v-model="movie.rating"
                disabled
                show-score
                text-color="#ff9900"
                score-template="{value}"
              />
              <div class="view-count">
                <el-icon><View /></el-icon>
                {{ movie.view_count }}
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Picture, View } from '@element-plus/icons-vue'

const movies = ref([])
const loading = ref(true)
const error = ref(null)

const fetchMovies = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await axios.get('/api/movies/rank?limit=24')
    movies.value = response.data
  } catch (err) {
    console.error('获取排行榜电影失败:', err)
    error.value = '获取电影数据失败，请刷新重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMovies()
})
</script>

<style lang="scss" scoped>
.rank-movies {
  .content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;

    .page-title {
      font-size: 28px;
      color: #fff;
      margin-bottom: 30px;
    }

    .loading-container,
    .error-container {
      padding: 40px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 8px;
    }

    .movie-grid {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 20px;

      .movie-card {
        transition: transform 0.3s;

        &:hover {
          transform: translateY(-5px);

          .movie-title {
            color: var(--el-color-primary);
          }
        }

        a {
          text-decoration: none;
        }

        .movie-cover {
          width: 100%;
          height: 300px;
          border-radius: 8px;
          overflow: hidden;
          margin-bottom: 10px;
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

        .movie-title {
          font-size: 16px;
          color: #fff;
          margin: 0 0 10px;
          text-align: center;
          transition: color 0.3s;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .movie-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 10px;

          .view-count {
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
          }
        }
      }
    }
  }
}
</style> 