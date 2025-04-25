<template>
  <div class="chart-container">
    <h2>不同地区电影平均评分对比</h2>
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'CountryRatingChart',
  props: {
    chartData: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      chart: null
    }
  },
  mounted() {
    this.initChart()
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chartRef)
      this.updateChart()
      
      // 添加窗口大小改变时自动调整图表大小的功能
      window.addEventListener('resize', this.handleResize)
    },
    handleResize() {
      if (this.chart) {
        this.chart.resize()
      }
    },
    updateChart() {
      // 确保数据有序且格式正确
      const data = this.processData()
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: (params) => {
            const country = params[0].name
            const rating = params[0].value
            const count = this.chartData.movie_counts[params[0].dataIndex]
            return `${country}<br/>平均评分: ${rating}<br/>电影数量: ${count}`
          },
          textStyle: {
            fontSize: 14
          },
          backgroundColor: 'rgba(50,50,50,0.9)',
          borderColor: '#777',
          borderWidth: 1,
          padding: [5, 10],
          extraCssText: 'box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        xAxis: [{
          type: 'category',
          data: data.countries,
          axisLabel: {
            interval: 0,
            rotate: 0,
            color: '#fff',
            fontSize: 12,
            width: 60,
            overflow: 'truncate'
          },
          axisLine: {
            lineStyle: {
              color: '#555'
            }
          }
        }],
        yAxis: [{
          type: 'value',
          name: '平均评分',
          nameTextStyle: {
            color: '#fff',
            fontSize: 14
          },
          min: Math.floor(Math.min(...data.ratings) * 0.9),
          max: Math.ceil(Math.max(...data.ratings) * 1.1),
          axisLabel: {
            color: '#fff',
            fontSize: 12,
            formatter: '{value}'
          },
          axisLine: {
            lineStyle: {
              color: '#555'
            }
          },
          splitLine: {
            lineStyle: {
              color: '#333'
            }
          }
        }],
        series: [
          {
            name: '平均评分',
            type: 'bar',
            data: data.ratings.map((value, index) => {
              return {
                value: value,
                itemStyle: {
                  color: this.getItemColor(index)
                }
              };
            }),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            barWidth: '65%',
            label: {
              show: true,
              position: 'top',
              formatter: '{c}',
              color: '#fff',
              fontSize: 12
            }
          }
        ]
      }
      this.chart.setOption(option)
    },
    processData() {
      // 确保数据按照评分从高到低排序
      const indices = Array.from(
        { length: this.chartData.countries.length },
        (_, i) => i
      )
      
      // 按评分从高到低排序
      indices.sort((a, b) => this.chartData.avg_ratings[b] - this.chartData.avg_ratings[a])
      
      // 选择前8个国家/地区
      const topIndices = indices.slice(0, 8)
      
      // 整理数据
      const countries = topIndices.map(i => this.chartData.countries[i])
      const ratings = topIndices.map(i => this.chartData.avg_ratings[i])
      
      return {
        countries,
        ratings
      }
    },
    
    getItemColor(index) {
      // 为每个柱子定义不同的颜色
      const colors = [
        '#3D5A80', // 蓝色
        '#4ECDC4', // 青色
        '#FFD166', // 黄色
        '#6A0572', // 紫色
        '#1A936F', // 绿色
        '#FF6B6B', // 红色
        '#F18F01', // 橙色
        '#8338EC'  // 紫色
      ];
      
      return colors[index % colors.length];
    }
  },
  watch: {
    chartData: {
      handler() {
        this.updateChart()
      },
      deep: true
    }
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    if (this.chart) {
      this.chart.dispose()
    }
  }
}
</script>

<style scoped>
.chart-container {
  background-color: #2a2a2a;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
}

.chart {
  height: 400px;
  width: 100%;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .chart {
    height: 350px;
  }
  
  h2 {
    font-size: 18px;
  }
}
</style> 