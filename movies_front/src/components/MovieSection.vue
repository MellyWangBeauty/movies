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
  margin-bottom: 40px;

  .section-header {
    margin: 20px 60px;
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
    grid-template-columns: repeat(auto-fit, 180px);
    gap: 24px;
    justify-content: center;
    padding: 0 60px;
    max-width: 1400px;
    margin: 0 auto;

    @media (max-width: 1280px) {
      max-width: 1100px;
    }

    @media (max-width: 1080px) {
      max-width: 900px;
    }

    @media (max-width: 880px) {
      max-width: 700px;
    }

    @media (max-width: 680px) {
      max-width: 500px;
    }
  }
}
</style> 