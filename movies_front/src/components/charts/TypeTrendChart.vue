<template>
  <div class="chart-container">
    <h2>2020-2024年电影类型趋势</h2>
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'TypeTrendChart',
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
      // 处理数据：确保所有值都是整数
      const processedSeries = this.chartData.series.map(item => ({
        ...item,
        // 确保数据值是整数
        data: item.data.map(val => Math.round(val)),
        // 增强线条和标记点的样式
        lineStyle: {
          width: 3  // 加粗线条
        },
        // 显示数据点
        symbol: 'circle',
        symbolSize: 8,  // 增大标记点
        // 确保显示标签
        label: {
          show: false
        },
        // 强调时的效果
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          },
          label: {
            show: true,
            formatter: '{c}', // 显示数值
            position: 'top',
            fontSize: 14,
            fontWeight: 'bold'
          },
          lineStyle: {
            width: 5  // 悬浮时线条更粗
          },
          symbolSize: 12  // 悬浮时标记点更大
        }
      }));

      // 获取所有系列名称用于图例
      const legendData = processedSeries.map(item => item.name);

      const option = {
        title: {
          textStyle: {
            color: '#fff',
            fontSize: 18  // 增大标题字体
          },
          left: 'center',
          top: 5
        },
        tooltip: {
          trigger: 'item', // 修改为item，只在鼠标悬停在数据点上时显示
          formatter: function(params) {
            // 确保显示年份、类型和数量
            return `${params.name}年<br/>${params.seriesName}: ${params.value}`;
          },
          textStyle: {
            fontSize: 14  // 增大提示文字
          },
          backgroundColor: 'rgba(50,50,50,0.9)',
          borderColor: '#777',
          borderWidth: 1,
          padding: [5, 10],
          extraCssText: 'box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);'
        },
        legend: {
          type: 'scroll',  // 启用滚动，防止图例过多挤在一起
          orient: 'horizontal', // 水平布局
          data: legendData,
          textStyle: {
            color: '#fff',
            fontSize: 14  // 增大图例文字
          },
          top: 30,
          itemWidth: 25,
          itemHeight: 14,
          itemGap: 20,
          selectedMode: false,  // 设置为false禁用图例点击交互
          selector: false,
          selected: legendData.reduce((acc, name) => {
            acc[name] = true;
            return acc;
          }, {})
        },
        grid: {
          left: '8%',
          right: '5%',
          bottom: '10%',
          top: '80px',  // 给图例更多空间
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.chartData.years,
          axisLabel: {
            color: '#fff',
            fontSize: 14,  // 增大坐标轴标签
            margin: 10     // 增加标签与轴线的距离
          },
          axisLine: {
            lineStyle: {
              color: '#555'
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#fff',
            fontSize: 14,  // 增大坐标轴标签
            margin: 10     // 增加标签与轴线的距离
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
        },
        series: processedSeries,
        color: ['#f56c6c', '#67c23a', '#e6a23c', '#409eff', '#909399']
      };
      
      // 先清除旧的图表实例
      if (this.chart) {
        this.chart.dispose();
      }
      
      // 创建新图表
      this.chart = echarts.init(this.$refs.chartRef);
      this.chart.setOption(option);
      
      // 添加图例点击事件监听器，用于调试
      this.chart.on('legendselectchanged', (params) => {
        console.log('图例选择变化:', params);
        // 由于已禁用图例点击，此事件不应被触发
      });
      
      // 确保窗口大小改变时图表自动调整
      window.removeEventListener('resize', this.handleResize);
      window.addEventListener('resize', this.handleResize);
    },
    
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    }
  },
  watch: {
    chartData: {
      handler() {
        this.updateChart();
      },
      deep: true
    }
  },
  beforeUnmount() {
    // 组件销毁前清除事件监听器
    window.removeEventListener('resize', this.handleResize);
    // 销毁图表实例
    if (this.chart) {
      this.chart.dispose();
    }
  }
}
</script>

<style scoped>
.chart-container {
  background-color: #2a2a2a;
  padding: 20px;  /* 增加内边距 */
  border-radius: 8px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

h2 {
  text-align: center;
  margin-bottom: 20px;  /* 增加下边距 */
  color: #fff;
  font-size: 20px;  /* 增大标题 */
  font-weight: bold;
}

.chart {
  height: 400px;
  width: 100%;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .chart {
    height: 350px;  /* 在小屏幕上调整高度 */
  }
  
  h2 {
    font-size: 18px;  /* 在小屏幕上调整标题大小 */
  }
}
</style> 