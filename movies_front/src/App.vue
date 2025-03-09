<template>
  <div>
    <MyHeader></MyHeader>
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>
<script>
import MyHeader from "@/components/MyHeader.vue";

export default {
  name: 'App',
  components: {
    MyHeader
  }
}
</script>

<style>
body {
  margin: 0;
  background-color: #111;
}
</style>
