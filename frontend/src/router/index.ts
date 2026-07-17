import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ==================== 前台 ====================
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/article/:slug',
      name: 'article',
      component: () => import('@/views/ArticleView.vue'),
    },
    {
      path: '/category/:slug',
      name: 'category',
      component: () => import('@/views/CategoryView.vue'),
    },
    {
      path: '/tag/:slug',
      name: 'tag',
      component: () => import('@/views/TagView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
    },

    // ==================== 后台 ====================
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/LoginView.vue'),
    },
    {
      path: '/admin',
      redirect: '/admin/articles',
    },
    {
      path: '/admin/articles',
      name: 'admin-articles',
      component: () => import('@/views/admin/ArticlesManage.vue'),
    },
    {
      path: '/admin/articles/new',
      name: 'admin-article-new',
      component: () => import('@/views/admin/ArticleEditor.vue'),
    },
    {
      path: '/admin/articles/:id/edit',
      name: 'admin-article-edit',
      component: () => import('@/views/admin/ArticleEditor.vue'),
    },
    {
      path: '/admin/comments',
      name: 'admin-comments',
      component: () => import('@/views/admin/CommentsManage.vue'),
    },
    {
      path: '/admin/categories',
      name: 'admin-categories',
      component: () => import('@/views/admin/CategoriesManage.vue'),
    },
    {
      path: '/admin/tags',
      name: 'admin-tags',
      component: () => import('@/views/admin/TagsManage.vue'),
    },
  ],
})

// 路由守卫：后台页面需要登录
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.path.startsWith('/admin') && !to.path.includes('/login') && !token) {
    return '/admin/login'
  }
})

export default router
