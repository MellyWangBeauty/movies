<template>
  <div class="user-center">
    <h1 style="text-align: center; color: #fff; padding-top: 20px">
      观影分析报告
    </h1>
    <div>
      <div class="charts-container">
        <!-- 电影标签分布 -->
        <div ref="tagsPieChart" class="chart"></div>

        <!-- 电影年份分布 -->
        <div ref="yearsBarChart" class="chart"></div>

        <!-- 电影地区分布 -->
        <div ref="countryBarChart" class="chart"></div>
      </div>
      <table class="reviews-table">
        <thead>
          <tr>
            <th>我的影评</th>
            <th>评分</th>
            <th>评价</th>
            <th>评价时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="review in userReviews" :key="review.movie_id">
            <td>
              <router-link :to="'/movie/' + review.movie_id" class="movie-link">
                {{ review.movie_title }}
              </router-link>
            </td>
            <td>
              <el-rate
                v-model="review.rating"
                disabled
                show-score
                text-color="#ff9900"
              />
            </td>
            <td>{{ review.content }}</td>
            <td>{{ formatDate(review.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from "vue";
import { ElMessage } from "element-plus";
import { useUserStore } from "../stores/user";
import * as echarts from "echarts";
import axios from "axios";

const userStore = useUserStore();
const userReviews = ref([]);

// ECharts 实例引用
const tagsPieChart = ref(null);
const yearsBarChart = ref(null);
const countryBarChart = ref(null);

const form = reactive({
  username: "",
  email: "",
  bio: "",
});

// 初始化表单数据
const initForm = () => {
  const userInfo = userStore.userInfo;
  if (userInfo) {
    form.username = userInfo.username;
    form.email = userInfo.email;
    form.bio = userInfo.bio || "";
  }
};

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// 获取用户评论数据
const fetchUserReviews = async () => {
  try {
    const response = await axios.get("/api/reviews/users/me/reviews");
    userReviews.value = response.data;
    await nextTick();
    initCharts(response.data);
  } catch (error) {
    console.error("获取用户评论失败:", error);
    ElMessage.error("获取评论数据失败");
  }
};

// 初始化图表
const initCharts = (reviews) => {
  // 设置图表主题色
  const chartTheme = {
    backgroundColor: "transparent",
    textStyle: {
      color: "rgba(255, 255, 255, 0.85)",
    },
    title: {
      textStyle: {
        color: "rgba(255, 255, 255, 0.85)",
        fontSize: 16,
        fontWeight: "normal",
      },
    },
    tooltip: {
      backgroundColor: "rgba(50, 50, 50, 0.9)",
      borderColor: "rgba(255, 255, 255, 0.1)",
      textStyle: {
        color: "#fff",
      },
    },
  };

  // 处理数据
  const tagsData = processTagsData(reviews);
  const yearsData = processYearsData(reviews);
  const countryData = processCountryData(reviews);

  // 初始化饼图
  const pieChart = echarts.init(tagsPieChart.value);
  pieChart.setOption({
    ...chartTheme,
    title: {
      text: "标签分布",
      left: "center",
      top: 0,
      textStyle: {
        color: "#fff", // 修改为你想要的颜色
      },
    },
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} ({d}%)",
    },
    series: [
      {
        type: "pie",
        radius: ["30%", "70%"],
        center: ["50%", "55%"],
        data: tagsData,
        label: {
          color: "rgba(255, 255, 255, 0.85)",
        },
        itemStyle: {
          borderColor: "rgba(17, 19, 25, 1)",
          borderWidth: 2,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.5)",
          },
        },
      },
    ],
  });

  // 初始化年份柱状图
  const yearsChart = echarts.init(yearsBarChart.value);
  yearsChart.setOption({
    ...chartTheme,
    title: {
      text: "年份分布",
      left: "center",
      textStyle: {
        color: "#fff",
      },
    },
    tooltip: {
      trigger: "axis",
    },
    yAxis: {
      type: "category",
      data: yearsData.map((item) => item.name.toString().split('').join('\n')),
      axisLabel: {
        color: "#fff",
        lineHeight: 18,
        padding: [0, 0, 0, 0],
        formatter: function(value) {
          return value.split('\n').join('\n');
        }
      },
    },
    xAxis: {
      type: "value",
      show: false, // 隐藏y轴
    },
    series: [
      {
        data: yearsData.map((item) => ({
          value: item.value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#409eff" },
              { offset: 1, color: "#36cfc9" },
            ]),
          },
        })),
        type: "bar",
        barWidth: "60%",
        label: {
          show: true,
          position: "right",
          color: "#fff",
        },
      },
    ],
  });

  // 初始化地区柱状图
  const countryChart = echarts.init(countryBarChart.value);
  countryChart.setOption({
    ...chartTheme,
    title: {
      text: "地区分布",
      left: "center",
      textStyle: {
        color: "#fff",
      },
    },
    tooltip: {
      trigger: "axis",
    },
    yAxis: {
      type: "value",
      show: false, // 隐藏x轴
    },
    xAxis: {
      type: "category",
      data: countryData.map((item) => item.name),
      axisLabel: {
        color: "#fff",
      },
    },
    series: [
      {
        data: countryData.map((item) => ({
          value: item.value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
              { offset: 0, color: "#409eff" },
              { offset: 1, color: "#36cfc9" },
            ]),
          },
        })),
        type: "bar",
        barWidth: "60%",
        label: {
          show: true,
          position: "top",
          color: "#fff",
        },
      },
    ],
  });

  // 监听窗口大小变化
  window.addEventListener("resize", () => {
    pieChart.resize();
    yearsChart.resize();
    countryChart.resize();
  });
};

// 处理标签数据
const processTagsData = (reviews) => {
  const tagsCount = {};
  reviews.forEach((review) => {
    const tags = review.tags.split("/");
    tags.forEach((tag) => {
      tagsCount[tag] = (tagsCount[tag] || 0) + 1;
    });
  });
  return Object.entries(tagsCount).map(([name, value]) => ({ name, value }));
};

// 处理年份数据
const processYearsData = (reviews) => {
  const yearsCount = {};
  reviews.forEach((review) => {
    const year = review.year;
    yearsCount[year] = (yearsCount[year] || 0) + 1;
  });
  return Object.entries(yearsCount)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => a.name - b.name);
};

// 处理地区数据
const processCountryData = (reviews) => {
  const countryCount = {};
  reviews.forEach((review) => {
    const country = review.country;
    countryCount[country] = (countryCount[country] || 0) + 1;
  });
  return Object.entries(countryCount)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
};

onMounted(() => {
  initForm();
  fetchUserReviews();
});
</script>

<style lang="scss" scoped>
.user-center {
  max-width: 1200px;
  padding: 0 20px 20px 20px;
  color: #fff;
  background-color: rgba(255, 255, 255, 0.02);

  .charts-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 40px;
    padding: 20px;
    border-radius: 16px;
    backdrop-filter: blur(10px);

    .chart {
      height: 350px;
      padding: 20px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 12px;
      transition: transform 0.3s ease, box-shadow 0.3s ease;

      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
      }
    }
  }

  .reviews-table {
    width: 96%;
    margin: 0 auto;
    border-collapse: collapse; /* 合并边框 */
    border-radius: 12px; /* 圆角 */
    max-width: 1200px; /* 设置最大宽度 */

    .movie-link {
      color: #409eff; /* 设置链接颜色为浅蓝 */
      text-decoration: none; /* 去掉下划线 */

      &:hover {
        text-decoration: underline; /* 悬停时添加下划线 */
      }
    }

    thead {
      background-color: rgba(255, 255, 255, 0.03); /* 表头背景色 */
      color: #fff; /* 表头文字颜色 */

      th {
        padding: 10px; /* 表头内边距 */
        border-bottom: 2px solid rgba(255, 255, 255, 0.1); /* 表头底部边框 */
        text-align: left; /* 表头居左对齐 */
      }
    }

    tbody {
      tr {
        background-color: rgba(255, 255, 255, 0.03); /* 行背景色 */
        color: #fff; /* 行文字颜色 */

        &:hover {
          background-color: rgba(70, 70, 70, 0.7); /* 悬停行背景色 */
        }

        td {
          padding: 10px; /* 单元格内边距 */
        }
      }
    }
  }
}
</style>
