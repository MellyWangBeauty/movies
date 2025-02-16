import { createRouter, createWebHistory } from "vue-router";
import Home from "./views/Home.vue";
import Test from "./views/Test.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/hot",
    component: Test,
  },
  {
    path: "/rank",
    component: Test,
  },
  {
    path: "/recommend",
    component: Test,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
