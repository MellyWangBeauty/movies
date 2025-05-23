<template>
  <div class="movie-list">
    <div class="content">
      <h1 class="page-title">{{ title }}</h1>
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
import MovieCard from './MovieCard.vue'
import MovieFilter from './MovieFilter.vue'
import MoviePagination from './MoviePagination.vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  apiEndpoint: {
    type: String,
    required: true
  },
  errorMessage: {
    type: String,
    required: true
  }
})

const movies = ref([])
const filteredMovies = ref([])
const loading = ref(true)
const error = ref(null)
const paginationInfo = ref({
  start: 0,
  end: 30,
  pageSize: 30
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
    const response = await axios.get(props.apiEndpoint)
    movies.value = response.data
    filteredMovies.value = response.data
  } catch (err) {
    console.error(props.errorMessage, err)
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
.movie-list {
  width: 100%;
  min-height: calc(100vh - 60px);
  box-sizing: border-box;
  padding: 0 40px;

  .content {
    width: 1200px;
    margin: 0 auto;
    padding: 20px 0;
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