<template>
  <footer class="app-footer">
    <p>&copy; {{ year }} 我的博客 · Powered by FastAPI &amp; Vue</p>
  </footer>
</template>

<script setup lang="ts">
const year = new Date().getFullYear()
</script>

<style scoped>
.app-footer {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 13px;
  border-top: 1px solid #eee;
  margin-top: 40px;
}
</style>
