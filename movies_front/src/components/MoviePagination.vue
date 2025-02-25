<template>
  <div class="pagination-container">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-count="pageCount"
      layout="prev, pager, next"
      @current-change="handleCurrentChange"
      background
      prev-text="上一页"
      next-text="下一页"
    />
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  total: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update'])

const currentPage = ref(1)
const pageSize = ref(25)

const pageCount = computed(() => {
  return Math.ceil(props.total / pageSize.value)
})

const handleCurrentChange = (val) => {
  currentPage.value = val
  emitUpdate()
}

const emitUpdate = () => {
  emit('update', {
    start: (currentPage.value - 1) * pageSize.value,
    end: currentPage.value * pageSize.value,
    pageSize: pageSize.value
  })
}

// 当总数变化时，重置到第一页
watch(() => props.total, () => {
  currentPage.value = 1
  emitUpdate()
})
</script>

<style lang="scss" scoped>
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  
  :deep(.el-pagination) {
    --el-pagination-bg-color: transparent;
    --el-pagination-hover-color: var(--el-color-primary);
    --el-pagination-button-color: #fff;
    --el-pagination-text-color: #ccc;
    
    .el-pager {
      li {
        background-color: transparent;
        color: #ccc;
        min-width: 32px;
        
        &.is-active {
          background-color: var(--el-color-primary);
          color: #fff;
        }
        
        &:hover {
          color: var(--el-color-primary);
        }
      }
    }
    
    .btn-prev,
    .btn-next {
      background-color: transparent;
      color: #ccc;
      
      &:hover {
        color: var(--el-color-primary);
      }
      
      &:disabled {
        background-color: transparent;
        color: #666;
      }
    }
  }
}
</style> 