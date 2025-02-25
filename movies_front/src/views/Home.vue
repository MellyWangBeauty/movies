<template>
  <div class="home">
    <MySwiper />
    <div class="content">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="error" class="error-container">
        <el-empty description="加载失败，请刷新重试" />
      </div>
      <div v-else class="movie-sections">
        <MovieSection 
          title="近期热门" 
          :movies="hotMovies" 
          more-link="/hot" 
        />
        <MovieSection 
          title="豆瓣排行" 
          :movies="rankedMovies" 
          more-link="/rank" 
        />
        <MovieSection 
          title="个性推荐" 
          :movies="recommendedMovies" 
          more-link="/recommend" 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import MySwiper from '../components/MySwiper.vue'
import MovieSection from '../components/MovieSection.vue'

const hotMovies = ref([])
const rankedMovies = ref([])
const recommendedMovies = ref([])
const loading = ref(true)
const error = ref(false)

const fetchMovies = async () => {
  loading.value = true
  error.value = false
  
  try {
    const [hotResponse, rankResponse, recommendResponse] = await Promise.all([
      axios.get('/api/movies/hot?limit=5'),
      axios.get('/api/movies/rank?limit=5'),
      axios.get('/api/movies/recommend?limit=5')
    ])

    hotMovies.value = hotResponse.data || []
    rankedMovies.value = rankResponse.data || []
    recommendedMovies.value = recommendResponse.data || []

    // 打印返回的数据，用于调试
    console.log('热门电影:', hotMovies.value)
    console.log('排行榜电影:', rankedMovies.value)
    console.log('推荐电影:', recommendedMovies.value)
  } catch (err) {
    console.error('获取电影数据失败:', err)
    error.value = true
    ElMessage.error('获取电影数据失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMovies()
})
</script>

<style lang="scss" scoped>
.home {
  .content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px 20px 20px;

  }

  .loading-container,
  .error-container {
    padding: 40px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    margin: 20px 0;
  }

  .movie-sections {
    margin-top: 40px;
  }
}
</style>
