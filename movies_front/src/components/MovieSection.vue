<template>
  <div class="movie-section">
    <div class="section-header">
      <h2 class="section-title">{{ title }}</h2>
      <router-link v-if="moreLink" :to="moreLink" class="more-link">
        更多
        <el-icon><ArrowRight /></el-icon>
      </router-link>
    </div>
    <div class="movie-grid">
      <MovieCard 
        v-for="movie in movies" 
        :key="movie.id" 
        :movie="movie"
      />
    </div>
  </div>
</template>

<script setup>
import { ArrowRight } from '@element-plus/icons-vue'
import MovieCard from './MovieCard.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  movies: {
    type: Array,
    required: true
  },
  moreLink: {
    type: String,
    required: true
  }
})
</script>

<style lang="scss" scoped>
.movie-section {
  margin-bottom: 20px;

  .section-header {
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .section-title {
      font-size: 24px;
      color: #fff;
      margin: 0;
    }

    .more-link {
      display: flex;
      align-items: center;
      color: #fff;
      text-decoration: none;
      font-size: 16px;
      opacity: 0.8;
      transition: opacity 0.3s;

      &:hover {
        opacity: 1;
      }

      .el-icon {
        margin-left: 5px;
      }
    }
  }

  .movie-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 20px;

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
</style> 