<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

import { fetchArticle, type ArticleDetail } from '@/api'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import CommentSection from '@/components/CommentSection.vue'
import TableOfContents from '@/components/TableOfContents.vue'
import ParticleBackground from '@/components/ParticleBackground.vue'

const route = useRoute()
const article = ref<ArticleDetail | null>(null)

// 配置 marked：代码高亮 + 标题加 id
marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
})

// 自定义标题渲染：给 h2/h3 加 id，用于目录导航定位
const renderer = new marked.Renderer()
renderer.heading = function (opts: any) {
  // marked v18+ 的 heading 参数是对象 { depth, text, tokens }
  const text = opts.text || marked.parseInline(opts.raw || '') || ''
  const plainText = text.replace(/<[^>]*>/g, '')
  const id = plainText.toLowerCase().replace(/\s+/g, '-').replace(/[^\w一-鿿-]/g, '')
  return `<h${opts.depth} id="${id}">${text}</h${opts.depth}>`
}
marked.use({ renderer })

onMounted(async () => {
  const slug = route.params.slug as string
  try {
    const res = await fetchArticle(slug)
    article.value = res.data
  } catch (e: any) {
    console.error('文章加载失败:', e?.response?.status, e?.response?.data || e.message)
  }
})

function renderMarkdown(md: string): string {
  return marked.parse(md) as string
}
</script>

<template>
  <div class="article-layout">
    <ParticleBackground />
    <AppHeader />

    <div v-if="article" class="article-wrapper">
      <article class="article-main">
        <!-- ====== 标题 ====== -->
        <h1 class="article-title">{{ article.title }}</h1>

        <!-- ====== 元信息 ====== -->
        <div class="article-meta">
          <span>发布于 {{ article.created_at.slice(0, 10) }}</span>
          <span class="meta-sep">·</span>
          <span>{{ article.read_count }} 阅读</span>
          <span class="meta-sep">·</span>
          <span>{{ article.comment_count }} 评论</span>
        </div>

        <!-- ====== 分类标签 ====== -->
        <div class="article-tags" v-if="article.category_name">
          <RouterLink :to="`/category/${article.category_slug}`" class="tag-pill">
            {{ article.category_name }}
          </RouterLink>
        </div>

        <hr class="divider" />

        <!-- ====== 正文 ====== -->
        <div class="markdown-body" v-html="renderMarkdown(article.content)" />

        <!-- ====== EOF 标记 ====== -->
        <div class="eof">__EOF__</div>

        <!-- ====== 作者卡片 ====== -->
        <div class="author-card">
          <div class="author-name">本文作者：凌云</div>
          <div class="author-desc">全栈开发者 · 热爱技术与分享</div>
        </div>

        <!-- ====== 上下篇导航 ====== -->
        <nav class="post-nav">
          <RouterLink
            v-if="article.prev_slug"
            :to="`/article/${article.prev_slug}`"
            class="post-nav-link"
          >
            &laquo; {{ article.prev_title }}
          </RouterLink>
          <span v-else class="post-nav-link disabled">&laquo; 已经是第一篇</span>

          <RouterLink
            v-if="article.next_slug"
            :to="`/article/${article.next_slug}`"
            class="post-nav-link next"
          >
            {{ article.next_title }} &raquo;
          </RouterLink>
          <span v-else class="post-nav-link disabled next">已经是最后一篇 &raquo;</span>
        </nav>

        <!-- ====== 底部元信息 ====== -->
        <div class="article-footer-meta">
          posted @ {{ article.created_at.slice(0, 10) }}
          &nbsp;阅读({{ article.read_count }})&nbsp;评论({{ article.comment_count }})
        </div>

        <hr class="divider" />

        <!-- ====== 评论区 ====== -->
        <CommentSection :article-id="article.id" />
      </article>

      <!-- 目录导航：右侧 sticky -->
      <aside class="toc-sidebar">
        <TableOfContents :content="article.content" />
      </aside>
    </div>

    <div v-else class="loading">加载中...</div>

    <AppFooter />
  </div>
</template>

<style scoped>
.article-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}
.article-wrapper {
  flex: 1;
  position: relative;
  z-index: 1;
}
.loading {
  text-align: center;
  padding: 80px 0;
  color: #999;
}

/* === 文章主体（居中） === */
.article-main {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* === 右侧目录（fixed 浮动在文章右侧，始终可见） === */
@media (min-width: 1400px) {
  .toc-sidebar {
    position: fixed;
    top: 100px;
    left: calc(50% + 450px + 30px);
    width: 200px;
    max-height: calc(100vh - 140px);
    overflow-y: auto;
    z-index: 50;
  }
}
@media (max-width: 1399px) {
  .toc-sidebar { display: none; }
}

/* === 标题 === */
.article-title {
  font-family: 'STKaiti', 'KaiTi', '楷体', 'STSong', serif;
  font-size: 30px;
  font-weight: 700;
  color: #222;
  line-height: 1.4;
  margin: 0 0 16px;
}

/* === 元信息 === */
.article-meta {
  font-size: 14px;
  color: #999;
  margin-bottom: 14px;
}
.meta-sep {
  margin: 0 8px;
  color: #ddd;
}

/* === 标签 === */
.article-tags {
  margin-bottom: 10px;
}
.tag-pill {
  display: inline-block;
  background: #e8f0fe;
  color: #4a90d9;
  padding: 4px 14px;
  border-radius: 14px;
  font-size: 13px;
  text-decoration: none;
}
.tag-pill:hover {
  background: #d0e2fc;
}

/* === 分割线 === */
.divider {
  border: none;
  border-top: 1px solid #eee;
  margin: 24px 0;
}

/* === Markdown 内容 === */
.markdown-body {
  font-size: 15px;
  line-height: 1.9;
  color: #333;
}
.markdown-body :deep(h2) {
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-size: 22px;
  margin: 36px 0 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #4a90d9;
}
.markdown-body :deep(h3) {
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-size: 18px;
  margin: 28px 0 12px;
}
.markdown-body :deep(p) { margin: 0 0 16px; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { margin: 0 0 16px; padding-left: 24px; }
.markdown-body :deep(li) { margin-bottom: 6px; }
.markdown-body :deep(li ul) { margin-top: 6px; }
.markdown-body :deep(blockquote) {
  border-left: 4px solid #4a90d9;
  background: #f8fafc;
  padding: 12px 20px;
  margin: 0 0 16px;
  border-radius: 0 6px 6px 0;
  color: #555;
}
.markdown-body :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}
.markdown-body :deep(pre) {
  background: #1e1e2e;
  border-radius: 8px;
  padding: 16px 20px;
  overflow-x: auto;
  margin: 0 0 16px;
}
.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
  color: #cdd6f4;
  font-size: 13px;
}
.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 6px;
  margin: 12px 0;
}
.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 16px;
}
.markdown-body :deep(th), .markdown-body :deep(td) {
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  text-align: left;
}
.markdown-body :deep(th) { background: #f8f8f8; }

/* === EOF === */
.eof {
  text-align: center;
  color: #ccc;
  margin: 40px 0;
  font-size: 13px;
  letter-spacing: 4px;
}

/* === 作者卡片 === */
.author-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 24px;
}
.author-name { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 4px; }
.author-desc { font-size: 13px; color: #999; }

/* === 上下篇导航 === */
.post-nav {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 16px;
}
.post-nav-link {
  flex: 1;
  color: #4a90d9;
  text-decoration: none;
  font-size: 14px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 6px;
  transition: background 0.2s;
}
.post-nav-link:hover { background: #eef3fa; }
.post-nav-link.next { text-align: right; }
.post-nav-link.disabled {
  color: #ccc;
  cursor: default;
  pointer-events: none;
}

/* === 底部元信息 === */
.article-footer-meta {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
}
</style>
