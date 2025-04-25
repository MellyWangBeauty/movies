<template>
  <div class="chart-container">
    <h2>电影类型、时长与评之间关系</h2>
    <div ref="chartContainer" class="chart"></div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'TypeDurationRatingChart',
  props: {
    chartData: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const chartContainer = ref(null)
    let chart = null

    // 根据评分生成颜色
    const getRatingColor = (rating) => {
      // 评分范围一般在7.0-9.5之间
      // 生成从蓝色到红色的渐变
      const normalizedRating = Math.min(1, Math.max(0, (rating - 7) / 2.5))
      const r = Math.floor(255 * normalizedRating)
      const g = Math.floor(150 * (1 - normalizedRating))
      const b = Math.floor(255 * (1 - normalizedRating))
      return `rgba(${r}, ${g}, ${b}, 0.8)`
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

      const { types, data } = props.chartData
      
      // 生成图例数据
      const legendData = types.map(type => ({ name: type }))
      
      // 散点图序列数据
      const seriesData = types.map((type, index) => {
        return {
          name: type,
          type: 'scatter',
          symbolSize: function(data) {
            // 根据评分调整点的大小 (7-10分映射到10-25大小)
            return (data[2] - 7) * 5 + 10
          },
          data: data.filter(item => item[3] === type),
          emphasis: {
            focus: 'series',
            label: {
              show: true,
              formatter: function(param) {
                return `${param.data[3]}\n时长：${param.data[0]}分钟\n评分：${param.data[2]}`
              },
              position: 'top',
              backgroundColor: 'rgba(50,50,50,0.7)',
              padding: [4, 8],
              borderRadius: 3,
              textStyle: {
                color: '#fff',
                fontSize: 12
              }
            }
          },
          itemStyle: {
            color: function(params) {
              return getRatingColor(params.data[2])
            },
            opacity: 0.8,
            borderColor: '#fff',
            borderWidth: 1
          }
        }
      })

      // 图表配置
      const options = {
        backgroundColor: '#2a2a2a',
        color: ['#dd6b66', '#759aa0', '#e69d87', '#8dc1a9', '#ea7e53', '#eedd78', '#73a373', '#73b9bc', '#7289ab', '#91ca8c', '#f49f42'],
        title: {
          show: false
        },
        legend: {
          right: '10%',
          top: '3%',
          type: 'scroll',
          textStyle: {
            color: '#fff'
          },
          data: types
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '10%',
          top: '15%',
          containLabel: true
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(50,50,50,0.9)',
          borderColor: '#777',
          borderWidth: 1,
          formatter: function(params) {
            return `电影类型：${params.data[3]}<br/>
                   时长：${params.data[0]}分钟<br/>
                   数量：${params.data[1]}<br/>
                   评分：${params.data[2]}`
          },
          textStyle: {
            color: '#fff',
            fontSize: 14
          },
          padding: [5, 10]
        },
        xAxis: {
          name: '电影时长（分钟）',
          nameLocation: 'middle',
          nameGap: 30,
          nameTextStyle: {
            color: '#fff',
            fontSize: 14
          },
          type: 'value',
          scale: true,
          min: 80,
          axisLine: {
            lineStyle: {
              color: '#555'
            }
          },
          axisLabel: {
            color: '#fff',
            formatter: '{value}'
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: '#333',
              type: 'dashed'
            }
          }
        },
        yAxis: {
          name: '电影数量',
          nameLocation: 'end',
          nameGap: 15,
          nameTextStyle: {
            color: '#fff',
            fontSize: 14,
            padding: [0, 0, 5, 0]
          },
          type: 'value',
          axisLine: {
            lineStyle: {
              color: '#555'
            }
          },
          axisLabel: {
            color: '#fff',
            formatter: '{value}'
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: '#333',
              type: 'dashed'
            }
          }
        },
        series: seriesData,
        visualMap: [
          {
            show: true,
            type: 'continuous',
            seriesIndex: 0,
            dimension: 2,
            min: 7,
            max: 9.5,
            inRange: {
              color: ['#2575fc', '#e14fad', '#ff4b00']
            },
            left: 'right',
            bottom: 10,
            orient: 'horizontal',
            text: ['高分', '低分'],
            textStyle: {
              color: '#fff'
            },
            formatter: function(value) {
              return value.toFixed(1) + '分'
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
  height: 500px;
  width: 100%;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .chart {
    height: 400px;
  }
  
  h2 {
    font-size: 18px;
  }
}
</style> 