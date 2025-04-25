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
      
      // 处理数据：将评分划分为区间，将时长大于200的归为一类
      const processedData = data.map(item => {
        // 确保item是有效的
        if (!item || item.length < 4) return null;
        
        const [duration, count, rating, type] = item;
        
        // 时长处理
        let durationValue = parseFloat(duration);
        if (isNaN(durationValue)) durationValue = 100; // 默认值
        
        // 将时长划分为区间
        let durationRange;
        let processedDuration;
        
        if (durationValue < 90) {
          durationRange = '<90';
          processedDuration = 85; // 区间中点
        } else if (durationValue < 120) {
          durationRange = '90-120';
          processedDuration = 105;
        } else if (durationValue < 150) {
          durationRange = '120-150';
          processedDuration = 135;
        } else if (durationValue < 180) {
          durationRange = '150-180';
          processedDuration = 165;
        } else if (durationValue < 200) {
          durationRange = '180-200';
          processedDuration = 190;
        } else {
          durationRange = '>200';
          processedDuration = 210;
        }
        
        // 评分处理
        let ratingValue = parseFloat(rating);
        if (isNaN(ratingValue)) ratingValue = 8.0; // 默认评分
        
        // 评分区间
        let ratingRange;
        if (ratingValue < 8.0) ratingRange = '7.0-7.9';
        else if (ratingValue < 9.0) ratingRange = '8.0-8.9';
        else ratingRange = '9.0-10.0';
        
        return [processedDuration, count, ratingValue, type, ratingRange, durationRange];
      }).filter(item => item !== null);
      
      // 对数据进行聚合
      const typeRatingDurationMap = {};
      
      processedData.forEach(item => {
        const [duration, count, rating, type, ratingRange, durationRange] = item;
        const key = `${type}-${ratingRange}-${durationRange}`;
        
        if (key in typeRatingDurationMap) {
          const existingItem = typeRatingDurationMap[key];
          // 累加电影数量
          existingItem[1] += count;
          // 更新平均评分 (加权平均)
          const totalMovies = existingItem[6] + count;
          existingItem[2] = (existingItem[2] * existingItem[6] + rating * count) / totalMovies;
          // 更新合并的电影总数
          existingItem[6] = totalMovies;
        } else {
          // 创建新条目: [duration中点值, 数量, 平均评分, 类型, 评分区间, 时长区间, 累计电影数]
          typeRatingDurationMap[key] = [duration, count, rating, type, ratingRange, durationRange, count];
        }
      });
      
      // 将聚合结果转为数组
      const aggregatedData = Object.values(typeRatingDurationMap);
      
      console.log('聚合后的数据:', aggregatedData); // 调试
      
      // 散点图系列
      const seriesData = types.map(type => {
        const typeData = aggregatedData.filter(item => item[3] === type);
        console.log(`${type} 数据:`, typeData); // 调试
        
        return {
          name: type,
          type: 'scatter',
          symbolSize: function(data) {
            // 根据电影数量调整大小 (最小10, 最大40)
            return Math.min(40, Math.max(10, Math.sqrt(data[1]) * 3 + 5));
          },
          data: typeData.map(item => {
            // 获取时长区间的基础位置
            const xMapping = {
              '<90': 0,
              '90-120': 1,
              '120-150': 2,
              '150-180': 3,
              '180-200': 4,
              '>200': 5
            };
            
            // 加入随机偏移，使同类点分散开
            const baseX = xMapping[item[5]];
            // 在X轴基础位置上增加一定的随机偏移，使点分散
            const randomOffset = (Math.random() - 0.5) * 0.8; 
            
            // 在Y轴上也增加一些随机偏移
            const yValue = item[1] + (Math.random() - 0.5) * 2;
            
            // 复制数组并修改
            const newItem = [...item];
            newItem[0] = baseX + randomOffset; // 修改x值
            newItem[1] = yValue; // 修改y值，增加随机性
            return newItem;
          }),
          emphasis: {
            focus: 'series',
            label: {
              show: true,
              formatter: function(param) {
                return `${param.data[3]}\n时长：${param.data[5]}\n评分：${param.data[4]}\n电影数：${param.data[6]}部`;
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
              return getRatingColor(params.data[2]);
            },
            opacity: 0.8,
            borderColor: '#fff',
            borderWidth: 1
          }
        };
      });

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
                   时长区间：${params.data[5]}<br/>
                   电影数量：${params.data[6]}部<br/>
                   评分区间：${params.data[4]}<br/>
                   平均评分：${params.data[2].toFixed(1)}`;
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
          type: 'category',
          data: ['<90', '90-120', '120-150', '150-180', '180-200', '>200'],
          boundaryGap: true,
          axisLabel: {
            color: '#fff'
          },
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(50, 50, 50, 0.2)', 'rgba(40, 40, 40, 0.2)']
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