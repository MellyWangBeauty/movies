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
            <th>操作</th>
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
            <td>
              <el-button
                type="danger"
                :icon="Delete"
                circle
                size="small"
                @click="handleDeleteReview(review.movie_id)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "../stores/user";
import * as echarts from "echarts";
import axios from "axios";
import { Delete } from '@element-plus/icons-vue'

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
      top: 5,
      textStyle: {
        color: "#fff",
        fontSize: 14
      },
    },
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} ({d}%)",
    },
    series: [
      {
        type: "pie",
        radius: ["20%", "55%"],
        center: ["50%", "55%"],
        data: tagsData,
        label: {
          color: "rgba(255, 255, 255, 0.85)",
          formatter: "{b}\n{c}部",
          fontSize: 12
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
      top: 5,
      textStyle: {
        color: "#fff",
        fontSize: 14
      },
    },
    grid: {
      top: 40,
      bottom: 20,
      left: '15%',
      right: '15%',
      containLabel: true
    },
    tooltip: {
      trigger: "axis",
    },
    yAxis: {
      type: "category",
      data: yearsData.map((item) => item.name),
      axisLabel: {
        color: "#fff",
        fontSize: 12,
        margin: 16,
        width: 30,
        overflow: 'break',
        interval: 0
      },
      axisTick: {
        alignWithLabel: true
      }
    },
    xAxis: {
      type: "value",
      show: false,
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
        barWidth: "50%",
        label: {
          show: true,
          position: "right",
          color: "#fff",
          formatter: "{c}部",
          fontSize: 12
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
      top: 5,
      textStyle: {
        color: "#fff",
        fontSize: 14
      },
    },
    grid: {
      top: 60,
      bottom: 30,
      left: '10%',
      right: '15%',
      containLabel: true
    },
    tooltip: {
      trigger: "axis",
    },
    yAxis: {
      type: "value",
      show: false,
    },
    xAxis: {
      type: "category",
      data: countryData.map((item) => item.name),
      axisLabel: {
        color: "#fff",
        interval: 0,
        rotate: 0,
        fontSize: 12,
        margin: 15
      },
      axisTick: {
        alignWithLabel: true
      }
    },
    series: [
      {
        data: countryData.map((item) => ({
          value: item.value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#FF6B6B" },
              { offset: 1, color: "#FFE66D" }
            ]),
          },
        })),
        type: "bar",
        barWidth: "40%",
        label: {
          show: true,
          position: "top",
          color: "#fff",
          formatter: "{c}部",
          fontSize: 12,
          distance: 10
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

// 删除评论
const handleDeleteReview = async (movieId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评价吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`/api/reviews/${movieId}`)
    ElMessage.success('删除成功')
    // 重新获取评论列表
    await fetchUserReviews()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除评论失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

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
  margin: 0 auto; /* 添加自动外边距使其居中 */
  width: 100%; /* 确保宽度为100% */
  box-sizing: border-box; /* 确保padding不会导致总宽度超过100% */

  .charts-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    padding: 20px;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    margin-bottom: 30px;

    .chart {
      height: 260px;
      padding: 10px;
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
    border-collapse: collapse;
    border-radius: 12px;
    max-width: 1200px;

    .movie-link {
      color: #409eff; /* 设置链接颜色为浅蓝 */
      text-decoration: none; /* 去掉下划线 */

      &:hover {
        text-decoration: underline; /* 悬停时添加下划线 */
      }
    }

    thead {
      background-color: rgba(255, 255, 255, 0.03);
      color: #fff;

      th {
        padding: 10px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        text-align: left;
      }
    }

    tbody {
      tr {
        background-color: rgba(255, 255, 255, 0.03);
        color: #fff;

        &:hover {
          background-color: rgba(70, 70, 70, 0.7);
        }

        td {
          padding: 10px;
        }

        .delete-btn {
          color: #f56c6c;
          cursor: pointer;
          transition: all 0.3s;
          
          &:hover {
            transform: scale(1.1);
          }
        }
      }
    }
  }
}
</style>
