<template>
  <div class="viewport-container glass-panel glow-box">
    <div class="viewport-header">
      <span class="viewport-title">Vista de Densidad y Espesor Variable (NURBS / SIMP)</span>
      <span class="viewport-badge font-mono" v-if="solution">
        {{ gridSize }}x{{ gridSize }} Elementos IGA ({{ solution.length }} vars)
      </span>
    </div>

    <div class="canvas-wrapper">
      <canvas ref="canvasRef" width="480" height="480" class="nurbs-canvas"></canvas>
      <div v-if="!solution" class="empty-overlay">
        <p>Inicia la optimización para visualizar la distribución de espesores y material en tiempo real</p>
      </div>
    </div>

    <!-- Density / Thickness Colorbar Legend -->
    <div class="thickness-legend">
      <span class="legend-label">Espesor Relativo t/t0:</span>
      <div class="legend-gradient"></div>
      <div class="legend-values font-mono">
        <span>0% (Vacío)</span>
        <span>50% (Delgado)</span>
        <span>100% (Sólido)</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'

const props = defineProps<{
  solution: number[] | null
  numVariables: number
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)

const gridSize = computed(() => {
  return Math.round(Math.sqrt(props.numVariables || 100))
})

function drawViewport() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = canvas.width
  const height = canvas.height
  ctx.clearRect(0, 0, width, height)

  // Background
  ctx.fillStyle = '#0f172a'
  ctx.fillRect(0, 0, width, height)

  const n = gridSize.value
  const cellSize = width / n

  if (props.solution && props.solution.length >= n * n) {
    // Draw continuous SIMP element densities / variable thickness
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const rho = props.solution[i * n + j] // float in [0.0, 1.0]

        // Continuous color interpolation:
        // rho = 1.0 -> Solid (#0f172a / dark material or cyan highlight)
        // rho = 0.0 -> Void (#f8fafc / light background)
        const intensity = Math.round((1 - rho) * 230 + 20)
        ctx.fillStyle = `rgb(${intensity}, ${intensity}, ${intensity})`
        ctx.fillRect(j * cellSize, i * cellSize, cellSize, cellSize)
      }
    }

    // Draw NURBS Isoline Grid overlay
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.25)'
    ctx.lineWidth = 1
    for (let i = 0; i <= n; i++) {
      ctx.beginPath()
      ctx.moveTo(0, i * cellSize)
      ctx.lineTo(width, i * cellSize)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(i * cellSize, 0)
      ctx.lineTo(i * cellSize, height)
      ctx.stroke()
    }

    // Draw Control Points Grid
    ctx.fillStyle = '#38bdf8'
    const step = Math.max(1, Math.floor(n / 8))
    for (let i = 0; i <= n; i += step) {
      for (let j = 0; j <= n; j += step) {
        ctx.beginPath()
        ctx.arc(j * cellSize, i * cellSize, 3, 0, 2 * Math.PI)
        ctx.fill()
      }
    }
  } else {
    // Grid preview placeholder
    ctx.strokeStyle = '#1e293b'
    ctx.lineWidth = 1
    const pSize = width / 10
    for (let i = 0; i <= 10; i++) {
      ctx.beginPath()
      ctx.moveTo(0, i * pSize)
      ctx.lineTo(width, i * pSize)
      ctx.stroke()
      ctx.beginPath()
      ctx.moveTo(i * pSize, 0)
      ctx.lineTo(i * pSize, height)
      ctx.stroke()
    }
  }
}

watch(() => props.solution, () => {
  drawViewport()
}, { deep: true })

onMounted(() => {
  drawViewport()
})
</script>

<style scoped>
.viewport-container {
  display: flex;
  flex-direction: column;
  padding: 1.25rem;
  flex: 1;
}

.viewport-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.85rem;
}

.viewport-title {
  font-weight: 700;
  font-size: 0.95rem;
  color: #f8fafc;
}

.viewport-badge {
  font-size: 0.75rem;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.canvas-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #090d16;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #1e293b;
  aspect-ratio: 1;
}

.nurbs-canvas {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.empty-overlay {
  position: absolute;
  color: #64748b;
  font-size: 0.85rem;
  text-align: center;
  padding: 1rem;
}

.thickness-legend {
  margin-top: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.legend-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
}

.legend-gradient {
  height: 10px;
  border-radius: 5px;
  background: linear-gradient(90deg, #f8fafc, #94a3b8, #0f172a);
  border: 1px solid #334155;
}

.legend-values {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #64748b;
}
</style>
