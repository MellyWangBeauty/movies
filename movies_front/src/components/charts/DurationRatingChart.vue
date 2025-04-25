<template>
  <div class="chart-container">
    <h2>电影时长与评分关系</h2>
    <div ref="chartContainer" class="chart"></div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'DurationRatingChart',
  props: {
    chartData: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const chartContainer = ref(null)
    let chart = null

    // 根据评分生成渐变色
    const getRatingColor = (rating) => {
      // 评分范围一般在7.0-9.5之间
      // 根据评分生成从黄色到红色的渐变
      const normalizedRating = Math.min(1, Math.max(0, (rating - 7) / 2.5))
      const r = Math.floor(255)
      const g = Math.floor(255 * (1 - normalizedRating * 0.8))
      const b = Math.floor(100 * (1 - normalizedRating))
      return `rgb(${r}, ${g}, ${b})`
    }

    const initChart = () => {
      if (!chartContainer.value) return

      // 销毁旧实例
      if (chart) {
        chart.dispose()
      }

      // 初始化图表
      chart = echarts.init(chartContainer.value)
      updateChart()
    }

    const updateChart = () => {
      if (!chart || !props.chartData) return

      const { categories, avg_ratings, movie_counts } = props.chartData
      
      // 确保数据类型正确
      const formattedRatings = avg_ratings.map(rating => parseFloat(rating).toFixed(1))
      const formattedCounts = movie_counts.map(count => parseInt(count))

      // 图表配置
      const options = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const ratingData = params[0]
            const countData = params[1]
            return `${ratingData.name}<br/>
                   平均评分: <strong>${ratingData.value}</strong><br/>
                   电影数量: <strong>${countData.value}</strong>`
          },
          backgroundColor: 'rgba(50,50,50,0.9)',
          borderColor: '#777',
          borderWidth: 1,
          textStyle: {
            color: '#fff',
            fontSize: 14
          },
          padding: [5, 10],
          extraCssText: 'box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);'
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '10%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: categories,
          axisLabel: {
            fontSize: 12,
            interval: 0,
            rotate: 0,
            color: '#fff'
          },
          axisLine: {
            lineStyle: {
              color: '#555'
            }
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '平均评分',
            min: function(value) {
              return Math.floor(value.min - 0.5)
            },
            max: function(value) {
              return Math.ceil(value.max + 0.5)
            },
            position: 'left',
            axisLabel: {
              formatter: '{value}',
              fontSize: 12,
              color: '#fff'
            },
            nameTextStyle: {
              color: '#fff',
              fontSize: 14
            },
            axisLine: {
              show: true,
              lineStyle: {
                color: '#555'
              }
            },
            splitLine: {
              show: true,
              lineStyle: {
                type: 'dashed',
                color: '#333'
              }
            }
          },
          {
            type: 'value',
            name: '电影数量',
            position: 'right',
            axisLabel: {
              formatter: '{value}',
              fontSize: 12,
              color: '#fff'
            },
            nameTextStyle: {
              color: '#fff',
              fontSize: 14
            },
            axisLine: {
              show: true,
              lineStyle: {
                color: '#555'
              }
            },
            splitLine: {
              show: false
            }
          }
        ],
        series: [
          {
            name: '平均评分',
            type: 'bar',
            yAxisIndex: 0,
            data: formattedRatings,
            barWidth: '40%',
            itemStyle: {
              color: function(params) {
                return getRatingColor(params.value)
              },
              borderRadius: [4, 4, 0, 0]
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              show: true,
              position: 'top',
              fontSize: 12,
              formatter: '{c}',
              color: '#fff'
            }
          },
          {
            name: '电影数量',
            type: 'line',
            yAxisIndex: 1,
            data: formattedCounts,
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: {
              color: '#5470c6',
              width: 2
            },
            itemStyle: {
              color: '#5470c6'
            },
            emphasis: {
              scale: true
            },
            label: {
              show: true,
              position: 'top',
              fontSize: 12,
              formatter: '{c}',
              offset: [0, -5],
              color: '#fff'
            }
          }
        ]
      }

      chart.setOption(options)
    }

    const handleResize = () => {
      if (chart) {
        chart.resize()
      }
    }

    watch(() => props.chartData, () => {
      updateChart()
    }, { deep: true })

    onMounted(() => {
      initChart()
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      if (chart) {
        chart.dispose()
        chart = null
      }
      window.removeEventListener('resize', handleResize)
    })

    return {
      chartContainer
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