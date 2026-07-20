<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchArticles, type ArticleListItem } from '@/api'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Sidebar from '@/components/Sidebar.vue'
import ArticleCard from '@/components/ArticleCard.vue'
import Pagination from '@/components/Pagination.vue'
import ParticleBackground from '@/components/ParticleBackground.vue'

const route = useRoute()
const articles = ref<ArticleListItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10

async function load() {
  const slug = route.params.slug as string
  const res = await fetchArticles(page.value, pageSize, undefined, slug)
  articles.value = res.data.items
  total.value = res.data.total
}

function onPageChange(p: number) { page.value = p; load(); window.scrollTo(0, 0) }
onMounted(load)
watch(() => route.params.slug, () => { page.value = 1; load() })
</script>

<template>
  <div class="layout">
    <ParticleBackground />
    <AppHeader />
    <div class="main-body">
      <main class="content">
        <h2 class="page-title">标签：{{ route.params.slug }}</h2>
        <ArticleCard v-for="a in articles" :key="a.id" :article="a" />
        <div v-if="articles.length === 0" class="empty">该标签下暂无文章</div>
        <Pagination :page="page" :total="total" :page-size="pageSize" @change="onPageChange" />
      </main>
      <Sidebar />
    </div>
    <AppFooter />
  </div>
</template>

<style scoped>
.layout { min-height: 100vh; display: flex; flex-direction: column; position: relative; }
.main-body { max-width: 1100px; margin: 24px auto; display: flex; gap: 24px; flex: 1; width: 100%; padding: 0 20px; box-sizing: border-box; position: relative; z-index: 1; }
.content { flex: 1; min-width: 0; }
.page-title { font-size: 18px; margin: 0 0 16px 0; color: #333; }
.empty { text-align: center; color: #999; padding: 60px 0; }
</style>
