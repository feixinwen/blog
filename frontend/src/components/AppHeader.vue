<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'

const hasToken = computed(() => !!localStorage.getItem('token'))
const menuOpen = ref(false)

function toggleMenu() { menuOpen.value = !menuOpen.value }
function closeMenu() { menuOpen.value = false }
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <RouterLink to="/" class="logo">我的博客</RouterLink>

      <!-- 汉堡菜单按钮 -->
      <button class="menu-btn" :class="{ open: menuOpen }" @click="toggleMenu">
        <span /><span /><span />
      </button>
    </div>

    <!-- 下拉导航面板 -->
    <Transition name="menu">
      <nav v-if="menuOpen" class="menu-panel" @click.self="closeMenu">
        <RouterLink to="/" @click="closeMenu">首页</RouterLink>
        <RouterLink to="/about" @click="closeMenu">关于</RouterLink>
        <RouterLink v-if="hasToken" to="/admin/articles" @click="closeMenu">管理</RouterLink>
        <RouterLink v-else to="/admin/login" @click="closeMenu">登录</RouterLink>
      </nav>
    </Transition>
  </header>
</template>

<style scoped>
.app-header {
  background: #fff;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
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

/* === 汉堡按钮 === */
.menu-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  padding: 0;
}
.menu-btn span {
  display: block;
  width: 22px;
  height: 2px;
  background: #555;
  border-radius: 1px;
  transition: transform 0.3s, opacity 0.3s;
}
/* 打开时变成 X */
.menu-btn.open span:nth-child(1) { transform: rotate(45deg) translate(5px, 5px); }
.menu-btn.open span:nth-child(2) { opacity: 0; }
.menu-btn.open span:nth-child(3) { transform: rotate(-45deg) translate(5px, -5px); }

/* === 下拉导航 === */
.menu-panel {
  position: absolute;
  top: 56px;
  right: 0;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  padding: 8px 0;
  min-width: 150px;
  display: flex;
  flex-direction: column;
}
.menu-panel a {
  padding: 10px 24px;
  color: #555;
  text-decoration: none;
  font-size: 15px;
}
.menu-panel a:hover {
  background: #f5f6f7;
  color: #4a90d9;
}

/* 下拉动画 */
.menu-enter-active { transition: opacity 0.2s, transform 0.2s; }
.menu-leave-active { transition: opacity 0.15s, transform 0.15s; }
.menu-enter-from { opacity: 0; transform: translateY(-8px); }
.menu-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
