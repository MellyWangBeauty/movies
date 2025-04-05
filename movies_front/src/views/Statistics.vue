<template>
  <div class="statistics-container">
    <h1>电影数据分析</h1>
    <div class="charts-container">
      <div class="chart-item">
        <h2>年份分布</h2>
        <div ref="yearChart" class="chart"></div>
      </div>
      <div class="chart-item">
        <h2>标签分布</h2>
        <div ref="tagChart" class="chart"></div>
      </div>
      <div class="chart-item">
        <h2>评分分布</h2>
        <div ref="ratingChart" class="chart"></div>
      </div>
      <div class="chart-item">
        <h2>国家分布</h2>
        <div ref="countryChart" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'Statistics',
  data() {
    return {
      yearChart: null,
      tagChart: null,
      ratingChart: null,
      countryChart: null
    }
  },
  mounted() {
    this.initCharts()
    this.fetchData()
  },
  methods: {
    initCharts() {
      this.yearChart = echarts.init(this.$refs.yearChart)
      this.tagChart = echarts.init(this.$refs.tagChart)
      this.ratingChart = echarts.init(this.$refs.ratingChart)
      this.countryChart = echarts.init(this.$refs.countryChart)
    },
    async fetchData() {
      try {
        const response = await axios.get('/api/statistics')
        const data = response.data
        
        // 更新年份分布图表
        this.updateYearChart(data.year_distribution)
        
        // 更新标签分布图表
        this.updateTagChart(data.tag_distribution)
        
        // 更新评分分布图表
        this.updateRatingChart(data.rating_distribution)
        
        // 更新国家分布图表
        this.updateCountryChart(data.country_distribution)
      } catch (error) {
        console.error('获取数据失败:', error)
      }
    },
    updateYearChart(data) {
      const option = {
        title: {
          text: '电影年份分布',
          textStyle: {
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.years,
          axisLabel: {
            color: '#fff'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#fff'
          }
        },
        series: [{
          data: data.counts,
          type: 'bar',
          itemStyle: {
            color: '#409EFF'
          }
        }]
      }
      this.yearChart.setOption(option)
    },
    updateTagChart(data) {
      const option = {
        title: {
          text: '电影标签分布',
          textStyle: {
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'item'
        },
        series: [{
          type: 'pie',
          radius: '50%',
          data: data.tags.map((tag, index) => ({
            name: tag,
            value: data.counts[index]
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      this.tagChart.setOption(option)
    },
    updateRatingChart(data) {
      const option = {
        title: {
          text: '电影评分分布',
          textStyle: {
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.ratings,
          axisLabel: {
            color: '#fff'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#fff'
          }
        },
        series: [{
          data: data.counts,
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#67C23A'
          }
        }]
      }
      this.ratingChart.setOption(option)
    },
    updateCountryChart(data) {
      const option = {
        title: {
          text: '电影国家分布',
          textStyle: {
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: data.countries,
          axisLabel: {
            color: '#fff',
            interval: 0,
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#fff'
          }
        },
        series: [{
          data: data.counts,
          type: 'bar',
          itemStyle: {
            color: '#E6A23C'
          }
        }]
      }
      this.countryChart.setOption(option)
    }
  }
}
</script>

<style scoped>
.statistics-container {
  padding: 20px;
  background-color: #1a1a1a;
  min-height: 100vh;
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
}

.chart-item {
  background-color: #2a2a2a;
  padding: 20px;
  border-radius: 8px;
}

.chart-item h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #fff;
}

.chart {
  height: 400px;
  width: 100%;
}
</style>