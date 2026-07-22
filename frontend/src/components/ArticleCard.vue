<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { ArticleListItem } from '@/api'

defineProps<{ article: ArticleListItem }>()
</script>

<template>
  <article class="card">
    <RouterLink :to="`/article/${article.slug}`" class="title">
      {{ article.title }}
    </RouterLink>

    <div class="meta">
      <span>发表于 {{ article.created_at.slice(0, 10) }}</span>
      <span class="meta-divider">|</span>
      <span>阅读 {{ article.read_count }}</span>
      <span class="meta-divider">|</span>
      <span>评论 {{ article.comment_count }}</span>
    </div>

    <hr class="sep" />

    <p class="summary">{{ article.summary || '暂无摘要' }}</p>

    <RouterLink :to="`/article/${article.slug}`" class="read-more">阅读全文 &raquo;</RouterLink>
  </article>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: 8px;
  padding: 32px 36px 24px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.title {
  font-size: 21px;
  font-weight: 600;
  color: #222;
  text-decoration: none;
  line-height: 1.4;
}
.title:hover {
  color: #4a90d9;
}
.meta {
  margin-top: 10px;
  font-size: 13px;
  color: #999;
  display: flex;
  gap: 8px;
  align-items: center;
}
.meta-divider {
  color: #ddd;
}
.sep {
  border: none;
  border-top: 1px solid #f0f0f0;
  margin: 14px 0;
}
.summary {
  font-size: 14px;
  color: #666;
  line-height: 1.8;
  margin: 0 0 14px;
}
.read-more {
  font-size: 14px;
  color: #4a90d9;
  text-decoration: none;
}
.read-more:hover {
  text-decoration: underline;
}
</style>
