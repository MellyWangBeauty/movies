import { createApp } from "vue";
import { createPinia } from 'pinia'
import "./style.css";
import router from "./router";
import App from "./App.vue";
import "element-plus/dist/index.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue"; // 引入所有图标
import ElementPlus from "element-plus";
import axios from 'axios'

// 配置 axios
axios.defaults.baseURL = ''  // 使用相对路径，让请求通过 Vite 代理
axios.defaults.withCredentials = true  // 允许跨域请求携带凭证

const app = createApp(App);
const pinia = createPinia()

// 全局注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

app.use(pinia);
app.use(router);
app.use(ElementPlus);
app.mount("#app");
