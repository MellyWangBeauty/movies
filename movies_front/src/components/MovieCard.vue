<template>
  <div class="movie-card">
    <router-link :to="`/movie/${movie.id}`">
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
    </router-link>
  </div>
</template>

<script setup>
import { Picture, View } from '@element-plus/icons-vue'

defineProps({
  movie: {
    type: Object,
    required: true
  }
})
</script>

<style lang="scss" scoped>
.movie-card {
  width: 100%;
  transition: transform 0.3s;
  margin-bottom: 20px;

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
}</style> 