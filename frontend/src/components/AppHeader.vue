<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const hasToken = computed(() => !!localStorage.getItem('token'))
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <RouterLink to="/" class="logo">我的博客</RouterLink>
      <nav>
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/about">关于</RouterLink>
        <RouterLink v-if="hasToken" to="/admin/articles">管理</RouterLink>
        <RouterLink v-else to="/admin/login">登录</RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 56px;
}
.logo {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  text-decoration: none;
}
nav {
  display: flex;
  gap: 20px;
}
nav a {
  color: #555;
  text-decoration: none;
  font-size: 15px;
}
nav a:hover {
  color: #4a90d9;
}
nav a.router-link-exact-active {
  color: #4a90d9;
}
</style>
