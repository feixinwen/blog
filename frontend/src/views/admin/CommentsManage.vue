<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AdminHeader from '@/components/AdminHeader.vue'
import { fetchAdminComments, deleteComment, type Comment } from '@/api'
const comments = ref<Comment[]>([])

onMounted(async () => {
  const res = await fetchAdminComments()
  comments.value = res.data
})

async function handleDelete(id: number) {
  if (!confirm('确定删除该评论？')) return
  await deleteComment(id)
  comments.value = comments.value.filter(c => c.id !== id)
}
</script>

<template>
  <div class="admin-layout">
    <AdminHeader />
    <main class="admin-main">
      <h2>评论管理</h2>
      <table>
        <thead><tr><th>ID</th><th>文章ID</th><th>作者</th><th>内容</th><th>时间</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="c in comments" :key="c.id">
            <td>{{ c.id }}</td>
            <td>{{ c.article_id }}</td>
            <td>{{ c.author_name }}</td>
            <td class="content-cell">{{ c.content.slice(0, 100) }}{{ c.content.length > 100 ? '...' : '' }}</td>
            <td>{{ c.created_at.slice(0, 10) }}</td>
            <td><a href="#" @click.prevent="handleDelete(c.id)">删除</a></td>
          </tr>
          <tr v-if="comments.length === 0"><td colspan="6" class="empty">暂无评论</td></tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<style scoped>
.admin-layout { min-height: 100vh; background: #f5f6f7; }
.admin-main { max-width: 1000px; margin: 24px auto; padding: 0 20px; }
h2 { margin: 0 0 16px; }
table { width: 100%; background: #fff; border-radius: 6px; overflow: hidden; border-collapse: collapse; }
th, td { padding: 10px 14px; text-align: left; font-size: 14px; border-bottom: 1px solid #eee; }
th { background: #fafafa; font-weight: 600; }
.content-cell { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
td a { color: #e74c3c; text-decoration: none; font-size: 13px; }
.empty { text-align: center; color: #999; padding: 30px; }
</style>
