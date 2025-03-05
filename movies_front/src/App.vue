<template>
  <div>
    <MyHeader></MyHeader>
    <keep-alive>
      <router-view />
    </keep-alive>
  </div>
</template>
<script>
import MyHeader from "@/components/MyHeader.vue";
</script>
