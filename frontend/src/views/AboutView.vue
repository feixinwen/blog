<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Sidebar from '@/components/Sidebar.vue'
</script>

<template>
  <div class="layout">
    <AppHeader />
    <div class="main-body">
      <main class="content">
        <div class="about-card">
          <h1>关于我</h1>
          <p>全栈开发者，热爱技术，喜欢写代码和分享知识。</p>
          <p>这个博客用于记录学习心得、技术笔记和个人思考。</p>
          <p>技术栈：Python / FastAPI / Vue / TypeScript / MySQL</p>
        </div>
      </main>
      <Sidebar />
    </div>
    <AppFooter />
  </div>
</template>

<style scoped>
.layout { min-height: 100vh; display: flex; flex-direction: column; background: #f5f6f7; }
.main-body { max-width: 1100px; margin: 24px auto; display: flex; gap: 24px; flex: 1; width: 100%; padding: 0 20px; box-sizing: border-box; }
.content { flex: 1; min-width: 0; }
.about-card { background: #fff; border-radius: 6px; padding: 30px; }
.about-card h1 { margin: 0 0 16px 0; font-size: 24px; }
.about-card p { color: #555; line-height: 1.8; margin: 0 0 10px; }
</style>
