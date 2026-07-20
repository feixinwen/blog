<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId = 0

// ===== 背景粒子 =====
interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
}
const bgParticles: Particle[] = []
const BG_COUNT = 35

// ===== 鼠标拖尾 =====
interface TrailDot {
  x: number
  y: number
  alpha: number
  size: number
}
const trails: TrailDot[] = []
const MAX_TRAILS = 30

// ===== 点击爆炸 =====
interface BurstParticle {
  x: number
  y: number
  vx: number
  vy: number
  alpha: number
  size: number
  life: number
  maxLife: number
  color: string
}
const bursts: BurstParticle[] = []

const mouse = { x: -9999, y: -9999 }

onMounted(() => {
  const canvas = canvasRef.value!
  const ctx = canvas.getContext('2d')!
  resize()
  initBgParticles()
  animate(ctx)
  window.addEventListener('resize', resize)
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('click', onClick)
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', resize)
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('click', onClick)
})

function resize() {
  const canvas = canvasRef.value!
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
}

function initBgParticles() {
  const w = canvasRef.value!.width
  const h = canvasRef.value!.height
  bgParticles.length = 0
  for (let i = 0; i < BG_COUNT; i++) {
    bgParticles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      size: Math.random() * 2 + 1.5,
    })
  }
}

function onMouseMove(e: MouseEvent) {
  mouse.x = e.clientX
  mouse.y = e.clientY

  // 添加拖尾点
  trails.push({ x: e.clientX, y: e.clientY, alpha: 0.5, size: 3 + Math.random() * 2 })
  if (trails.length > MAX_TRAILS) trails.shift()
}

function onClick(e: MouseEvent) {
  // 在点击位置生成 10-15 个爆炸粒子
  const count = 10 + Math.floor(Math.random() * 6)
  const colors = ['#a0c4f0', '#b8d4f8', '#c8c8d8', '#d0d8e8', '#e0c8f0', '#f0c8c8']
  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5
    const speed = 1.5 + Math.random() * 3
    bursts.push({
      x: e.clientX,
      y: e.clientY,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 1.5, // 偏上飘
      alpha: 1,
      size: 2 + Math.random() * 3,
      life: 0,
      maxLife: 40 + Math.random() * 30,
      color: colors[Math.floor(Math.random() * colors.length)],
    })
  }
}

function animate(ctx: CanvasRenderingContext2D) {
  const canvas = canvasRef.value!
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // ===== 1. 绘制背景粒子 =====
  for (const p of bgParticles) {
    p.x += p.vx
    p.y += p.vy
    if (p.x < 0 || p.x > canvas.width) p.vx *= -1
    if (p.y < 0 || p.y > canvas.height) p.vy *= -1

    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(180, 195, 215, 0.35)'
    ctx.fill()

    // 鼠标附近连线
    const dx = mouse.x - p.x
    const dy = mouse.y - p.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist < 140) {
      ctx.beginPath()
      ctx.moveTo(p.x, p.y)
      ctx.lineTo(mouse.x, mouse.y)
      ctx.strokeStyle = `rgba(155, 170, 200, ${0.1 * (1 - dist / 140)})`
      ctx.lineWidth = 0.4
      ctx.stroke()
    }
  }

  // ===== 2. 绘制鼠标拖尾 =====
  for (let i = 0; i < trails.length; i++) {
    const t = trails[i]
    t.alpha *= 0.94  // 渐隐
    t.size *= 0.97   // 渐小
    if (t.alpha < 0.01) {
      trails.splice(i, 1)
      i--
      continue
    }
    ctx.beginPath()
    ctx.arc(t.x, t.y, t.size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(170, 190, 220, ${t.alpha})`
    ctx.fill()
  }

  // ===== 3. 绘制点击爆炸粒子 =====
  for (let i = 0; i < bursts.length; i++) {
    const b = bursts[i]
    b.x += b.vx
    b.y += b.vy
    b.vy += 0.03  // 重力
    b.life++
    b.alpha = 1 - b.life / b.maxLife
    b.size *= 0.98

    if (b.alpha <= 0 || b.life >= b.maxLife) {
      bursts.splice(i, 1)
      i--
      continue
    }

    ctx.beginPath()
    ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2)
    ctx.fillStyle = b.color.replace(')', `, ${b.alpha})`).replace('rgb', 'rgba')
    ctx.fill()
  }

  animationId = requestAnimationFrame(() => animate(ctx))
}
</script>

<template>
  <canvas ref="canvasRef" class="particle-canvas" />
</template>

<style scoped>
.particle-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}
</style>
