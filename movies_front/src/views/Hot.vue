<template>
  <BaseMovieList
    title="热门电影"
    api-endpoint="/api/movies/hot"
    error-message="获取热门电影失败"
  />
</template>

<script setup>
import BaseMovieList from '../components/BaseMovieList.vue'
</script>

<style lang="scss" scoped>
.hot-movies {
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