<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{ content: string }>()

interface TocItem {
  id: string
  text: string
  level: number
}

const items = ref<TocItem[]>([])
const activeId = ref('')

// 解析 Markdown 内容提取 h2/h3 标题
function parseHeadings() {
  const result: TocItem[] = []
  const regex = /^(#{2,3})\s+(.+)$/gm
  let match: RegExpExecArray | null
  while ((match = regex.exec(props.content)) !== null) {
    const level = match[1].length
    const text = match[2].trim()
    const id = text.toLowerCase().replace(/\s+/g, '-').replace(/[^\w一-鿿-]/g, '')
    result.push({ id, text, level })
  }
  items.value = result
}

// IntersectionObserver 监控标题可见性
let observer: IntersectionObserver | null = null

function setupObserver() {
  // 等 DOM 渲染完
  setTimeout(() => {
    const headings = document.querySelectorAll('.markdown-body h2, .markdown-body h3')
    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            activeId.value = entry.target.id
          }
        }
      },
      { rootMargin: '-80px 0px -60% 0px' }
    )
    headings.forEach(h => observer!.observe(h))
  }, 500)
}

function scrollTo(id: string) {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

watch(() => props.content, () => {
  parseHeadings()
  setupObserver()
})

onMounted(() => { parseHeadings(); setupObserver() })
onUnmounted(() => { if (observer) observer.disconnect() })
</script>

<template>
  <nav v-if="items.length > 0" class="toc">
    <div class="toc-title">目录</div>
    <ul>
      <li
        v-for="item in items"
        :key="item.id"
        :class="{ active: item.id === activeId, 'toc-h3': item.level === 3 }"
        @click="scrollTo(item.id)"
      >
        {{ item.text }}
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.toc {
  width: 100%;
  max-height: calc(100vh - 180px);
  overflow-y: auto;
  background: rgba(255,255,255,0.95);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  padding: 16px;
  font-size: 13px;
}
.toc-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}
.toc ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.toc li {
  padding: 5px 8px;
  color: #666;
  cursor: pointer;
  border-radius: 4px;
  line-height: 1.5;
  transition: background 0.15s, color 0.15s;
}
.toc li:hover {
  background: #f0f4f8;
  color: #4a90d9;
}
.toc li.active {
  color: #4a90d9;
  font-weight: 600;
  background: #eef3fa;
}
.toc li.toc-h3 {
  padding-left: 20px;
  font-size: 12px;
}
@media (max-width: 1200px) {
  .toc { display: none; }
}
</style>
