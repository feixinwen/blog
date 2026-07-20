<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// ===== 动画常量 =====
const SLICE_DELAY = 80        // 每个切片依次延迟 ms
const TRANSITION_DURATION = 1200  // 滑入时长 ms
const FADE_DURATION = 300     // 整体淡出 ms

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

let timer: ReturnType<typeof setInterval> | null = null
let fadeOutTimer: ReturnType<typeof setTimeout> | null = null

const total = computed(() => props.images.length)
const currentImage = computed(() => props.images[currentIndex.value])
const nextImage = computed(() => {
  if (nextIndex.value === null) return ''
  return props.images[nextIndex.value]
})

// 每个切片的 clip-path：只露出自己那条
function sliceClipPath(i: number /* 1-indexed */): string {
  const n = props.sliceCount
  const left = ((i - 1) / n) * 100
  const right = 100 - (i / n) * 100
  return `inset(0 ${right}% 0 ${left}%)`
}

onMounted(() => {
  props.images.forEach(src => {
    const img = new Image()
    img.onerror = () => console.warn(`Banner 图片加载失败: ${src}`)
    img.src = src
  })
  if (total.value > 1) timer = setInterval(nextSlide, props.interval)
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (fadeOutTimer) clearTimeout(fadeOutTimer)
})

function nextSlide() {
  if (isAnimating.value || total.value <= 1) return
  transitionTo((currentIndex.value + 1) % total.value)
  resetTimer()
}
function prevSlide() {
  if (isAnimating.value || total.value <= 1) return
  transitionTo(currentIndex.value === 0 ? total.value - 1 : currentIndex.value - 1)
  resetTimer()
}

function transitionTo(next: number) {
  isAnimating.value = true
  nextIndex.value = next
  sliceActive.value = false
  slicesFading.value = false

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      sliceActive.value = true
    })
  })

  const lastSliceDone = (props.sliceCount - 1) * SLICE_DELAY + TRANSITION_DURATION
  fadeOutTimer = setTimeout(() => {
    currentIndex.value = next
    slicesFading.value = true
  }, lastSliceDone)
}

function onSlicesTransitionEnd(e: TransitionEvent) {
  if (e.propertyName === 'opacity' && slicesFading.value) {
    nextIndex.value = null
    sliceActive.value = false
    slicesFading.value = false
    isAnimating.value = false
  }
}

function resetTimer() {
  if (timer) clearInterval(timer)
  if (total.value > 1) timer = setInterval(nextSlide, props.interval)
}
function stopTimer() { if (timer) clearInterval(timer) }
function startTimer() { if (total.value > 1 && !timer) timer = setInterval(nextSlide, props.interval) }

function scrollDown() {
  emit('scrollToContent')
  document.getElementById('article-list')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <div
    class="banner-slider"
    @mouseenter="stopTimer"
    @mouseleave="startTimer"
  >
    <!-- 底层：完整当前图 -->
    <div
      class="bg-layer"
      :style="{ backgroundImage: `url(${currentImage})` }"
    />

    <!-- 切片层：每个切片覆盖整个 banner，clip-path 裁出各自条带 -->
    <!-- 所有切片背景图完全一致，像素级对齐，不存在拼接问题 -->
    <div
      v-if="nextIndex !== null"
      class="slices-layer"
      :class="{ 'slices-fading': slicesFading }"
      @transitionend="onSlicesTransitionEnd"
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
          backgroundImage: `url(${nextImage})`,
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

    <!-- 指示点 -->
    <div v-if="total > 1" class="dots">
      <span
        v-for="i in total" :key="i"
        :class="{ active: i - 1 === currentIndex }"
        @click="transitionTo(i - 1); resetTimer()"
      />
    </div>
  </div>
</template>

<style scoped>
.banner-slider {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* === 底层 === */
.bg-layer {
  position: absolute;
  inset: 0;
  background-size: 100% 100%;
  background-position: center;
  z-index: 1;
}

/* === 切片层 === */
.slices-layer {
  position: absolute;
  inset: 0;
  z-index: 2;
  transition: opacity v-bind('`${FADE_DURATION}ms`') ease-out;
}
.slices-fading {
  opacity: 0;
  pointer-events: none;
}

/* 每个切片覆盖整个 banner，clip-path 只露出自己那条 */
.slice {
  position: absolute;
  inset: 0;
  background-size: 100% 100%;   /* 和底层完全一致 */
  background-position: center;  /* 和底层完全一致 */
  transition: transform v-bind('`${TRANSITION_DURATION}ms`') cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}
.slice-from-top  { transform: translateY(-100%); }
.slice-from-bottom { transform: translateY(100%); }
.slice-in { transform: translateY(0) !important; }

/* === 暗色遮罩 === */
.overlay {
  position: absolute;
  inset: 0;
  z-index: 3;
  background: rgba(0, 0, 0, 0.3);
  pointer-events: none;
}

/* === 文字 === */
.banner-text {
  position: absolute; inset: 0; z-index: 4;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  pointer-events: none;
}
.banner-text h1 {
  color: #fff; font-size: 42px; font-weight: 700;
  letter-spacing: 6px; text-shadow: 0 2px 12px rgba(0,0,0,0.4);
  margin: 0 0 12px;
}
.banner-text p {
  color: rgba(255,255,255,0.8); font-size: 16px;
  letter-spacing: 3px; text-shadow: 0 1px 6px rgba(0,0,0,0.3);
  margin: 0;
}

/* === 向下箭头 === */
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

/* === 左右按钮 === */
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

/* === 指示点 === */
.dots {
  position: absolute; bottom: 80px; left: 50%;
  transform: translateX(-50%); z-index: 4; display: flex; gap: 10px;
}
.dots span {
  width: 10px; height: 10px; border-radius: 50%;
  background: rgba(255,255,255,0.4);
  cursor: pointer; transition: background 0.3s, transform 0.3s;
}
.dots span.active { background: #fff; transform: scale(1.2); }

@media (max-width: 768px) {
  .banner-text h1 { font-size: 28px; letter-spacing: 3px; }
  .banner-text p { font-size: 14px; }
  .nav-btn { width: 36px; height: 36px; font-size: 18px; }
  .slice { transition-duration: 0.5s; }
}
</style>
