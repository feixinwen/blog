<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  fetchAdminArticle, fetchAdminCategories, fetchAdminTags,
  createArticle, updateArticle, type Category, type Tag,
} from '@/api'
import { RouterLink } from 'vue-router'
import MarkdownEditor from '@/components/MarkdownEditor.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isEdit = !!route.params.id
const articleId = Number(route.params.id)

const title = ref('')
const slug = ref('')
const content = ref('')
const summary = ref('')
const coverUrl = ref('')
const categoryId = ref<number | null>(null)
const selectedTagIds = ref<number[]>([])
const isPublished = ref(true)

const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const saving = ref(false)

onMounted(async () => {
  const [catRes, tagRes] = await Promise.all([fetchAdminCategories(), fetchAdminTags()])
  categories.value = catRes.data
  tags.value = tagRes.data

  if (isEdit) {
    const res = await fetchAdminArticle(articleId)
    const a = res.data
    title.value = a.title
    slug.value = a.slug
    content.value = a.content
    summary.value = a.summary || ''
    coverUrl.value = a.cover_url || ''
    categoryId.value = a.category_id
    selectedTagIds.value = a.tag_ids
    isPublished.value = a.is_published
  }
})

async function handleSave() {
  if (!title.value || !slug.value || !content.value) {
    alert('标题、标识和内容不能为空')
    return
  }
  saving.value = true
  try {
    const data = {
      title: title.value,
      slug: slug.value,
      content: content.value,
      summary: summary.value || null,
      cover_url: coverUrl.value || null,
      category_id: categoryId.value,
      tag_ids: selectedTagIds.value,
      is_published: isPublished.value,
    }
    if (isEdit) {
      await updateArticle(articleId, data)
    } else {
      const res = await createArticle(data)
      router.replace(`/admin/articles/${res.data.id}/edit`)
    }
    alert('保存成功')
  } catch (err: any) {
    alert(err.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

function toggleTag(id: number) {
  const idx = selectedTagIds.value.indexOf(id)
  if (idx >= 0) selectedTagIds.value.splice(idx, 1)
  else selectedTagIds.value.push(id)
}
</script>

<template>
  <div class="admin-layout">
    <header class="admin-header">
      <nav>
        <RouterLink to="/admin/articles">文章管理</RouterLink>
        <RouterLink to="/admin/categories">分类管理</RouterLink>
        <RouterLink to="/admin/tags">标签管理</RouterLink>
        <RouterLink to="/admin/comments">评论管理</RouterLink>
      </nav>
      <button @click="auth.logout(); router.push('/admin/login')">退出</button>
    </header>
    <main class="admin-main">
      <RouterLink to="/admin/articles" class="back-link">&larr; 返回文章列表</RouterLink>
      <h2>{{ isEdit ? '编辑文章' : '新建文章' }}</h2>

      <div class="form-group">
        <label>标题</label>
        <input v-model="title" placeholder="文章标题" maxlength="200" />
      </div>
      <div class="form-group">
        <label>URL 标识 (slug)</label>
        <input v-model="slug" placeholder="url-biao-shi" maxlength="200" />
      </div>
      <div class="form-group">
        <label>文章内容</label>
        <MarkdownEditor v-model="content" />
      </div>
      <div class="form-group">
        <label>摘要</label>
        <textarea v-model="summary" placeholder="简短描述..." rows="2" maxlength="500"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>分类</label>
          <select v-model.number="categoryId">
            <option :value="null">无分类</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>标签</label>
          <div class="tag-checks">
            <label v-for="t in tags" :key="t.id" class="tag-check">
              <input type="checkbox" :checked="selectedTagIds.includes(t.id)" @change="toggleTag(t.id)" />
              {{ t.name }}
            </label>
            <span v-if="tags.length === 0" class="hint">暂无标签</span>
          </div>
        </div>
      </div>
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="isPublished" />
          发布
        </label>
      </div>
      <button class="btn-save" @click="handleSave" :disabled="saving">
        {{ saving ? '保存中...' : '保存' }}
      </button>
    </main>
  </div>
</template>

<style scoped>
.admin-layout { min-height: 100vh; background: #f5f6f7; }
.admin-header { display: flex; justify-content: space-between; align-items: center; padding: 0 24px; height: 50px; background: #333; color: #fff; }
.admin-header nav { display: flex; gap: 20px; }
.admin-header a { color: #ccc; text-decoration: none; font-size: 14px; }
.admin-header a:hover, .admin-header a.router-link-active { color: #fff; }
.admin-header button { background: none; border: 1px solid #888; color: #ccc; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 13px; }
.admin-main { max-width: 1000px; margin: 24px auto; padding: 0 20px; }
.back-link { color: #888; text-decoration: none; font-size: 13px; }
.back-link:hover { color: #4a90d9; }
h2 { margin: 12px 0 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; color: #555; margin-bottom: 6px; }
.form-group input[type="text"], .form-group textarea, .form-group select {
  width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; box-sizing: border-box;
}
textarea { resize: vertical; }
.form-row { display: flex; gap: 20px; }
.form-row .form-group { flex: 1; }
.tag-checks { display: flex; flex-wrap: wrap; gap: 10px; }
.tag-check { font-size: 13px; color: #555; display: flex; align-items: center; gap: 4px; cursor: pointer; }
.hint { color: #999; font-size: 13px; }
.btn-save { background: #4a90d9; color: #fff; border: none; padding: 10px 30px; border-radius: 4px; cursor: pointer; font-size: 15px; }
.btn-save:disabled { opacity: 0.6; }
</style>
