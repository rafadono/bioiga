<template>
  <div class="metrics-grid">
    <div class="metric-card glass-panel">
      <span class="metric-label">Progreso</span>
      <div class="metric-value font-mono">
        {{ currentGen }} / {{ maxGen }}
      </div>
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>

    <div class="metric-card glass-panel">
      <span class="metric-label">Mejor Fitness</span>
      <div class="metric-value font-mono highlight">
        {{ bestFitness !== null ? bestFitness.toFixed(4) : '---' }}
      </div>
      <span class="metric-sub">Max global de la población</span>
    </div>

    <div class="metric-card glass-panel">
      <span class="metric-label">Algoritmo Activo</span>
      <div class="metric-value">
        {{ algorithm }}
      </div>
      <span class="metric-sub">Capa 1 Scientfic Core</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  currentGen: number
  maxGen: number
  bestFitness: number | null
  algorithm: string
}>()

const progressPercent = computed(() => {
  if (!props.maxGen) return 0
  return Math.min(100, Math.round((props.currentGen / props.maxGen) * 100))
})
</script>

<style scoped>
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.metric-card {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f8fafc;
}

.highlight {
  color: #38bdf8;
}

.metric-sub {
  font-size: 0.7rem;
  color: #64748b;
}

.progress-bar-bg {
  height: 4px;
  background: #0f172a;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 0.25rem;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #38bdf8, #818cf8);
  transition: width 0.3s ease;
}
</style>
