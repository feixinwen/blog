<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

import { fetchArticle, type ArticleDetail } from '@/api'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Sidebar from '@/components/Sidebar.vue'
import CommentSection from '@/components/CommentSection.vue'

const route = useRoute()
const article = ref<ArticleDetail | null>(null)

// 配置 marked 代码高亮
marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
})

onMounted(async () => {
  const slug = route.params.slug as string
  const res = await fetchArticle(slug)
  article.value = res.data
})

function renderMarkdown(md: string): string {
  return marked.parse(md) as string
}
</script>

<template>
  <div class="article-layout">
    <AppHeader />
    <div class="main-body">
      <main class="content">
        <div v-if="article" class="article-detail">
          <h1>{{ article.title }}</h1>
          <div class="meta">
            <span v-if="article.category_name">{{ article.category_name }}</span>
            <span>{{ article.created_at.slice(0, 10) }}</span>
          </div>
          <div class="markdown-body" v-html="renderMarkdown(article.content)"></div>
        </div>
        <CommentSection v-if="article" :article-id="article.id" />
      </main>
      <Sidebar />
    </div>
    <AppFooter />
  </div>
</template>

<style scoped>
.article-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f6f7;
}
.main-body {
  max-width: 1100px;
  margin: 24px auto;
  display: flex;
  gap: 24px;
  flex: 1;
  width: 100%;
  padding: 0 20px;
  box-sizing: border-box;
}
.content {
  flex: 1;
  min-width: 0;
}
.article-detail {
  background: #fff;
  border-radius: 6px;
  padding: 30px;
}
.article-detail h1 {
  font-size: 26px;
  margin: 0 0 12px 0;
  color: #222;
}
.meta {
  font-size: 13px;
  color: #999;
  margin-bottom: 24px;
  display: flex;
  gap: 16px;
}
.markdown-body {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
}
.markdown-body :deep(h2) { font-size: 22px; margin: 28px 0 12px; }
.markdown-body :deep(h3) { font-size: 18px; margin: 24px 0 10px; }
.markdown-body :deep(p) { margin: 0 0 14px; }
.markdown-body :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
}
.markdown-body :deep(pre) {
  background: #f8f8f8;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
}
.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
}
.markdown-body :deep(blockquote) {
  border-left: 4px solid #4a90d9;
  padding: 4px 16px;
  margin: 0 0 14px;
  color: #666;
  background: #f8fafc;
}
.markdown-body :deep(img) { max-width: 100%; border-radius: 4px; }
</style>
