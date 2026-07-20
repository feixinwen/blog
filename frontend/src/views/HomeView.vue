<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchArticles, type ArticleListItem } from '@/api'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Sidebar from '@/components/Sidebar.vue'
import ArticleCard from '@/components/ArticleCard.vue'
import Pagination from '@/components/Pagination.vue'
import ParticleBackground from '@/components/ParticleBackground.vue'
import BannerSlider from '@/components/BannerSlider.vue'

const bannerImages = [
  'https://picsum.photos/seed/blog1/1920/1080',
  'https://picsum.photos/seed/blog2/1920/1080',
  'https://picsum.photos/seed/blog3/1920/1080',
]

const articles = ref<ArticleListItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10

async function loadArticles() {
  const res = await fetchArticles(page.value, pageSize)
  articles.value = res.data.items
  total.value = res.data.total
}

function onPageChange(p: number) {
  page.value = p
  loadArticles()
  window.scrollTo(0, 0)
}

onMounted(loadArticles)
</script>

<template>
  <div class="home-layout">
    <ParticleBackground />
    <BannerSlider
      :images="bannerImages"
      title="我的博客"
      subtitle="用代码记录思考与成长"
      :slice-count="4"
      :interval="25000"
    />
    <AppHeader />
    <div id="article-list" class="main-body">
      <main class="content">
        <ArticleCard v-for="a in articles" :key="a.id" :article="a" />
        <div v-if="articles.length === 0" class="empty">还没有文章</div>
        <Pagination
          :page="page"
          :total="total"
          :page-size="pageSize"
          @change="onPageChange"
        />
      </main>
      <Sidebar />
    </div>
    <AppFooter />
  </div>
</template>

<style scoped>
.home-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
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
  position: relative;
  z-index: 1;
}
.content {
  flex: 1;
  min-width: 0;
}
.empty {
  text-align: center;
  color: #999;
  padding: 60px 0;
  font-size: 16px;
}
</style>
