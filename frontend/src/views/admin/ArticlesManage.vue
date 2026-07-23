<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AdminHeader from '@/components/AdminHeader.vue'
import { fetchAdminArticles, deleteArticle, type ArticleDetail } from '@/api'
const articles = ref<ArticleDetail[]>([])

onMounted(async () => {
  const res = await fetchAdminArticles()
  articles.value = res.data
})

async function handleDelete(id: number, title: string) {
  if (!confirm(`确定删除文章「${title}」？`)) return
  await deleteArticle(id)
  articles.value = articles.value.filter(a => a.id !== id)
}
</script>

<template>
  <div class="admin-layout">
    <AdminHeader />
    <main class="admin-main">
      <div class="toolbar">
        <h2>文章管理</h2>
        <RouterLink to="/admin/articles/new" class="btn-primary">新建文章</RouterLink>
      </div>
      <table>
        <thead>
          <tr><th>ID</th><th>标题</th><th>分类</th><th>发布时间</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in articles" :key="a.id">
            <td>{{ a.id }}</td>
            <td>{{ a.title }}</td>
            <td>{{ a.category_name || '-' }}</td>
            <td>{{ a.created_at.slice(0, 10) }}</td>
            <td class="actions">
              <RouterLink :to="`/admin/articles/${a.id}/edit`">编辑</RouterLink>
              <a href="#" @click.prevent="handleDelete(a.id, a.title)">删除</a>
            </td>
          </tr>
          <tr v-if="articles.length === 0">
            <td colspan="5" class="empty">暂无文章</td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<style scoped>
.admin-layout { min-height: 100vh; background: #f5f6f7; }
.admin-main { max-width: 1000px; margin: 24px auto; padding: 0 20px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.toolbar h2 { margin: 0; font-size: 18px; }
.btn-primary { background: #4a90d9; color: #fff; padding: 8px 18px; border-radius: 4px; text-decoration: none; font-size: 14px; }
table { width: 100%; background: #fff; border-radius: 6px; overflow: hidden; border-collapse: collapse; }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; border-bottom: 1px solid #eee; }
th { background: #fafafa; font-weight: 600; }
.actions { display: flex; gap: 12px; }
.actions a { color: #4a90d9; text-decoration: none; font-size: 13px; }
.empty { text-align: center; color: #999; padding: 30px 0; }
</style>
