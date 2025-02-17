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
        <MovieFilter 
          :movies="movies" 
          @filter="handleFilter"
        />
        <div class="movie-grid">
          <MovieCard 
            v-for="movie in displayedMovies" 
            :key="movie.id" 
            :movie="movie"
          />
        </div>
        <MoviePagination 
          :total="filteredMovies.length"
          @update="handlePagination"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import MovieCard from '../components/MovieCard.vue'
import MovieFilter from '../components/MovieFilter.vue'
import MoviePagination from '../components/MoviePagination.vue'

const movies = ref([])
const filteredMovies = ref([])
const loading = ref(true)
const error = ref(null)
const paginationInfo = ref({
  start: 0,
  end: 24,
  pageSize: 24
})

const displayedMovies = computed(() => {
  return filteredMovies.value.slice(paginationInfo.value.start, paginationInfo.value.end)
})

const handleFilter = (filtered) => {
  filteredMovies.value = filtered
}

const handlePagination = (info) => {
  paginationInfo.value = info
}

const fetchMovies = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await axios.get('/api/movies/rank')
    movies.value = response.data
    filteredMovies.value = response.data
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
    }
  }
}
</style> 