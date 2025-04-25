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
      <year-chart 
        v-if="chartData.year_distribution" 
        :chart-data="chartData.year_distribution" 
      />
      

      
      <rating-chart 
        v-if="chartData.rating_distribution" 
        :chart-data="chartData.rating_distribution" 
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

export default {
  name: 'Statistics',
  components: {
    YearChart,
    TagChart,
    RatingChart,
    TypeTrendChart
  },
  data() {
    return {
      chartData: {
        year_distribution: null,
        tag_distribution: null,
        rating_distribution: null,
        type_trend: null
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