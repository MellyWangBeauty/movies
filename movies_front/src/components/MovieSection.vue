<template>
  <div class="movie-section">
    <div class="section-header">
      <h2 class="section-title">{{ title }}</h2>
      <router-link :to="moreLink" class="more-link">
        更多
        <el-icon><ArrowRight /></el-icon>
      </router-link>
    </div>
    <div class="movie-grid">
      <div v-for="movie in movies" :key="movie.id" class="movie-card">
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
    </div>
  </div>
</template>

<script setup>
import { ArrowRight, Picture } from '@element-plus/icons-vue'

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
  margin: 30px 0;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

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

    .movie-card {
      transition: transform 0.3s;

      &:hover {
        transform: translateY(-5px);

        .movie-title {
          color: var(--el-color-primary);
        }
      }

      a {
        text-decoration: none;
      }

      .movie-cover {
        width: 100%;
        height: 300px;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 10px;
      }

      .image-error {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f5f7fa;
        color: #909399;
        font-size: 30px;
      }

      .movie-title {
        font-size: 16px;
        color: #fff;
        margin: 0;
        text-align: center;
        transition: color 0.3s;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}
</style> 