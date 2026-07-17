<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { ArticleListItem } from '@/api'

defineProps<{ article: ArticleListItem }>()
</script>

<template>
  <article class="article-card">
    <RouterLink :to="`/article/${article.slug}`" class="title-link">
      <h2>{{ article.title }}</h2>
    </RouterLink>
    <p class="summary">{{ article.summary || '暂无摘要' }}</p>
    <div class="meta">
      <span v-if="article.category_name" class="category">
        {{ article.category_name }}
      </span>
      <span class="date">{{ article.created_at.slice(0, 10) }}</span>
    </div>
  </article>
</template>

<style scoped>
.article-card {
  background: #fff;
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 16px;
}
.title-link {
  text-decoration: none;
}
.title-link h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}
.title-link:hover h2 {
  color: #4a90d9;
}
.summary {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 12px 0;
}
.meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #999;
}
.category {
  background: #f0f4f8;
  padding: 2px 10px;
  border-radius: 10px;
}
</style>
