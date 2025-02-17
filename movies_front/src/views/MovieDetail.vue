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
          <span class="year">年份：{{ movie.years }}</span>
          <span class="country">制片国家：{{ movie.country }}</span>
        </div>
        <div class="movie-crew">
          <p class="director">导演：{{ movie.director_description }}</p>
          <p class="cast">主演：{{ movie.leader }}</p>
        </div>
        <div class="movie-tags">
          <span class="tag-label">标签：</span>
          <span class="tag" v-for="tag in movieTags" :key="tag">{{ tag }}</span>
        </div>
        <div class="movie-description">
          <h3>剧情简介</h3>
          <p>{{ movie.description }}</p>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="loading">
    加载中...
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/request'

export default {
  name: 'MovieDetail',
  setup() {
    const route = useRoute()
    const movie = ref(null)

    const fetchMovieDetail = async () => {
      try {
        const response = await request.get(`/movies/${route.params.id}`)
        movie.value = response.data
        // 增加浏览量
        await request.put(`/movies/${route.params.id}/view`)
      } catch (error) {
        console.error('Error fetching movie details:', error)
      }
    }

    const movieTags = computed(() => {
      if (!movie.value?.tags) return []
      return movie.value.tags.split('/')
    })

    onMounted(() => {
      fetchMovieDetail()
    })

    return {
      movie,
      movieTags
    }
  }
}
</script>

<style scoped>
.movie-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.movie-header {
  display: flex;
  gap: 30px;
  margin-bottom: 40px;
}

.movie-poster {
  flex-shrink: 0;
  width: 300px;
  height: 450px;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.movie-info {
  flex: 1;
}

.movie-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #333;
}

.movie-meta {
  margin-bottom: 20px;
}

.movie-meta span {
  margin-right: 20px;
  color: #666;
}

.rating {
  color: #e09015;
  font-weight: bold;
}

.movie-crew {
  margin-bottom: 20px;
}

.movie-crew p {
  margin: 10px 0;
  color: #666;
}

.movie-tags {
  margin-bottom: 30px;
}

.tag-label {
  color: #666;
  margin-right: 10px;
}

.tag {
  display: inline-block;
  padding: 4px 12px;
  margin: 0 8px 8px 0;
  background: #f5f5f5;
  border-radius: 15px;
  color: #666;
  font-size: 14px;
}

.movie-description {
  color: #333;
}

.movie-description h3 {
  margin-bottom: 15px;
  font-size: 20px;
}

.movie-description p {
  line-height: 1.6;
  color: #666;
}

.loading {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style> 