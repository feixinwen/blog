<script setup lang="ts">
import { ref, watch } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { uploadImage } from '@/api'

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const preview = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const uploading = ref(false)

marked.setOptions({
  highlight(code: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
})

function update(val: string) {
  emit('update:modelValue', val)
  preview.value = marked.parse(val) as string
}

watch(() => props.modelValue, (v) => { preview.value = marked.parse(v || '') as string }, { immediate: true })

async function handleUpload() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    uploading.value = true
    try {
      const res = await uploadImage(file)
      const url = res.data.url
      const tag = `![${file.name}](${url})`

      // 在光标位置插入，或追加到末尾
      const ta = textareaRef.value
      if (ta) {
        const start = ta.selectionStart
        const end = ta.selectionEnd
        const newVal = props.modelValue.slice(0, start) + tag + props.modelValue.slice(end)
        update(newVal)
        // 恢复焦点和光标位置
        setTimeout(() => {
          ta.focus()
          ta.setSelectionRange(start + tag.length, start + tag.length)
        })
      } else {
        update(props.modelValue + '\n' + tag)
      }
    } catch {
      alert('图片上传失败，请重试')
    } finally {
      uploading.value = false
    }
  }
  input.click()
}
</script>

<template>
  <div class="editor">
    <div class="pane">
      <div class="pane-header">
        编辑
        <button class="btn-upload" @click="handleUpload" :disabled="uploading">
          {{ uploading ? '上传中...' : '上传图片' }}
        </button>
      </div>
      <textarea
        ref="textareaRef"
        :value="modelValue"
        @input="update(($event.target as HTMLTextAreaElement).value)"
        placeholder="使用 Markdown 语法编写..."
      ></textarea>
    </div>
    <div class="pane">
      <div class="pane-header">预览</div>
      <div class="markdown-body" v-html="preview"></div>
    </div>
  </div>
</template>

<style scoped>
.editor {
  display: flex;
  gap: 16px;
  min-height: 500px;
}
.pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
}
.pane-header {
  background: #f8f8f8;
  padding: 8px 12px;
  font-size: 13px;
  color: #666;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.btn-upload {
  background: #4a90d9;
  color: #fff;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}
.btn-upload:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
textarea {
  flex: 1;
  border: none;
  padding: 12px;
  font-size: 14px;
  font-family: 'Consolas', 'Monaco', monospace;
  resize: none;
  outline: none;
  line-height: 1.8;
}
.markdown-body {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.8;
}
.markdown-body :deep(pre) { background: #f8f8f8; padding: 12px; border-radius: 4px; overflow-x: auto; }
.markdown-body :deep(code) { background: #f5f5f5; padding: 2px 4px; border-radius: 2px; font-size: 13px; }
.markdown-body :deep(pre code) { background: none; padding: 0; }
.markdown-body :deep(blockquote) { border-left: 3px solid #4a90d9; padding-left: 12px; color: #888; }
</style>
