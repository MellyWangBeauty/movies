<template>
  <div class="chart-container">
    <h2>不同地区电影评分对比</h2>
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
            const count = data.counts[params[0].dataIndex]
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
          top: '20%',
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
          min: 7.5,
          max: 8.7,
          interval: 0.2,
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
      // 对国家/地区进行分类和处理
      let processedData = this.groupAndProcessCountries();
      
      // 按评分从高到低排序
      processedData.sort((a, b) => b.rating - a.rating);
      
      // 不再限制为前8个，而是使用所有处理后的目标区域
      const topRegions = processedData;
      
      // 整理数据
      const countries = topRegions.map(item => item.name);
      const ratings = topRegions.map(item => item.rating);
      const counts = topRegions.map(item => item.count);
      
      return {
        countries,
        ratings,
        counts
      }
    },
    
    groupAndProcessCountries() {
      // 指定要比较的区域列表
      const targetRegions = ['中国大陆', '中国香港', '中国台湾', '美国', '日本', '韩国', '英国', '法国'];
      
      // 按区域分类并合并数据
      const regionMap = {
        '中国大陆': '中国大陆',
        '中国香港': '中国香港',
        '中国台湾': '中国台湾',
        '香港': '中国香港',
        '台湾': '中国台湾',
        '中国': '中国大陆',
        '美国': '美国',
        '日本': '日本',
        '韩国': '韩国',
        '英国': '英国',
        '法国': '法国'
      };
      
      const regions = {};
      
      // 初始化目标区域
      targetRegions.forEach(region => {
        regions[region] = {
          name: region,
          rating: 0,
          count: 0,
          total: 0
        };
      });
      
      // 遍历原始数据，按区域分组，只处理目标区域
      for (let i = 0; i < this.chartData.countries.length; i++) {
        let country = this.chartData.countries[i];
        let rating = this.chartData.avg_ratings[i];
        let count = this.chartData.movie_counts[i];
        
        // 尝试匹配区域
        for (const [pattern, region] of Object.entries(regionMap)) {
          if (country.includes(pattern) && targetRegions.includes(region)) {
            // 累加该区域的评分和电影数量
            regions[region].total += rating * count;
            regions[region].count += count;
            break;
          }
        }
      }
      
      // 计算每个区域的平均评分
      for (const region in regions) {
        if (regions[region].count > 0) {
          regions[region].rating = parseFloat((regions[region].total / regions[region].count).toFixed(1));
        }
      }
      
      // 过滤掉没有数据的区域
      return Object.values(regions).filter(region => region.count > 0);
    },
    
    getItemColor(index) {
      // 为每个特定区域设置固定颜色
      const regionColors = {
        '中国大陆': '#FF6B6B', // 红色
        '中国香港': '#FF9E80', // 橙红色
        '中国台湾': '#EF476F', // 粉红色
        '美国': '#3D5A80', // 深蓝色
        '日本': '#FFD166', // 黄色
        '韩国': '#06D6A0', // 绿松石色
        '英国': '#4ECDC4', // 青色
        '法国': '#8338EC'  // 紫色
      };
      
      // 使用固定颜色映射
      const region = this.processData().countries[index];
      return regionColors[region] || '#78909C'; // 默认颜色为灰色
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
  margin-bottom: 30px;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
}

.chart {
  height: 450px;
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