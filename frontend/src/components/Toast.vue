<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
const type = ref<'success' | 'error'>('success')
let timer: ReturnType<typeof setTimeout> | null = null

function show(msg: string, t: 'success' | 'error' = 'success') {
  message.value = msg
  type.value = t
  visible.value = true
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => { visible.value = false }, 2400)
}

defineExpose({ show })
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="toast" :class="type">
      {{ type === 'success' ? '✓' : '✕' }} {{ message }}
    </div>
  </Teleport>
</template>

<style scoped>
.toast {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  padding: 10px 24px;
  border-radius: 6px;
  font-size: 14px;
  color: #fff;
  animation: toast-in 0.3s ease;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
.toast.success { background: #52c41a; }
.toast.error { background: #e74c3c; }
@keyframes toast-in {
  from { opacity: 0; transform: translateX(-50%) translateY(-12px); }
  to   { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
