<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { fetchCategories, fetchTags, type Category, type Tag } from '@/api'

const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])

onMounted(async () => {
  const [catRes, tagRes] = await Promise.all([fetchCategories(), fetchTags()])
  categories.value = catRes.data
  tags.value = tagRes.data
})
</script>

<template>
  <aside class="sidebar">
    <!-- 个人信息卡片 -->
    <div class="sidebar-card">
      <h3>关于博主</h3>
      <p>全栈开发者，热爱 Python 和 Vue。</p>
    </div>

    <!-- 分类 -->
    <div class="sidebar-card">
      <h3>文章分类</h3>
      <ul>
        <li v-for="cat in categories" :key="cat.id">
          <RouterLink :to="`/category/${cat.slug}`">
            {{ cat.name }}
            <span class="count">{{ cat.article_count }}</span>
          </RouterLink>
        </li>
        <li v-if="categories.length === 0" class="empty">暂无分类</li>
      </ul>
    </div>

    <!-- 标签云 -->
    <div class="sidebar-card">
      <h3>标签</h3>
      <div class="tag-cloud">
        <RouterLink
          v-for="tag in tags"
          :key="tag.id"
          :to="`/tag/${tag.slug}`"
          class="tag-item"
        >
          {{ tag.name }}
        </RouterLink>
        <span v-if="tags.length === 0" class="empty">暂无标签</span>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 280px;
  flex-shrink: 0;
}
.sidebar-card {
  background: #fff;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 16px;
}
.sidebar-card h3 {
  font-size: 16px;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}
.sidebar-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar-card li {
  margin-bottom: 8px;
}
.sidebar-card li a {
  color: #555;
  text-decoration: none;
  display: flex;
  justify-content: space-between;
}
.sidebar-card li a:hover {
  color: #4a90d9;
}
.count {
  color: #999;
  font-size: 13px;
}
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag-item {
  background: #f0f4f8;
  color: #555;
  padding: 4px 12px;
  border-radius: 14px;
  font-size: 13px;
  text-decoration: none;
}
.tag-item:hover {
  background: #4a90d9;
  color: #fff;
}
.empty {
  color: #999;
  font-size: 14px;
}
</style>
