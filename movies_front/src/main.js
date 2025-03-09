import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// 配置 axios 拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    // // 忽略特定的请求错误
    // if (error.config.url.includes('/api/reviews/')) {
    //   return Promise.reject(error);
    // }
    // 其他错误正常处理
    return Promise.reject(error);
  }
);

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')