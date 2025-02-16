import axios from "axios";

// 创建axios实例
const service = axios.create({
  // axios中请求配置有baseURL选项，表示请求URL公共部分
  // baseURL: process.env.VUE_APP_BASE_API,
  baseURL: "http://localhost:5000",
  // 超时
  timeout: 20000,
});

export default service;
