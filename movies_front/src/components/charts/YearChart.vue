<template>
  <div class="chart-container">
    <h2>年份分布</h2>
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'YearChart',
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
      window.addEventListener('resize', () => {
        this.chart.resize()
      })
    },
    updateChart() {
      const option = {
        title: {
          textStyle: {
            color: '#fff',
            fontSize: 16
          },
          left: 'center',
          top: 5
        },
        tooltip: {
          trigger: 'axis'
        },
        grid: {
          left: '8%',
          right: '5%',
          bottom: '10%',
          top: '20%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.chartData.years,
          axisLabel: {
            color: '#fff',
            fontSize: 12,
            margin: 8,
            rotate: 45,
            interval: 'auto'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#fff',
            fontSize: 12
          }
        },
        series: [{
          data: this.chartData.counts,
          type: 'bar',
          itemStyle: {
            color: '#409EFF'
          }
        }]
      }
      
      this.chart.setOption(option)
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
    // 组件销毁前清除事件监听器
    window.removeEventListener('resize', this.chart.resize)
    // 销毁图表实例
    this.chart.dispose()
  }
}
</script>

<style scoped>
.chart-container {
  background-color: #2a2a2a;
  padding: 15px;
  border-radius: 8px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

h2 {
  text-align: center;
  margin-bottom: 15px;
  color: #fff;
  font-size: 18px;
}

.chart {
  height: 350px;
  width: 100%;
  box-sizing: border-box;
}
</style> 