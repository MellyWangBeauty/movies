<template>
  <BaseMovieList
    title="电影排行榜"
    api-endpoint="/api/movies/rank"
    error-message="获取排行榜电影失败"
  />
</template>

<script setup>
import BaseMovieList from '../components/BaseMovieList.vue'
</script> 