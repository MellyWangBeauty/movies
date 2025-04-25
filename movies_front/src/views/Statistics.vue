<template>
  <div class="statistics-container">
    <h1>电影数据分析</h1>
    <div class="charts-container">

      <tag-chart 
        v-if="chartData.tag_distribution" 
        :chart-data="chartData.tag_distribution" 
      />
      <type-trend-chart 
        v-if="chartData.type_trend" 
        :chart-data="chartData.type_trend" 
      />
      <country-rating-chart
        v-if="chartData.country_rating_comparison"
        :chart-data="chartData.country_rating_comparison"
      />
      <type-duration-rating-chart
        v-if="chartData.type_duration_rating"
        :chart-data="chartData.type_duration_rating"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import YearChart from '@/components/charts/YearChart.vue'
import TagChart from '@/components/charts/TagChart.vue'
import RatingChart from '@/components/charts/RatingChart.vue'
import TypeTrendChart from '@/components/charts/TypeTrendChart.vue'
import CountryRatingChart from '@/components/charts/CountryRatingChart.vue'
import DurationRatingChart from '@/components/charts/DurationRatingChart.vue'
import TypeDurationRatingChart from '@/components/charts/TypeDurationRatingChart.vue'

export default {
  name: 'Statistics',
  components: {
    YearChart,
    TagChart,
    RatingChart,
    TypeTrendChart,
    CountryRatingChart,
    DurationRatingChart,
    TypeDurationRatingChart
  },
  data() {
    return {
      chartData: {
        year_distribution: null,
        tag_distribution: null,
        rating_distribution: null,
        type_trend: null,
        country_rating_comparison: null,
        duration_rating_relation: null,
        type_duration_rating: null
      }
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get('/api/statistics')
        const data = response.data
        console.log('收到的统计数据:', data)
        
        this.chartData = data
        
        // 如果缺少类型趋势数据，使用默认数据
        if (!this.chartData.type_trend) {
          console.error('未找到类型趋势数据')
          this.chartData.type_trend = {
            years: ['2020', '2021', '2022', '2023', '2024'],
            series: [
              {name: '动作', type: 'line', data: [5, 8, 12, 10, 15]},
              {name: '爱情', type: 'line', data: [10, 7, 5, 8, 6]},
              {name: '喜剧', type: 'line', data: [8, 10, 15, 18, 20]},
              {name: '科幻', type: 'line', data: [3, 5, 7, 9, 12]},
              {name: '动画', type: 'line', data: [6, 8, 4, 7, 9]}
            ]
          }
        }
        
        // 如果缺少地区评分对比数据，使用默认数据
        if (!this.chartData.country_rating_comparison) {
          console.error('未找到地区评分对比数据')
          this.chartData.country_rating_comparison = {
            countries: ['中国大陆', '美国', '日本', '韩国', '英国', '法国', '中国香港', '中国台湾'],
            avg_ratings: [8.2, 8.5, 8.8, 8.0, 8.3, 8.1, 8.6, 8.4],
            movie_counts: [30, 45, 25, 15, 20, 10, 18, 12]
          }
        }
        
        // 如果缺少电影时长与评分关系数据，使用默认数据
        if (!this.chartData.duration_rating_relation) {
          console.error('未找到电影时长与评分关系数据')
          this.chartData.duration_rating_relation = {
            categories: ['90分钟以下', '90-120分钟', '120-150分钟', '150-180分钟', '180分钟以上'],
            avg_ratings: [7.5, 8.2, 8.6, 8.4, 8.8],
            movie_counts: [12, 45, 35, 20, 8]
          }
        }
        
        // 如果缺少电影类型、时长与评分关系数据，使用默认数据
        if (!this.chartData.type_duration_rating) {
          console.error('未找到电影类型、时长与评分关系数据')
          this.chartData.type_duration_rating = {
            types: ["剧情", "喜剧", "动作", "爱情", "科幻", "动画", "惊悚", "冒险"],
            data: [
              [90, 15, 8.5, "剧情"],
              [120, 12, 9.0, "剧情"],
              [150, 8, 8.8, "剧情"],
              [95, 10, 8.2, "喜剧"],
              [110, 8, 8.0, "喜剧"],
              [130, 5, 7.8, "喜剧"],
              [125, 15, 7.9, "动作"],
              [140, 10, 8.3, "动作"],
              [100, 8, 8.2, "爱情"],
              [115, 6, 8.5, "爱情"],
              [135, 10, 8.8, "科幻"],
              [160, 8, 9.2, "科幻"],
              [90, 12, 8.6, "动画"],
              [110, 8, 8.9, "动画"],
              [120, 10, 8.1, "惊悚"],
              [145, 7, 8.4, "冒险"]
            ]
          }
        }
      } catch (error) {
        console.error('获取数据失败:', error)
        // 使用默认数据
        this.chartData = {
          year_distribution: {
            years: ['2020', '2021', '2022', '2023', '2024'],
            counts: [10, 15, 20, 25, 30]
          },
          tag_distribution: {
            tags: ['动作', '爱情', '喜剧', '科幻', '动画'],
            counts: [30, 25, 20, 15, 10]
          },
          rating_distribution: {
            ratings: ['7.0', '7.5', '8.0', '8.5', '9.0'],
            counts: [5, 10, 20, 15, 8]
          },
          type_trend: {
            years: ['2020', '2021', '2022', '2023', '2024'],
            series: [
              {name: '动作', type: 'line', data: [5, 8, 12, 10, 15]},
              {name: '爱情', type: 'line', data: [10, 7, 5, 8, 6]},
              {name: '喜剧', type: 'line', data: [8, 10, 15, 18, 20]},
              {name: '科幻', type: 'line', data: [3, 5, 7, 9, 12]},
              {name: '动画', type: 'line', data: [6, 8, 4, 7, 9]}
            ]
          },
          country_rating_comparison: {
            countries: ['中国大陆', '美国', '日本', '韩国', '英国', '法国', '中国香港', '中国台湾'],
            avg_ratings: [8.2, 8.5, 8.8, 8.0, 8.3, 8.1, 8.6, 8.4],
            movie_counts: [30, 45, 25, 15, 20, 10, 18, 12]
          },
          duration_rating_relation: {
            categories: ['90分钟以下', '90-120分钟', '120-150分钟', '150-180分钟', '180分钟以上'],
            avg_ratings: [7.5, 8.2, 8.6, 8.4, 8.8],
            movie_counts: [12, 45, 35, 20, 8]
          },
          type_duration_rating: {
            types: ["剧情", "喜剧", "动作", "爱情", "科幻", "动画", "惊悚", "冒险"],
            data: [
              [90, 15, 8.5, "剧情"],
              [120, 12, 9.0, "剧情"],
              [150, 8, 8.8, "剧情"],
              [95, 10, 8.2, "喜剧"],
              [110, 8, 8.0, "喜剧"],
              [130, 5, 7.8, "喜剧"],
              [125, 15, 7.9, "动作"],
              [140, 10, 8.3, "动作"],
              [100, 8, 8.2, "爱情"],
              [115, 6, 8.5, "爱情"],
              [135, 10, 8.8, "科幻"],
              [160, 8, 9.2, "科幻"],
              [90, 12, 8.6, "动画"],
              [110, 8, 8.9, "动画"],
              [120, 10, 8.1, "惊悚"],
              [145, 7, 8.4, "冒险"]
            ]
          }
        }
      }
    }
  }
}
</script>

<style scoped>
.statistics-container {
  padding: 20px;
  background-color: #1a1a1a;
  min-height: 100vh;
  max-width: 100%;
  overflow-x: hidden;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #fff;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  max-width: 100%;
  padding: 0 10px;
}

@media (max-width: 1200px) {
  .charts-container {
    grid-template-columns: 1fr; /* 在小屏幕上改为单列 */
  }
}
</style>