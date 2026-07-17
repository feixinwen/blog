<script setup lang="ts">
const props = defineProps<{
  page: number
  total: number
  pageSize: number
}>()

const emit = defineEmits<{
  change: [page: number]
}>()

const totalPages = () => Math.ceil(props.total / props.pageSize)

const go = (p: number) => {
  if (p >= 1 && p <= totalPages()) emit('change', p)
}
</script>

<template>
  <div class="pagination" v-if="totalPages() > 1">
    <button :disabled="page <= 1" @click="go(page - 1)">上一页</button>
    <span
      v-for="p in totalPages()"
      :key="p"
      :class="{ active: p === page }"
      @click="go(p)"
    >
      {{ p }}
    </span>
    <button :disabled="page >= totalPages()" @click="go(page + 1)">下一页</button>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 24px;
}
.pagination span,
.pagination button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  padding: 0 10px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #555;
}
.pagination span.active {
  background: #4a90d9;
  color: #fff;
  border-color: #4a90d9;
}
.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
