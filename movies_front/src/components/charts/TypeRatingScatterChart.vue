<template>
  <div class="chart-container">
    <h2>电影类型、时长与评分之间的关系</h2>
    <div ref="chartContainer" class="chart"></div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'TypeRatingScatterChart',
  props: {
    chartData: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const chartContainer = ref(null)
    let chart = null

    // 生成每个电影类型的固定颜色 - 针对指定的六种类型使用完全不同的颜色
    const typeColors = {
      '剧情': '#2C78E4', // 蓝色
      '纪录片': '#FFCC00', // 明黄色
      '喜剧': '#34C759', // 翠绿色
      '动画': '#FF6BB3', // 粉色
      '动作': '#FF9500', // 橙色
      '爱情': '#FF2D55'  // 粉红色
    }

    // 根据电影类型获取颜色
    const getTypeColor = (type) => {
      return typeColors[type] || '#C4E538'; // 默认颜色
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
      
      // 防止不同系列的点过于重叠，导致多个tooltip出现
      // 为每个类型分配一个小的固定偏移
      const typeOffsets = {};
      let offsetIndex = 0;
      types.forEach((type) => {
        // 使用固定偏移而非随机偏移，确保同一类型的偏移一致
        typeOffsets[type] = {
          x: [0.02, -0.02, 0.01, -0.01, 0.03, -0.03][offsetIndex % 6],
          y: [0.01, -0.01, 0.02, -0.02, 0.015, -0.015][offsetIndex % 6]
        };
        offsetIndex++;
      });
      
      // 处理气泡图数据 - 对相同类型的数据进行聚合
      const bubbleData = [];
      const aggregatedData = {};
      
      // 对数据进行聚合
      data.forEach(item => {
        const [duration, count, rating, type] = item;
        
        // 只处理时长大于等于60的数据
        if (duration < 60) return;
        
        // 处理时长：大于180分钟的归为一类
        const processedDuration = duration > 180 ? 180 : duration;
        
        // 时长分区间：按30分钟分组
        const durationGroup = Math.floor(processedDuration / 30) * 30;
        
        // 评分分区间：按整数分组（如7-8、8-9、9-10）
        const ratingFloor = Math.floor(rating);
        
        const key = `${type}-${durationGroup}-${ratingFloor}`;
        
        // 设置显示的时长区间
        let displayDuration;
        if (durationGroup >= 180) {
          displayDuration = ">180";
        } else {
          displayDuration = `${durationGroup}-${durationGroup + 30}`;
        }
        
        // 设置显示的评分区间
        const displayRating = `${ratingFloor}-${ratingFloor + 1}`;
        
        if (aggregatedData[key]) {
          aggregatedData[key].count += count;
          aggregatedData[key].totalRating += rating * count;
          aggregatedData[key].totalCount += count;
          aggregatedData[key].totalDuration += processedDuration * count;
        } else {
          aggregatedData[key] = {
            type,
            durationGroup,
            displayDuration,
            ratingFloor,
            displayRating,
            count,
            totalRating: rating * count,
            totalCount: count,
            totalDuration: processedDuration * count
          };
        }
      });
      
      // 转换聚合数据为气泡数据
      Object.values(aggregatedData).forEach(item => {
        const avgRating = item.totalRating / item.totalCount;
        const avgDuration = item.totalDuration / item.totalCount;
        
        // 为同类型添加固定偏移，避免完全重叠
        const offset = typeOffsets[item.type] || { x: 0, y: 0 };
        
        bubbleData.push({
          name: item.type,
          value: [
            // 使用平均时长作为x坐标
            avgDuration * (1 + offset.x), 
            // 使用平均评分作为y坐标
            avgRating * (1 + offset.y), 
            item.count, // 电影数量
            item.type
          ],
          // 保存显示用的时长区间和评分区间
          displayDuration: item.displayDuration,
          displayRating: item.displayRating,
          avgRating: avgRating.toFixed(1),
          itemStyle: {
            color: getTypeColor(item.type),
            borderColor: '#fff',
            borderWidth: 1,
            opacity: 0.8,
            shadowBlur: 5,
            shadowColor: 'rgba(0,0,0,0.3)'
          }
        });
      });
      
      // 按类型分组
      const seriesData = types.map(type => {
        return {
          name: type,
          type: 'scatter',
          // 设置气泡大小随数量变化，但更严格地限制最大尺寸
          symbolSize: function(data) {
            // 更保守的气泡大小设置，防止超出边界
            const size = Math.sqrt(data[2]) * 2.8 + 10;
            return Math.min(40, Math.max(10, size)); // 进一步降低最大尺寸
          },
          // 确保边缘点不会超出图表
          symbolOffset: function(data) {
            // 对于y值接近边界的点，添加内向偏移
            const yValue = data[1];
            const xValue = data[0];
            let yOffset = 0;
            let xOffset = 0;
            
            // Y轴边界偏移
            if (yValue <= 7.3) yOffset = 8; // 靠近下边界的点向上偏移更多
            else if (yValue <= 7.5) yOffset = 5; // 稍微靠近下边界的点轻微向上偏移
            else if (yValue >= 9.8) yOffset = -8; // 靠近上边界的点向下偏移更多
            else if (yValue >= 9.6) yOffset = -5; // 稍微靠近上边界的点轻微向下偏移
            
            // X轴边界偏移
            if (xValue <= 65) xOffset = 5; // 靠近左边界的点向右偏移
            
            return [xOffset, yOffset];
          },
          data: bubbleData.filter(item => item.name === type),
          // 气泡效果
          // emphasis: {
          //   focus: 'series',
          //   label: {
          //     show: true,
          //     formatter: function(param) {
          //       // 使用displayDuration来显示时长
          //       const durationText = param.data.displayDuration || param.data.value[0] + '分钟';
          //       return `${param.data.name}\n时长: ${durationText}\n评分: ${param.data.value[1].toFixed(1)}\n电影数: ${param.data.value[2]}部`;
          //     },
          //     position: 'top',
          //     backgroundColor: 'rgba(50,50,50,0.7)',
          //     padding: [4, 8],
          //     borderRadius: 4,
          //     lineHeight: 20,
          //     textStyle: {
          //       color: '#fff',
          //       fontSize: 12
          //     }
          //   },
          //   itemStyle: {
          //     shadowBlur: 20,
          //     shadowColor: 'rgba(0,0,0,0.5)'
          //   }
          // },
          // 为系列设置全局颜色，确保图例颜色与气泡颜色一致
          itemStyle: {
            color: getTypeColor(type)
          }
        };
      });

      // 最终处理：移除bubbleData中的itemStyle，改为继承系列的全局样式
      bubbleData.forEach(item => {
        // 保留原始阴影和边框效果
        const borderStyle = item.itemStyle ? {
          borderColor: item.itemStyle.borderColor || '#fff',
          borderWidth: item.itemStyle.borderWidth || 1,
          opacity: item.itemStyle.opacity || 0.8,
          shadowBlur: item.itemStyle.shadowBlur || 5,
          shadowColor: item.itemStyle.shadowColor || 'rgba(0,0,0,0.3)'
        } : {};
        
        // 移除各自的颜色设置，改为使用系列全局颜色
        item.itemStyle = borderStyle;
      });

      // 图表配置
      const options = {
        backgroundColor: '#2a2a2a',
        title: {
          show: false
        },
        legend: {
          right: '5%',
          top: '3%',
          type: 'scroll',
          orient: 'vertical',
          textStyle: {
            color: '#fff'
          },
          data: types.map(type => ({
            name: type,
            // 设置图例样式，与气泡颜色一致
            itemStyle: {
              color: getTypeColor(type)
            }
          })),
          itemGap: 12, // 增加图例项之间的间距
          itemWidth: 12, // 增加图例标记大小
          itemHeight: 12,
          selectedMode: true,
          padding: 10, // 增加图例内边距
          backgroundColor: 'rgba(40, 40, 40, 0.2)', // 添加轻微背景色
          borderRadius: 5 // 图例边框圆角
        },
        grid: {
          left: '12%', // 再增加左侧边距
          right: '20%', // 增加右侧边距，为图例留出更多空间
          bottom: '12%', // 增加底部边距
          top: '15%',
          containLabel: false // 设置为false，这样坐标轴的标签不会影响图表区域计算
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(50,50,50,0.9)',
          borderColor: '#777',
          borderWidth: 1,
          confine: true, // 确保提示框在图表区域内
          enterable: false, // 鼠标不可进入提示框
          hideDelay: 100, // 增加隐藏延迟，防止闪烁
          triggerOn: 'mousemove', // 仅在鼠标移动时触发
          formatter: function(params) {
            // 使用时长区间和评分区间显示
            return `<div style="font-weight:bold;margin-bottom:5px;">${params.data.name}</div>
                   时长区间：${params.data.displayDuration}分钟<br/>
                   评分区间：${params.data.displayRating}<br/>
                   平均时长：${Math.round(params.data.value[0])}分钟<br/>
                   平均评分：${params.data.avgRating}<br/>
                   电影数量：${params.data.value[2]}部`;
          },
          textStyle: {
            color: '#fff',
            fontSize: 14
          },
          padding: [8, 12]
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
          min: 50,
          max: 180,
          interval: 10, // 设置刻度间隔为10
          minInterval: 10,
          axisLabel: {
            color: '#fff',
            formatter: function(value) {
              if (value === 180) {
                return '>180';
              }
              // 不显示小于60的刻度值
              if (value < 60) {
                return '';
              }
              return value;
            }
          },
          // 在X轴上设置一个分隔区域，标记50-60之间的区域为非数据区
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(40, 40, 40, 0.3)', 'rgba(40, 40, 40, 0)']
            }
          },
          axisLine: {
            lineStyle: {
              color: '#555'
            }
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
          name: '电影评分',
          nameLocation: 'end',
          nameGap: 20, // 增加名称与轴的间距
          nameTextStyle: {
            color: '#fff',
            fontSize: 14,
            padding: [0, 0, 5, 0]
          },
          type: 'value',
          min: 7,
          max: 10,
          interval: 0.5,
          // 增加y轴内边界，为气泡留出更多空间
          boundaryGap: ['25%', '25%'], // 在y轴两端添加更多额外空间
          scale: true, // 启用坐标轴的缩放，使数据点分布更加合理
          axisLine: {
            lineStyle: {
              color: '#555'
            }
          },
          axisLabel: {
            color: '#fff',
            formatter: '{value}',
            margin: 16 // 增加轴标签与轴线之间的间距
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
        // 添加缩放工具
        dataZoom: [
          {
            type: 'inside',
            xAxisIndex: 0,
            filterMode: 'empty'
          },
          {
            type: 'inside',
            yAxisIndex: 0,
            filterMode: 'empty'
          }
        ]
      };

      chart.setOption(options);
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