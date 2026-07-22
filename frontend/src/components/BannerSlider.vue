<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// ===== 动画常量 =====
const SLICE_DELAY = 80
const TRANSITION_DURATION = 1200
const FADE_DURATION = 300

const props = withDefaults(defineProps<{
  images: string[]
  title?: string
  subtitle?: string
  sliceCount?: number
  interval?: number
}>(), {
  sliceCount: 5,
  interval: 25000,
})

const emit = defineEmits<{ scrollToContent: [] }>()

const currentIndex = ref(0)
const nextIndex = ref<number | null>(null)
const isAnimating = ref(false)
const sliceActive = ref(false)
const slicesFading = ref(false)

let autoTimer: ReturnType<typeof setTimeout> | null = null
let animTimer: ReturnType<typeof setTimeout> | null = null
let fadeTimer: ReturnType<typeof setTimeout> | null = null

const total = computed(() => props.images.length)
const currentImage = computed(() => props.images[currentIndex.value])

// 每个切片用 clip-path 裁出自己那条
function sliceClipPath(i: number /* 1-indexed */): string {
  const n = props.sliceCount
  const left = ((i - 1) / n) * 100
  const right = 100 - (i / n) * 100
  return `inset(0 ${right}% 0 ${left}%)`
}

// 预加载 + 启动轮播
onMounted(() => {
  props.images.forEach(src => {
    new Image().src = src
  })
  if (total.value > 1) scheduleNext(props.interval)
})
onUnmounted(() => {
  if (autoTimer) clearTimeout(autoTimer)
  if (animTimer) clearTimeout(animTimer)
  if (fadeTimer) clearTimeout(fadeTimer)
})

// 递归定时：动画全部完成后才倒计时下一次
function scheduleNext(delay: number) {
  if (autoTimer) clearTimeout(autoTimer)
  autoTimer = setTimeout(() => {
    nextSlide()
  }, delay)
}

function nextSlide() {
  if (isAnimating.value || total.value <= 1) return
  const next = (currentIndex.value + 1) % total.value
  transitionTo(next)
}
function prevSlide() {
  if (isAnimating.value || total.value <= 1) return
  const next = currentIndex.value === 0 ? total.value - 1 : currentIndex.value - 1
  transitionTo(next)
}

function transitionTo(next: number) {
  isAnimating.value = true
  nextIndex.value = next
  sliceActive.value = false
  slicesFading.value = false

  // 双 RAF：确保浏览器先绘制切片的初始位置（屏幕外），再触发滑入
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      sliceActive.value = true
    })
  })

  // 等最后一片滑到位
  const lastSliceDone = (props.sliceCount - 1) * SLICE_DELAY + TRANSITION_DURATION
  animTimer = setTimeout(() => {
    // 此时切片完全遮住底层，安全切换背景图
    currentIndex.value = next
    // 切片层整体淡出
    slicesFading.value = true

    // 淡出完成后清理
    fadeTimer = setTimeout(() => {
      nextIndex.value = null
      sliceActive.value = false
      slicesFading.value = false
      isAnimating.value = false
      // 动画彻底结束，开始下一次倒计时
      scheduleNext(props.interval)
    }, FADE_DURATION)
  }, lastSliceDone)
}

function stopTimer() { if (autoTimer) { clearTimeout(autoTimer); autoTimer = null } }
function resumeTimer() { if (!autoTimer && total.value > 1) scheduleNext(props.interval) }

function scrollDown() {
  emit('scrollToContent')
  document.getElementById('article-list')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <div
    class="banner-slider"
    @mouseenter="stopTimer"
    @mouseleave="resumeTimer"
  >
    <!-- 底层：完整当前图 -->
    <div
      class="bg-layer"
      :style="{ backgroundImage: `url(${currentImage})` }"
    />

    <!-- 切片层 -->
    <div
      v-if="nextIndex !== null"
      class="slices-layer"
      :class="{ 'slices-fading': slicesFading }"
    >
      <div
        v-for="i in sliceCount"
        :key="i"
        class="slice"
        :class="{
          'slice-from-top': i % 2 === 1,
          'slice-from-bottom': i % 2 === 0,
          'slice-in': sliceActive,
        }"
        :style="{
          backgroundImage: `url(${images[nextIndex]})`,
          clipPath: sliceClipPath(i),
          transitionDelay: `${(i - 1) * SLICE_DELAY}ms`,
        }"
      />
    </div>

    <!-- 暗色遮罩 -->
    <div class="overlay" />

    <!-- 文字 -->
    <div class="banner-text" v-if="title || subtitle">
      <h1 v-if="title">{{ title }}</h1>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>

    <!-- 向下箭头 -->
    <div class="scroll-arrow" @click="scrollDown">
      <span /><span />
    </div>

    <!-- 左右按钮 -->
    <button v-if="total > 1" class="nav-btn nav-prev" @click="prevSlide">&lt;</button>
    <button v-if="total > 1" class="nav-btn nav-next" @click="nextSlide">&gt;</button>

  </div>
</template>

<style scoped>
.banner-slider {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
.bg-layer {
  position: absolute; inset: 0;
  background-size: 100% 100%;
  background-position: center;
  z-index: 1;
}
.slices-layer {
  position: absolute; inset: 0; z-index: 2;
  transition: opacity v-bind('`${FADE_DURATION}ms`') ease-out;
}
.slices-fading { opacity: 0; pointer-events: none; }

.slice {
  position: absolute; inset: 0;
  background-size: 100% 100%;
  background-position: center;
  transition: transform v-bind('`${TRANSITION_DURATION}ms`') cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}
.slice-from-top  { transform: translateY(-100%); }
.slice-from-bottom { transform: translateY(100%); }
.slice-in { transform: translateY(0) !important; }

.overlay {
  position: absolute; inset: 0; z-index: 3;
  background: rgba(0, 0, 0, 0.3);
  pointer-events: none;
}
.banner-text {
  position: absolute; inset: 0; z-index: 4;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  pointer-events: none;
}
.banner-text h1 {
  font-family: 'STKaiti', 'KaiTi', '楷体', 'STSong', serif;
  font-size: 48px;
  font-weight: 700;
  letter-spacing: 8px;
  margin: 0 0 14px;
  cursor: default;
  user-select: none;
  pointer-events: auto;  /* 父容器 pointer-events: none，这里恢复使 :hover 生效 */
  /* 默认：白色 + 立体阴影 + 光晕 */
  color: #fff;
  text-shadow:
    0 2px 4px rgba(0, 0, 0, 0.35),
    0 0 20px rgba(255, 255, 255, 0.15);
  transition: text-shadow 0.3s;
}
/* 悬停：暖金粉渐变在文字内流动 */
.banner-text h1:hover {
  background: linear-gradient(
    135deg,
    #f0c27b 0%,
    #e2b0ff 20%,
    #fbc2eb 40%,
    #a1c4fd 60%,
    #f0c27b 80%,
    #e2b0ff 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: none;
  animation: warm-flow 3s linear infinite;
}
@keyframes warm-flow {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}
.banner-text p {
  font-family: 'STKaiti', 'KaiTi', '楷体', 'STSong', serif;
  color: rgba(255,255,255,0.75);
  font-size: 17px;
  letter-spacing: 4px;
  text-shadow: 0 1px 6px rgba(0,0,0,0.3);
  margin: 0;
}

.scroll-arrow {
  position: absolute; bottom: 30px; left: 50%;
  transform: translateX(-50%); z-index: 4; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
}
.scroll-arrow span {
  display: block; width: 20px; height: 20px;
  border-right: 2px solid rgba(255,255,255,0.7);
  border-bottom: 2px solid rgba(255,255,255,0.7);
  transform: rotate(45deg);
  animation: bounce 1.6s ease-in-out infinite;
}
.scroll-arrow span:nth-child(2) { animation-delay: 0.2s; }
@keyframes bounce {
  0%, 100% { opacity: 0.3; transform: rotate(45deg) translate(0,0); }
  50% { opacity: 1; transform: rotate(45deg) translate(4px,4px); }
}

.nav-btn {
  position: absolute; top: 50%; transform: translateY(-50%); z-index: 4;
  background: rgba(255,255,255,0.15); border: none; color: #fff;
  font-size: 24px; width: 44px; height: 44px; border-radius: 50%;
  cursor: pointer; opacity: 0; transition: opacity 0.3s;
}
.banner-slider:hover .nav-btn { opacity: 1; }
.nav-btn:hover { background: rgba(255,255,255,0.3); }
.nav-prev { left: 20px; }
.nav-next { right: 20px; }

@media (max-width: 768px) {
  .banner-text h1 { font-size: 28px; letter-spacing: 3px; }
  .banner-text p { font-size: 14px; }
  .nav-btn { width: 36px; height: 36px; font-size: 18px; }
  .slice { transition-duration: 0.5s; }
}
</style>
