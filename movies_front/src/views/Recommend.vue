<template>
  <BaseMovieList
    title="推荐电影"
    api-endpoint="/api/movies/recommend"
    error-message="获取推荐电影失败"
  />
</template>

<script setup>
import BaseMovieList from '../components/BaseMovieList.vue'
</script> 