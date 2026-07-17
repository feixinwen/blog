<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchComments, createComment, type Comment } from '@/api'

const props = defineProps<{ articleId: number }>()

const comments = ref<Comment[]>([])

const authorName = ref('')
const authorEmail = ref('')
const content = ref('')
const submitting = ref(false)
const error = ref('')

onMounted(async () => {
  const res = await fetchComments(props.articleId)
  comments.value = res.data
})

async function submit() {
  if (!authorName.value.trim() || !authorEmail.value.trim() || !content.value.trim()) {
    error.value = '请填写所有字段'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const res = await createComment({
      article_id: props.articleId,
      author_name: authorName.value,
      author_email: authorEmail.value,
      content: content.value,
    })
    comments.value.unshift(res.data)  // 新评论插到最前面
    content.value = ''
  } catch {
    error.value = '发表失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="comment-section">
    <h3>评论 ({{ comments.length }})</h3>

    <!-- 发表评论 -->
    <div class="comment-form">
      <div class="form-row">
        <input v-model="authorName" placeholder="昵称（必填）" maxlength="50" />
        <input v-model="authorEmail" placeholder="邮箱（必填，不会公开）" maxlength="100" />
      </div>
      <textarea v-model="content" placeholder="写下你的评论..." rows="4" maxlength="5000"></textarea>
      <p v-if="error" class="error">{{ error }}</p>
      <button @click="submit" :disabled="submitting">
        {{ submitting ? '发表中...' : '发表评论' }}
      </button>
    </div>

    <!-- 评论列表 -->
    <div v-if="comments.length === 0" class="empty">暂无评论，来说几句吧</div>
    <div v-for="c in comments" :key="c.id" class="comment-item">
      <div class="comment-header">
        <strong>{{ c.author_name }}</strong>
        <span class="time">{{ c.created_at.slice(0, 10) }}</span>
      </div>
      <p class="comment-content">{{ c.content }}</p>
    </div>
  </div>
</template>

<style scoped>
.comment-section {
  margin-top: 40px;
}
.comment-section h3 {
  font-size: 18px;
  margin-bottom: 16px;
}
.comment-form {
  margin-bottom: 24px;
}
.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}
.form-row input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}
textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  box-sizing: border-box;
  margin-bottom: 8px;
}
.error {
  color: #e74c3c;
  font-size: 13px;
  margin: 0 0 8px 0;
}
.comment-form button {
  background: #4a90d9;
  color: #fff;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.comment-form button:disabled {
  opacity: 0.6;
}
.comment-item {
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 0;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}
.comment-header strong {
  font-size: 14px;
  color: #333;
}
.time {
  font-size: 12px;
  color: #999;
}
.comment-content {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
  margin: 0;
}
.empty {
  color: #999;
  font-size: 14px;
  padding: 20px 0;
}
</style>
