<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { RouterLink } from 'vue-router'
import AdminHeader from '@/components/AdminHeader.vue'

interface StageItem {
  stage: string
  message: string
  status: 'running' | 'done'
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  process?: StageItem[]
  article?: { title: string; content: string; summary: string; tags: string[] }
}

// ===== 持久化存储 =====
const STORAGE_PREFIX = 'blog_chat_'

function loadThreadId(): string {
  const saved = localStorage.getItem(STORAGE_PREFIX + 'tid')
  if (saved) return saved
  const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
  localStorage.setItem(STORAGE_PREFIX + 'tid', id)
  return id
}

function loadMessages(threadId: string): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_PREFIX + threadId)
    return raw ? JSON.parse(raw) : []
  } catch { return [] }
}

function saveMessages(threadId: string, msgs: Message[]) {
  localStorage.setItem(STORAGE_PREFIX + threadId, JSON.stringify(msgs))
}

// ===== 初始化 =====
const threadId = ref(loadThreadId())
const messages = ref<Message[]>(loadMessages(threadId.value))
const input = ref('')
const loading = ref(false)
const chatRef = ref<HTMLElement | null>(null)
const processIdx = ref(-1)

// 消息变化时自动保存
watch(messages, (val) => saveMessages(threadId.value, val), { deep: true })

function scrollBottom() {
  nextTick(() => {
    if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight
  })
}

async function handleSend() {
  const text = input.value.trim()
  if (!text || loading.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  processIdx.value = -1
  scrollBottom()
  loading.value = true

  let aiIdx = -1
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('http://localhost:8000/api/admin/chat?stream=true', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message: text, thread_id: threadId.value }),
    })

    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') break
          try {
            const parsed = JSON.parse(data)

            // --- 思考过程事件 ---
            if (parsed.stage) {
              if (parsed.status === 'started') {
                if (processIdx.value === -1) {
                  messages.value.push({ role: 'assistant', content: '', process: [] })
                  processIdx.value = messages.value.length - 1
                  loading.value = false
                }
                const p = messages.value[processIdx.value].process!
                const existing = p.find(s => s.stage === parsed.stage)
                if (existing) {
                  // revision 循环回到 reviewer 时重置状态
                  existing.status = 'running'
                } else {
                  p.push({ stage: parsed.stage, message: parsed.message, status: 'running' })
                }
              } else if (parsed.status === 'completed') {
                if (processIdx.value >= 0) {
                  const p = messages.value[processIdx.value].process!
                  const item = p.find(s => s.stage === parsed.stage)
                  if (item) item.status = 'done'
                }
              }
              scrollBottom()
            }

            // --- 流式 Token ---
            if (parsed.token) {
              if (aiIdx === -1) {
                // 第一条 token：如果已有思考过程消息，复用它；否则新建
                if (processIdx.value >= 0) {
                  aiIdx = processIdx.value
                } else {
                  messages.value.push({ role: 'assistant', content: '' })
                  aiIdx = messages.value.length - 1
                }
                loading.value = false
              }
              messages.value[aiIdx].content += parsed.token
              scrollBottom()
            }

            // --- 文章生成完成 ---
            if (parsed.article) {
              const last = messages.value[messages.value.length - 1]
              if (last && last.role === 'assistant') {
                last.article = parsed.article
              } else {
                messages.value.push({ role: 'assistant', content: '', article: parsed.article })
              }
            }

            if (parsed.error && aiIdx === -1) {
              messages.value.push({ role: 'assistant', content: `错误: ${parsed.error}` })
              loading.value = false
            }
          } catch {}
        }
      }
    }
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，AI 助手暂时无法响应。' })
  } finally {
    loading.value = false
    processIdx.value = -1
    if (aiIdx === -1) {
      // 既没有 token 也没有 process
      const hasProcess = messages.value.some(m => m.process && m.process!.length > 0)
      if (!hasProcess) {
        messages.value.push({ role: 'assistant', content: '助手暂时无法响应，请稍后再试。' })
      }
    }
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function newChat() {
  if (loading.value) return
  // 保存旧对话
  saveMessages(threadId.value, messages.value)
  // 创建新对话
  const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
  localStorage.setItem(STORAGE_PREFIX + 'tid', id)
  threadId.value = id
  messages.value = []
  processIdx.value = -1
}
</script>

<template>
  <div class="chat-layout">
    <AdminHeader />

    <main class="chat-main">
      <div class="chat-panel">
        <div class="chat-header">
          <span>AI 创作助手 — 和我聊聊你想写的文章</span>
          <button class="btn-new-chat" @click="newChat" :disabled="loading">+ 新对话</button>
        </div>

        <div class="chat-messages" ref="chatRef">
          <div v-if="messages.length === 0" class="welcome">
            <h3>你好！我是你的博客创作助手 👋</h3>
            <p>告诉我你想写什么主题的文章，我们一起讨论。</p>
            <div class="suggestions">
              <span @click="input = '我想写一篇关于 Python 异步编程的教程'">Python 异步编程教程</span>
              <span @click="input = '帮我规划一篇 Docker 入门的文章'">Docker 入门教程</span>
              <span @click="input = '最近在学习 Rust，想写一篇学习笔记'">Rust 学习笔记</span>
            </div>
          </div>

          <div
            v-for="(m, i) in messages" :key="i"
            class="message-row"
            :class="m.role"
          >
            <div class="avatar">{{ m.role === 'user' ? '👤' : '🤖' }}</div>
            <div class="bubble">
              <!-- 思考过程时间线 -->
              <div v-if="m.process?.length" class="process-timeline">
                <div class="process-title">思考过程</div>
                <div
                  v-for="step in m.process" :key="step.stage"
                  class="process-step"
                  :class="{ done: step.status === 'done', running: step.status === 'running' }"
                >
                  <span class="step-icon">{{ step.status === 'done' ? '✓' : '⟳' }}</span>
                  <span class="step-text">{{ step.message }}</span>
                </div>
              </div>

              <!-- 正文 -->
              <div v-if="m.content" class="message-content">{{ m.content }}</div>

              <!-- 文章卡片 -->
              <div v-if="m.article" class="article-card">
                <div class="card-badge">已自动保存为草稿</div>
                <h4>{{ m.article.title }}</h4>
                <p v-if="m.article.summary" class="article-summary">{{ m.article.summary }}</p>
                <div v-if="m.article.tags?.length" class="article-tags">
                  <span v-for="t in m.article.tags" :key="t" class="tag">{{ t }}</span>
                </div>
                <RouterLink to="/admin/articles" class="import-link">→ 去文章管理查看</RouterLink>
              </div>
            </div>
          </div>

          <!-- 纯文本加载（discuss 阶段，没有思考过程时） -->
          <div v-if="loading" class="message-row assistant">
            <div class="avatar">🤖</div>
            <div class="bubble typing">思考中...</div>
          </div>
        </div>

        <div class="chat-input">
          <textarea
            v-model="input"
            placeholder="输入你的想法..."
            rows="1"
            :disabled="loading"
            @keydown="handleKeydown"
          ></textarea>
          <button @click="handleSend" :disabled="loading || !input.trim()">发送</button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.chat-layout { min-height: 100vh; display: flex; flex-direction: column; background: #f5f6f7; }

.chat-main {
  flex: 1; display: flex; justify-content: center;
  padding: 20px;
}
.chat-panel {
  width: 100%; max-width: 760px; display: flex; flex-direction: column;
  background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  max-height: calc(100vh - 90px);
}
.chat-header {
  padding: 10px 20px; font-size: 14px; color: #888;
  border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center;
}
.btn-new-chat {
  padding: 5px 14px; border: 1px solid #ddd; border-radius: 6px;
  background: #fff; color: #666; font-size: 13px; cursor: pointer;
}
.btn-new-chat:hover { border-color: #4a90d9; color: #4a90d9; }
.btn-new-chat:disabled { opacity: 0.4; cursor: default; }

.chat-messages {
  flex: 1; overflow-y: auto; padding: 20px;
}
.welcome { text-align: center; padding: 30px 0; }
.welcome h3 { font-size: 20px; margin: 0 0 8px; }
.welcome p { color: #888; margin: 0 0 20px; }
.suggestions { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
.suggestions span {
  padding: 8px 16px; border: 1px solid #e0e0e0; border-radius: 18px;
  font-size: 13px; color: #555; cursor: pointer;
}
.suggestions span:hover { border-color: #4a90d9; color: #4a90d9; background: #f5f9ff; }

.message-row { display: flex; gap: 10px; margin-bottom: 18px; }
.message-row.user { flex-direction: row-reverse; }
.message-row.user .bubble { background: #4a90d9; color: #fff; }
.message-row.assistant .bubble { background: #f0f2f5; color: #333; }
.avatar { font-size: 24px; flex-shrink: 0; }
.bubble {
  max-width: 85%; padding: 12px 16px; border-radius: 10px;
  font-size: 14px; line-height: 1.7;
}
.typing { opacity: 0.6; }

/* 思考过程时间线 */
.process-timeline {
  margin-bottom: 12px; padding-bottom: 10px;
  border-bottom: 1px dashed #d0d0d0;
}
.process-title {
  font-size: 12px; color: #999; margin-bottom: 8px; letter-spacing: 1px;
}
.process-step {
  display: flex; align-items: center; gap: 8px;
  padding: 3px 0; font-size: 13px; color: #999;
  transition: color 0.3s;
}
.process-step.done { color: #666; }
.process-step.running { color: #4a90d9; }
.step-icon {
  font-size: 12px; width: 18px; text-align: center; flex-shrink: 0;
}
.process-step.done .step-icon { color: #2e7d32; }
.process-step.running .step-icon {
  color: #4a90d9;
  animation: spin 1.2s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.step-text { flex: 1; }

.message-content { white-space: pre-wrap; }

/* 文章卡片 */
.article-card {
  margin-top: 12px; padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}
.card-badge {
  display: inline-block; padding: 2px 10px; border-radius: 10px;
  background: #e6f7e9; color: #2e7d32; font-size: 12px; margin-bottom: 8px;
}
.article-card h4 { margin: 0 0 6px; font-size: 16px; }
.article-summary { font-size: 13px; color: #888; margin: 0 0 8px; }
.article-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.tag { background: #e8f0fe; color: #4a90d9; padding: 2px 10px; border-radius: 10px; font-size: 12px; }
.import-link { color: #4a90d9; font-size: 13px; text-decoration: none; }
.import-link:hover { text-decoration: underline; }

.chat-input {
  display: flex; gap: 10px; padding: 12px 16px; border-top: 1px solid #eee;
}
.chat-input textarea {
  flex: 1; border: 1px solid #e0e0e0; border-radius: 6px;
  padding: 10px 14px; font-size: 14px; resize: none; outline: none;
  font-family: inherit; max-height: 120px;
}
.chat-input textarea:focus { border-color: #4a90d9; }
.chat-input button {
  padding: 10px 20px; background: #4a90d9; color: #fff;
  border: none; border-radius: 6px; cursor: pointer; font-size: 14px;
}
.chat-input button:disabled { opacity: 0.5; }
</style>
