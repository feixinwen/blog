<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AdminHeader from '@/components/AdminHeader.vue'
import { fetchAdminCategories, createCategory, updateCategory, deleteCategory, type Category } from '@/api'
const categories = ref<Category[]>([])
const newName = ref('')
const newSlug = ref('')
const editingId = ref<number | null>(null)
const editName = ref('')
const editSlug = ref('')

onMounted(async () => { const res = await fetchAdminCategories(); categories.value = res.data })

async function handleCreate() {
  if (!newName.value || !newSlug.value) return
  await createCategory({ name: newName.value, slug: newSlug.value })
  newName.value = ''; newSlug.value = ''
  const res = await fetchAdminCategories(); categories.value = res.data
}

function startEdit(c: Category) { editingId.value = c.id; editName.value = c.name; editSlug.value = c.slug }
function cancelEdit() { editingId.value = null }

async function handleUpdate(id: number) {
  await updateCategory(id, { name: editName.value, slug: editSlug.value })
  editingId.value = null
  const res = await fetchAdminCategories(); categories.value = res.data
}

async function handleDelete(id: number) {
  if (!confirm('确定删除？')) return
  await deleteCategory(id)
  categories.value = categories.value.filter(c => c.id !== id)
}
</script>

<template>
  <div class="admin-layout">
    <AdminHeader />
    <main class="admin-main">
      <h2>分类管理</h2>

      <div class="create-form">
        <input v-model="newName" placeholder="分类名" />
        <input v-model="newSlug" placeholder="slug 标识" />
        <button class="btn-small" @click="handleCreate">添加</button>
      </div>

      <table>
        <thead><tr><th>ID</th><th>名称</th><th>Slug</th><th>文章数</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="c in categories" :key="c.id">
            <td>{{ c.id }}</td>
            <td>
              <span v-if="editingId !== c.id">{{ c.name }}</span>
              <input v-else v-model="editName" />
            </td>
            <td>
              <span v-if="editingId !== c.id">{{ c.slug }}</span>
              <input v-else v-model="editSlug" />
            </td>
            <td>{{ c.article_count }}</td>
            <td>
              <template v-if="editingId === c.id">
                <a href="#" @click.prevent="handleUpdate(c.id)">保存</a>
                <a href="#" @click.prevent="cancelEdit()">取消</a>
              </template>
              <template v-else>
                <a href="#" @click.prevent="startEdit(c)">编辑</a>
                <a href="#" @click.prevent="handleDelete(c.id)">删除</a>
              </template>
            </td>
          </tr>
          <tr v-if="categories.length === 0"><td colspan="5" class="empty">暂无分类</td></tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<style scoped>
.admin-layout { min-height: 100vh; background: #f5f6f7; }
.admin-main { max-width: 1000px; margin: 24px auto; padding: 0 20px; }
h2 { margin: 0 0 16px; }
.create-form { display: flex; gap: 10px; margin-bottom: 16px; }
.create-form input { padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.btn-small { background: #4a90d9; color: #fff; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 13px; }
table { width: 100%; background: #fff; border-radius: 6px; overflow: hidden; border-collapse: collapse; }
th, td { padding: 10px 14px; text-align: left; font-size: 14px; border-bottom: 1px solid #eee; }
th { background: #fafafa; font-weight: 600; }
td input { padding: 4px 8px; border: 1px solid #ddd; border-radius: 3px; font-size: 13px; width: 120px; }
td a { margin-right: 10px; font-size: 13px; color: #4a90d9; text-decoration: none; }
td a:last-child { color: #e74c3c; }
.empty { text-align: center; color: #999; padding: 30px; }
</style>
