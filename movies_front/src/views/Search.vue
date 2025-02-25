<template>
  <div class="search-movies">
    <div class="content">
      <div class="search-header">
        <h1 class="page-title">搜索电影</h1>
      </div>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="error" class="error-container">
        <el-empty :description="error" />
      </div>
      <div v-else>
        <div v-if="movies.length === 0" class="empty-result">
          <el-empty description="暂无搜索结果" />
        </div>
        <div v-else class="movie-grid">
          <MovieCard 
            v-for="movie in movies" 
            :key="movie.id" 
            :movie="movie"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import MovieCard from '../components/MovieCard.vue'

const route = useRoute()
const router = useRouter()
const movies = ref([])
const loading = ref(false)
const error = ref(null)
const searchKeyword = ref('')

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  // 更新 URL，但不触发路由变化
  router.replace({
    query: { keyword: searchKeyword.value.trim() }
  })

  loading.value = true
  error.value = null
  
  try {
    console.log('发送搜索请求:', searchKeyword.value.trim())  // 调试日志
    const response = await axios.get('/api/movies/search', {
      params: { keyword: searchKeyword.value.trim() }
    })
    console.log('搜索结果:', response.data)  // 调试日志
    movies.value = response.data
  } catch (err) {
    console.error('搜索电影失败:', err)
    error.value = '搜索失败，请重试'
    ElMessage.error(err.response?.data?.message || '搜索失败，请重试')
  } finally {
    loading.value = false
  }
}

// 监听路由参数变化
watch(
  () => route.query.keyword,
  (newKeyword) => {
    if (newKeyword && newKeyword !== searchKeyword.value) {
      searchKeyword.value = newKeyword
      handleSearch()
    }
  }
)

// 如果URL中有查询参数，自动执行搜索
onMounted(() => {
  const keyword = route.query.keyword
  if (keyword) {
    searchKeyword.value = keyword
    handleSearch()
  }
})
</script>

<style lang="scss" scoped>
.search-movies {
  width: 100%;
  min-height: calc(100vh - 60px);
  box-sizing: border-box;
  padding: 0 40px;

  .content {
    width: 1200px;
    margin: 0 auto;
    padding: 20px 0;
    box-sizing: border-box;

    .search-header {
      margin-bottom: 30px;
      text-align: center;

      .page-title {
        font-size: 28px;
        color: #fff;
        margin-bottom: 20px;
      }

      .search-bar {
        max-width: 600px;
        margin: 0 auto;

        :deep(.el-input-group__append) {
          background-color: var(--el-color-primary);
          border-color: var(--el-color-primary);
          
          .el-button {
            color: #fff;
            border: none;
            
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
    }

    .loading-container,
    .error-container,
    .empty-result {
      padding: 40px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      text-align: center;
    }

    .movie-grid {
      display: grid;
      grid-template-columns: repeat(6, 180px);
      gap: 24px;
      justify-content: center;

      @media (max-width: 1280px) {
        grid-template-columns: repeat(5, 180px);
      }

      @media (max-width: 1080px) {
        grid-template-columns: repeat(4, 180px);
      }

      @media (max-width: 880px) {
        grid-template-columns: repeat(3, 180px);
      }

      @media (max-width: 680px) {
        grid-template-columns: repeat(2, 180px);
      }
    }
  }

  @media (max-width: 1280px) {
    .content {
      width: 980px;
    }
  }

  @media (max-width: 1080px) {
    .content {
      width: 780px;
    }
  }

  @media (max-width: 880px) {
    .content {
      width: 580px;
    }
  }

  @media (max-width: 680px) {
    .content {
      width: 380px;
    }
  }
}
</style> 