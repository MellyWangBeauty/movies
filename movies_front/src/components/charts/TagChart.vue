<template>
  <div class="chart-container">
    <h2>不同类型电影数量对比</h2>
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'TagChart',
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
      // 处理数据，确保标签没有斜杠，并组合成饼图需要的格式
      let pieData = [];
      
      // 先分割每个标签，然后合并计数
      this.chartData.tags.forEach((tag, index) => {
        // 如果标签包含斜杠，则拆分
        if (tag.includes('/')) {
          const subTags = tag.split('/');
          // 每个子标签都保持原始标签的完整计数值
          const originalValue = this.chartData.counts[index];
          
          subTags.forEach(subTag => {
            const trimmedTag = subTag.trim();
            if (trimmedTag) {
              pieData.push({
                name: trimmedTag,
                value: originalValue  // 使用原始完整计数值
              });
            }
          });
        } else {
          // 没有斜杠，直接使用
          pieData.push({
            name: tag.trim(),
            value: this.chartData.counts[index]
          });
        }
      });
      
      // 合并同名标签的数据
      const mergedData = [];
      const tagMap = new Map();
      
      pieData.forEach(item => {
        if (tagMap.has(item.name)) {
          // 如果已经存在该标签，合并值
          const existingItem = tagMap.get(item.name);
          existingItem.value += item.value;
        } else {
          // 否则添加新标签
          const newItem = { ...item };
          mergedData.push(newItem);
          tagMap.set(item.name, newItem);
        }
      });
      
      // 排序并取前12个标签（减少标签数量以适应更大的字体）
      const sortedData = mergedData.sort((a, b) => b.value - a.value)
        .slice(0, 12)
        .map(item => ({
          ...item,
          value: Math.round(item.value) // 确保所有值都是整数
        }));
      
      const option = {
        title: {
          textStyle: {
            color: '#fff',
            fontSize: 18  // 增加标题字体大小
          },
          left: 'center',
          top: 5
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            // 自定义提示框格式，确保显示整数
            return `${params.seriesName}<br/>${params.name}: ${params.value} (${params.percent}%)`;
          },
          textStyle: {
            fontSize: 14
          }
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          left: '60%',  // 调整左侧边距，给饼图更多空间
          top: 'middle', // 垂直居中
          itemWidth: 12, // 增加图例项宽度
          itemHeight: 12, // 增加图例项高度
          itemGap: 10,   // 增加图例项间距
          textStyle: {
            color: '#fff',
            fontSize: 14,  // 增加图例字体大小
            lineHeight: 20
          },
          formatter: function(name) {
            // 找到对应数据项
            const item = sortedData.find(item => item.name === name);
            if (item) {
              // 返回 "标签名: 数量 (百分比%)"
              const total = sortedData.reduce((sum, item) => sum + item.value, 0);
              const percent = ((item.value / total) * 100).toFixed(1);
              return `${name}: ${item.value} (${percent}%)`;
            }
            return name;
          }
        },
        grid: {
          top: '10%',
          bottom: '10%',
          containLabel: true
        },
        series: [{
          name: '电影类型',
          type: 'pie',
          radius: '55%',  // 增加饼图半径
          center: ['32%', '55%'],  // 调整位置，给右侧图例留出更多空间
          label: {
            show: false  // 不在饼图上显示标签
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            },
            label: {
              show: true,
              fontSize: 14,  // 增加强调时的标签字体大小
              fontWeight: 'bold'
            }
          },
          data: sortedData
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
  font-size: 20px;  /* 增大标题字体 */
  font-weight: bold;
}

.chart {
  height: 380px;  /* 增加图表高度 */
  width: 100%;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .chart {
    height: 300px;  /* 在小屏幕上调整高度 */
  }
  
  h2 {
    font-size: 18px;  /* 在小屏幕上调整标题大小 */
  }
}
</style> 