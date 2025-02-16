<template>
  <div class="swiper-container">
    <swiper
      :modules="modules"
      :autoplay="{
        delay: 4000, // 自动播放间隔时间（毫秒）
        disableOnInteraction: false, // 用户操作后是否停止自动播放
      }"
      :loop="true"
      :pagination="{ clickable: true }"
      :navigation="true"
    >
      <!-- 轮播项 -->
      <swiper-slide v-for="(slide, index) in slides" :key="index">
        <img :src="slide.image" :alt="slide.title" class="slide-image" />
      </swiper-slide>
    </swiper>
  </div>
</template>

<script setup>
// 引入 Swiper 核心和样式
import { Swiper, SwiperSlide } from "swiper/vue";
import { Autoplay, Pagination, Navigation } from "swiper/modules";
import "swiper/swiper-bundle.css";
import p1 from "../assets/p1.jpeg";
import p2 from "../assets/p2.png";
import p4 from "../assets/p4.jpeg";

// 定义 Swiper 模块
const modules = [Autoplay, Pagination, Navigation];

// 轮播图数据
const slides = [
  {
    image: p1,
    title: "复仇者联盟",
  },
  {
    image: p2,
    title: "哪吒",
  },
  {
    image: p4,
    title: "功夫熊猫",
  },
];
</script>

<style lang="scss">
.swiper-container {
  width: 100%;
  height: 75vh; /* 调整轮播图的高度为视口的 75% */
  position: relative;
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  overflow: hidden; /* 避免超出容器部分被显示 */

  &::before,
  &::after {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    width: 20%; /* 渐变区域的宽度 */
    z-index: 2;
    pointer-events: none;
  }

  &::before {
    left: 0;
    background: linear-gradient(
      to right,
      rgba(17, 19, 25) 0%,
      rgba(0, 0, 0, 0) 100%
    ); /* 左侧渐变 */
  }

  &::after {
    right: 0;
    background: linear-gradient(
      to left,
      rgba(17, 19, 25) 0%,
      rgba(0, 0, 0, 0) 100%
    ); /* 右侧渐变 */
  }

  .swiper {
    width: 100%;
    height: 100%;

    .slide-image {
      width: 100%; /* 宽度撑满容器 */
      height: 100%; /* 高度撑满容器 */
      object-fit: fill; /* 保持图片比例，覆盖容器 */
    }

    .swiper-button-next,
    .swiper-button-prev {
      position: absolute;
      top: 50%;
      z-index: 10;
      width: 50px;
      height: 50px;
      margin-top: -25px; /* 使箭头垂直居中 */
      background-color: rgba(0, 0, 0, 0.3);
      border-radius: 50%;
      color: white;
    }
  }
}
</style>
