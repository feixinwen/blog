<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
</script>

<template>
  <header class="admin-header">
    <nav>
      <RouterLink to="/admin/articles">文章管理</RouterLink>
      <RouterLink to="/admin/categories">分类管理</RouterLink>
      <RouterLink to="/admin/tags">标签管理</RouterLink>
      <RouterLink to="/admin/comments">评论管理</RouterLink>
      <RouterLink to="/admin/chat">创作助手</RouterLink>
      <a href="/" target="_blank">查看博客</a>
    </nav>
    <button @click="auth.logout(); router.push('/admin/login')">退出</button>
  </header>
</template>

<style scoped>
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 50px;
  background: #333;
  color: #fff;
}
.admin-header nav {
  display: flex;
  gap: 20px;
}
.admin-header a {
  color: #ccc;
  text-decoration: none;
  font-size: 14px;
}
.admin-header a:hover, .admin-header a.router-link-active {
  color: #fff;
}
.admin-header button {
  background: none;
  border: 1px solid #888;
  color: #ccc;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
</style>
