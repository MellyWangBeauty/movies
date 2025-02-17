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
    <el-skeleton :rows="10" animated />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const movie = ref(null)

const movieTags = computed(() => {
  if (!movie.value?.tags) return []
  return movie.value.tags.split('/')
})

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
})
</script>

<style lang="scss" scoped>
.movie-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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

.loading {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}
</style> 