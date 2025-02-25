<template>
  <div class="movie-filter">
    <div class="filter-section">
      <div class="filter-row">
        <span class="label">类型</span>
        <div class="options">
          <span 
            v-for="tag in tags" 
            :key="tag"
            :class="['option', { active: selectedTags.includes(tag) }]"
            @click="toggleTag(tag)"
          >{{ tag }}</span>
        </div>
      </div>

      <div class="filter-row">
        <span class="label">年代</span>
        <div class="options">
          <span 
            v-for="year in years" 
            :key="year"
            :class="['option', { active: selectedYears.includes(year) }]"
            @click="toggleYear(year)"
          >{{ year }}</span>
        </div>
      </div>

      <div class="filter-row">
        <span class="label">地区</span>
        <div class="options">
          <span 
            v-for="country in countries" 
            :key="country"
            :class="['option', { active: selectedCountries.includes(country) }]"
            @click="toggleCountry(country)"
          >{{ country }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  movies: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['filter'])

// 预设选项
const tags = ['全部', '剧情', '喜剧', '动作', '爱情', '科幻', '动画', '悬疑', '惊悚', '恐怖', '纪录片']
const years = ['全部', '2024', '2023', '2022', '2021', '2020', '2010年代', '2000年代', '更早']
const countries = ['全部', '中国大陆', '中国香港', '中国台湾', '美国', '日本', '韩国', '英国', '法国', '其他']

// 选中的值
const selectedTags = ref(['全部'])
const selectedYears = ref(['全部'])
const selectedCountries = ref(['全部'])

// 切换选项的方法
const toggleOption = (value, selectedArray, category) => {
  const index = selectedArray.value.indexOf(value)
  if (value === '全部') {
    selectedArray.value = ['全部']
  } else {
    // 如果已经选中了"全部"，先移除它
    const allIndex = selectedArray.value.indexOf('全部')
    if (allIndex > -1) {
      selectedArray.value.splice(allIndex, 1)
    }
    
    if (index > -1) {
      selectedArray.value.splice(index, 1)
      // 如果没有选中任何选项，自动选中"全部"
      if (selectedArray.value.length === 0) {
        selectedArray.value = ['全部']
      }
    } else {
      selectedArray.value.push(value)
    }
  }
  
  filterMovies()
}

const toggleTag = (tag) => toggleOption(tag, selectedTags, 'tags')
const toggleYear = (year) => toggleOption(year, selectedYears, 'years')
const toggleCountry = (country) => toggleOption(country, selectedCountries, 'country')

// 筛选电影
const filterMovies = () => {
  let filteredMovies = [...props.movies]
  
  if (!selectedTags.value.includes('全部')) {
    filteredMovies = filteredMovies.filter(movie => 
      selectedTags.value.some(tag => movie.tags?.includes(tag))
    )
  }
  
  if (!selectedYears.value.includes('全部')) {
    filteredMovies = filteredMovies.filter(movie => {
      const movieYear = parseInt(movie.years)
      return selectedYears.value.some(year => {
        if (year.includes('年代')) {
          const decade = parseInt(year.slice(0, 4))
          return movieYear >= decade && movieYear < decade + 10
        } else if (year === '更早') {
          return movieYear < 2000
        } else {
          return movie.years === year
        }
      })
    })
  }
  
  if (!selectedCountries.value.includes('全部')) {
    filteredMovies = filteredMovies.filter(movie =>
      selectedCountries.value.some(country => movie.country?.includes(country))
    )
  }
  
  emit('filter', filteredMovies)
}

// 监听电影数据变化
watch(() => props.movies, filterMovies, { immediate: true })
</script>

<style lang="scss" scoped>
.movie-filter {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;

  .filter-section {
    .filter-row {
      display: flex;
      align-items: flex-start;
      margin-bottom: 15px;
      
      &:last-child {
        margin-bottom: 0;
      }

      .label {
        flex-shrink: 0;
        width: 40px;
        color: #999;
        font-size: 14px;
        line-height: 24px;
      }

      .options {
        flex: 1;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;

        .option {
          padding: 3px 12px;
          border-radius: 15px;
          font-size: 14px;
          color: #fff;
          cursor: pointer;
          transition: all 0.3s;
          background: transparent;

          &:hover {
            background: rgba(255, 255, 255, 0.1);
          }

          &.active {
            background: var(--el-color-primary);
            color: #fff;
          }
        }
      }
    }
  }
}
</style> 