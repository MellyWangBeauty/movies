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
      <div v-else>
        <div class="movie-grid">
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
  width: 100%;
  min-height: calc(100vh - 60px); // 减去头部导航的高度
  box-sizing: border-box;

  .content {
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding: 20px;
    box-sizing: border-box;

    .page-title {
      font-size: 28px;
      color: #fff;
      margin-bottom: 20px;
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
      gap: 16px;
      margin: 0 auto;

      @media (max-width: 1200px) {
        grid-template-columns: repeat(5, 1fr);
      }

      @media (max-width: 992px) {
        grid-template-columns: repeat(4, 1fr);
      }

      @media (max-width: 768px) {
        grid-template-columns: repeat(3, 1fr);
      }

      @media (max-width: 576px) {
        grid-template-columns: repeat(2, 1fr);
      }

      .movie-card {
        width: 100%;
        transition: transform 0.3s;

        &:hover {
          transform: translateY(-5px);

          .movie-title {
            color: var(--el-color-primary);
          }
        }

        a {
          text-decoration: none;
          display: block;
          width: 100%;
        }

        .movie-cover {
          width: 100%;
          aspect-ratio: 2/3;
          border-radius: 8px;
          overflow: hidden;
          margin-bottom: 8px;
          background-color: rgba(255, 255, 255, 0.1);
        }

        .image-error {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: rgba(255, 255, 255, 0.1);
          color: #909399;
          font-size: 24px;
        }

        .movie-title {
          font-size: 14px;
          color: #fff;
          margin: 0 0 8px;
          text-align: center;
          transition: color 0.3s;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          padding: 0 4px;
        }

        .movie-info {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;

          :deep(.el-rate) {
            height: 20px;
            line-height: 1;
            font-size: 12px;

            .el-rate__icon {
              font-size: 14px;
              margin-right: 2px;
            }
          }

          .view-count {
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 4px;

            .el-icon {
              font-size: 14px;
            }
          }
        }
      }
    }
  }
}
</style> 