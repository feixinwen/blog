<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { RouterLink } from 'vue-router'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import Toast from '@/components/Toast.vue'
import { uploadImage, fetchAdminArticle, fetchAdminCategories, fetchAdminTags,
  createArticle, updateArticle, type Category, type Tag, } from '@/api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = ref<InstanceType<typeof Toast> | null>(null)

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
const saving = ref(false)
const coverUploading = ref(false)

const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])

// 标题变化 → 自动生成随机 slug
watch(title, (val) => {
  if (isEdit) return
  if (!val.trim()) { slug.value = ''; return }
  // 只在 slug 还是空的时候自动生成一次，避免覆盖手动修改
  if (!slug.value) {
    const ts = Date.now().toString(36)
    const rand = Math.random().toString(36).slice(2, 8)
    slug.value = `${ts}-${rand}`
  }
})

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

// 封面上传
async function handleCoverUpload() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    coverUploading.value = true
    try { const res = await uploadImage(file); coverUrl.value = res.data.url }
    catch { toast.value?.show('封面上传失败', 'error') }
    finally { coverUploading.value = false }
  }
  input.click()
}

function toggleTag(id: number) {
  const i = selectedTagIds.value.indexOf(id)
  i >= 0 ? selectedTagIds.value.splice(i, 1) : selectedTagIds.value.push(id)
}

async function handleSave() {
  if (!title.value.trim() || !slug.value.trim() || !content.value.trim()) {
    toast.value?.show('标题、标识和内容不能为空', 'error'); return
  }
  saving.value = true
  try {
    const data = {
      title: title.value, slug: slug.value, content: content.value,
      summary: summary.value || null, cover_url: coverUrl.value || null,
      category_id: categoryId.value, tag_ids: selectedTagIds.value,
      is_published: isPublished.value,
    }
    if (isEdit) {
      await updateArticle(articleId, data)
      toast.value?.show('文章已更新')
    } else {
      const res = await createArticle(data)
      router.replace(`/admin/articles/${res.data.id}/edit`)
      toast.value?.show('文章已创建')
    }
  } catch (err: any) {
    toast.value?.show(err.response?.data?.detail || '保存失败', 'error')
  } finally { saving.value = false }
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

      <!-- 顶部栏：标题 + 发布开关 -->
      <div class="editor-topbar">
        <h2>{{ isEdit ? '编辑文章' : '新建文章' }}</h2>
        <label class="publish-switch">
          <input type="checkbox" v-model="isPublished" />
          <span class="switch-track">
            <span class="switch-thumb" />
          </span>
          <span class="switch-label">{{ isPublished ? '已发布' : '草稿' }}</span>
        </label>
      </div>

      <!-- 标题 -->
      <div class="form-group">
        <input
          v-model="title"
          class="input-title"
          placeholder="文章标题"
          maxlength="200"
        />
      </div>

      <!-- slug -->
      <div class="form-group">
        <label>URL 标识</label>
        <input v-model="slug" placeholder="url-biao-shi" maxlength="200" />
        <span class="hint">访问地址: /article/{{ slug || '...' }}</span>
      </div>

      <!-- 封面图 -->
      <div class="form-group">
        <label>封面图</label>
        <div class="cover-row">
          <div class="cover-preview" v-if="coverUrl">
            <img :src="coverUrl" alt="封面预览" />
            <button class="cover-remove" @click="coverUrl = ''">&times;</button>
          </div>
          <div class="cover-actions">
            <button class="btn-outline" @click="handleCoverUpload" :disabled="coverUploading">
              {{ coverUploading ? '上传中...' : '本地上传' }}
            </button>
            <input v-model="coverUrl" placeholder="或粘贴图片 URL" class="cover-url-input" />
          </div>
        </div>
      </div>

      <!-- 内容 -->
      <div class="form-group">
        <label>正文</label>
        <MarkdownEditor v-model="content" />
      </div>

      <!-- 摘要 -->
      <div class="form-group">
        <label>摘要</label>
        <textarea v-model="summary" placeholder="简短描述，列表页展示..." rows="2" maxlength="500"></textarea>
      </div>

      <!-- 分类 + 标签 -->
      <div class="form-row">
        <div class="form-group">
          <label>分类</label>
          <select v-model.number="categoryId">
            <option :value="null">不分类</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>标签</label>
          <div class="tag-choices">
            <span
              v-for="t in tags" :key="t.id"
              class="tag-option"
              :class="{ selected: selectedTagIds.includes(t.id) }"
              @click="toggleTag(t.id)"
            >{{ t.name }}</span>
            <span v-if="tags.length === 0" class="hint">暂无标签</span>
          </div>
        </div>
      </div>

      <!-- 保存 -->
      <button class="btn-save" @click="handleSave" :disabled="saving">
        {{ saving ? '保存中...' : '保存' }}
      </button>
    </main>

    <Toast ref="toast" />
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

/* === 顶部栏 === */
.editor-topbar {
  display: flex; justify-content: space-between; align-items: center;
  margin: 12px 0 20px;
}
.editor-topbar h2 { margin: 0; font-size: 18px; }

/* 发布开关 */
.publish-switch { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.publish-switch input { display: none; }
.switch-track {
  width: 44px; height: 24px; background: #ccc; border-radius: 12px;
  position: relative; transition: background 0.2s;
}
.publish-switch input:checked + .switch-track { background: #52c41a; }
.switch-thumb {
  position: absolute; top: 2px; left: 2px;
  width: 20px; height: 20px; background: #fff; border-radius: 50%;
  transition: transform 0.2s;
}
.publish-switch input:checked + .switch-track .switch-thumb { transform: translateX(20px); }
.switch-label { font-size: 14px; color: #555; min-width: 56px; }

/* === 标题输入 === */
.input-title {
  width: 100%; padding: 12px 16px; border: none; border-radius: 6px;
  font-size: 22px; font-family: 'STKaiti','KaiTi',serif;
  outline: none; box-sizing: border-box;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.input-title:focus { box-shadow: 0 0 0 2px rgba(74,144,217,0.2); }

/* === 封面 === */
.cover-row { display: flex; gap: 16px; align-items: flex-start; }
.cover-preview {
  width: 160px; height: 100px; border-radius: 6px; overflow: hidden;
  position: relative; flex-shrink: 0; background: #f0f0f0;
}
.cover-preview img { width: 100%; height: 100%; object-fit: cover; }
.cover-remove {
  position: absolute; top: 4px; right: 4px;
  width: 22px; height: 22px; border-radius: 50%;
  border: none; background: rgba(0,0,0,0.5); color: #fff;
  font-size: 14px; cursor: pointer; line-height: 22px; text-align: center;
}
.cover-actions { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.btn-outline {
  padding: 6px 14px; border: 1px solid #d0d0d0; border-radius: 4px;
  background: #fff; color: #555; cursor: pointer; font-size: 13px; width: fit-content;
}
.btn-outline:hover { border-color: #4a90d9; color: #4a90d9; }
.cover-url-input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }

/* === 标签 === */
.tag-choices { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-option {
  padding: 5px 14px; border-radius: 16px; font-size: 13px;
  border: 1px solid #e0e0e0; color: #777; cursor: pointer;
  transition: all 0.15s; user-select: none;
}
.tag-option:hover { border-color: #4a90d9; color: #4a90d9; }
.tag-option.selected {
  background: #4a90d9; border-color: #4a90d9; color: #fff;
}

/* === 通用表单 === */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; color: #555; margin-bottom: 6px; }
.form-group input[type="text"], .form-group textarea, .form-group select {
  width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px;
  font-size: 14px; box-sizing: border-box;
}
textarea { resize: vertical; }
.form-row { display: flex; gap: 20px; }
.form-row .form-group { flex: 1; }
.hint { color: #999; font-size: 12px; margin-top: 4px; display: block; }
.btn-save {
  background: #4a90d9; color: #fff; border: none;
  padding: 10px 30px; border-radius: 4px; cursor: pointer; font-size: 15px;
}
.btn-save:disabled { opacity: 0.6; }
</style>
