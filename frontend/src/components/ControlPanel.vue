<template>
  <aside :class="['sidebar-panel', 'glass-panel', { collapsed: isCollapsed }]">
    <div class="sidebar-header">
      <Icon name="sliders" :size="18" v-if="!isCollapsed" />
      <h2 class="sidebar-title" v-if="!isCollapsed">Configuración del Optimizador</h2>
      <button
        @click="isCollapsed = !isCollapsed"
        class="btn-icon-collapse"
        :title="isCollapsed ? 'Expandir Barra Lateral' : 'Colapsar Barra Lateral (Más Espacio Canvas)'"
      >
        <Icon :name="isCollapsed ? 'chevron-right' : 'chevron-left'" :size="16" />
      </button>
    </div>

    <!-- Content visible only when expanded -->
    <template v-if="!isCollapsed">


    <!-- Minimum Simulation Requirements Checklist Banner -->
    <div class="validation-banner" :class="{ 'is-valid': isValidToStart }">
      <div class="banner-header">
        <Icon :name="isValidToStart ? 'shield' : 'warning'" :size="16" />
        <span class="banner-title">
          {{ isValidToStart ? 'Estructura Lista para Simular' : 'Requisitos Mínimos Requeridos' }}
        </span>
      </div>
      <ul class="checklist font-mono">
        <li :class="{ ok: true }">✔ Geometría NURBS Grid ({{ form.num_variables }} vars)</li>
        <li :class="{ ok: hasMaterial }">{{ hasMaterial ? '✔' : '✖' }} Material Estructural Asignado</li>
        <li :class="{ ok: true }">✔ Apoyo Borde Dirichlet / PBC Periódico</li>
        <li :class="{ ok: true }">✔ Estado de Cargas (Neumann / Modo Libre)</li>
      </ul>

    </div>

    <div class="accordion-container">
      <!-- Category 1: Optimization & Metaheuristics -->
      <details class="accordion-group" open>
        <summary class="accordion-summary">
          <Icon name="cpu" :size="16" />
          <span>Configuración del Optimizador</span>
        </summary>

        <div class="form-container">
          <div class="form-group">
            <label class="form-label">Estrategia / Tipo de Análisis</label>
            <select v-model="form.optimization_type" class="form-select" :disabled="isRunning">
              <option value="iga_direct">Análisis IGA Directo (Frecuencias Normales Sin Optimizar)</option>
              <option value="topology">Topológica (Distribución SIMP)</option>
              <option value="shape">De Forma (Deformación Bordes NURBS)</option>
              <option value="sizing">De Tamaño (Espesor de Secciones)</option>
              <option value="combined">Combinada (Forma + Topología + Tamaño)</option>
            </select>
          </div>


          <div class="form-group">
            <label class="form-label">Modo de Normalización / Escala</label>
            <select v-model="form.normalization_mode" class="form-select" :disabled="isRunning">
              <option value="adimensional">Adimensional (Leissa w_bar, F_bar)</option>
              <option value="dimensional">Dimensiones Físicas (Hz, N, Pa, m)</option>
              <option value="min_max">Normalización Min-Max [0.0, 1.0]</option>
              <option value="z_score">Estandarización Z-Score (μ=0, σ=1)</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Algoritmo Metaheurístico</label>
            <select v-model="form.algorithm" class="form-select" :disabled="isRunning">
              <option value="MPMBPSO">MPMBPSO (Multi-Population BPSO)</option>
              <option value="MPGA">MPGA (Multi-Population Genetic Algorithm)</option>
              <option value="MPBFA">MPBFA (Binary Firefly Algorithm)</option>
              <option value="MPBGWO">MPBGWO (Grey Wolf Optimizer)</option>
              <option value="MPBBA">MPBBA (Binary Bat Algorithm)</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Generaciones Maximás</label>
            <div class="range-number-pair">
              <input type="range" v-model.number="form.generations" min="10" max="300" step="10" class="range-input" :disabled="isRunning" />
              <input type="number" v-model.number="form.generations" min="10" max="1000" step="10" class="form-input num-box" :disabled="isRunning" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Población por Isla</label>
            <div class="range-number-pair">
              <input type="range" v-model.number="form.pop_size" min="4" max="100" step="2" class="range-input" :disabled="isRunning" />
              <input type="number" v-model.number="form.pop_size" min="4" max="500" step="2" class="form-input num-box" :disabled="isRunning" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Islas Paralelas</label>
              <input type="number" v-model.number="form.num_islands" min="1" max="16" class="form-input" :disabled="isRunning" />
            </div>
            <div class="form-group">
              <label class="form-label">Variables Grid</label>
              <input type="number" v-model.number="form.num_variables" min="16" max="400" step="4" class="form-input" :disabled="isRunning" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Volumen Objetivo SIMP (Vtarget)</label>
            <div class="range-number-pair">
              <input type="range" v-model.number="form.target_volume" min="0.1" max="0.9" step="0.05" class="range-input" :disabled="isRunning" />
              <input type="number" v-model.number="form.target_volume" min="0.05" max="0.95" step="0.05" class="form-input num-box" :disabled="isRunning" />
            </div>
          </div>

          <div class="form-group" v-if="form.algorithm === 'MPMBPSO'">
            <label class="form-label">Función de Transferencia Binaria</label>
            <select v-model="form.transfer_function" class="form-select" :disabled="isRunning">
              <option value="S">S-Shape (Sigmoide tradicional)</option>
              <option value="V">V-Shape (Tanh Absoluto)</option>
              <option value="U">U-Shape (Cuadrática)</option>
              <option value="Z">Z-Shape (Exponencial Z4)</option>
            </select>
          </div>


          <div class="toggle-group">
            <label class="toggle-label">
              <input type="checkbox" v-model="form.continuous_densities" :disabled="isRunning" />
              <span>Espesores variables y densidades continuas [0.0, 1.0]</span>
            </label>
          </div>
        </div>
      </details>
    </div>

    <!-- Action Buttons Fixed at Bottom with Validation Check -->
    <div class="action-buttons">
      <button
        v-if="!isRunning && !isPaused"
        @click="onStart"
        :disabled="!isValidToStart"
        class="btn btn-primary btn-block"
      >
        <Icon name="play" :size="16" />
        <span>{{ isValidToStart ? 'Iniciar Optimización' : 'Complete Requisitos Previos' }}</span>
      </button>

      <button v-if="isRunning" @click="$emit('pause')" class="btn btn-secondary btn-block">
        <Icon name="pause" :size="16" />
        <span>Pausar</span>
      </button>

      <button v-if="isPaused" @click="$emit('resume')" class="btn btn-primary btn-block">
        <Icon name="refresh" :size="16" />
        <span>Reanudar</span>
      </button>

      <button v-if="isRunning || isPaused" @click="$emit('stop')" class="btn btn-danger btn-block">
        <Icon name="stop" :size="16" />
        <span>Detener</span>
      </button>
    </div>
    </template>
  </aside>
</template>


<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import Icon from './Icon.vue'
import type { OptimizationConfig } from '../types'

const isCollapsed = ref<boolean>(false)


const props = defineProps<{
  status: string
}>()

const emit = defineEmits<{
  (e: 'start', config: OptimizationConfig): void
  (e: 'pause'): void
  (e: 'resume'): void
  (e: 'stop'): void
}>()

const hasMaterial = ref<boolean>(true)
const hasBoundaryConditions = ref<boolean>(true)
const hasPointLoads = ref<boolean>(true)

const isValidToStart = computed(() => {
  return (
    hasMaterial.value &&
    form.generations >= 10 &&
    form.pop_size >= 4 &&
    form.num_variables >= 16
  )
})


const form = reactive<OptimizationConfig>({
  algorithm: 'MPMBPSO',
  optimization_type: 'topology',
  normalization_mode: 'adimensional',
  continuous_densities: true,
  generations: 50,
  pop_size: 20,
  num_islands: 4,
  migration_interval: 5,
  migration_rate: 0.1,
  target_volume: 0.5,
  num_variables: 100,
  transfer_function: 'S',
  is_time_varying: true,
  w: 0.729,
  c1: 1.494,
  c2: 1.494,
  v_max: 6.0,
})

const isRunning = computed(() => props.status === 'running')
const isPaused = computed(() => props.status === 'paused')

function onStart() {
  if (!isValidToStart.value) return
  emit('start', { ...form })
}
</script>

<style scoped>
.sidebar-panel {
  padding: 1rem;
  width: 100%;
  max-width: 350px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  transition: all 0.25s ease-in-out;
}

.sidebar-panel.collapsed {
  max-width: 48px;
  padding: 0.6rem 0.4rem;
  overflow: hidden;
  align-items: center;
}

.btn-icon-collapse {
  background: #1e293b;
  border: 1px solid #334155;
  color: #38bdf8;
  border-radius: 6px;
  padding: 0.35rem 0.45rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: auto;
  transition: all 0.15s ease;
}

.btn-icon-collapse:hover {
  background: #38bdf8;
  color: #0f172a;
}

.sidebar-panel.collapsed .btn-icon-collapse {
  margin-left: 0;
  width: 100%;
}



.validation-banner {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  padding: 0.6rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.validation-banner.is-valid {
  background: rgba(52, 211, 153, 0.1);
  border-color: rgba(52, 211, 153, 0.3);
}

.banner-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #f87171;
  font-size: 0.78rem;
  font-weight: 700;
}

.validation-banner.is-valid .banner-header {
  color: #34d399;
}

.checklist {
  list-style: none;
  font-size: 0.72rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.checklist li {
  color: #f87171;
}

.checklist li.ok {
  color: #34d399;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #38bdf8;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
}

.sidebar-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f8fafc;
}

.accordion-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.accordion-group {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 6px;
  overflow: hidden;
}

.accordion-summary {
  padding: 0.6rem 0.75rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: #cbd5e1;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #1e293b;

  &:hover {
    color: #38bdf8;
  }
}

.form-container {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.val {
  color: #38bdf8;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
}

.range-number-pair {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.num-box {
  width: 65px !important;
  padding: 0.2rem 0.3rem !important;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #38bdf8;
  text-align: center;
}

.range-input {
  flex: 1;
  accent-color: #38bdf8;
  cursor: pointer;
}

.toggle-group {
  margin-top: 0.1rem;
}

.toggle-label {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: #cbd5e1;
  cursor: pointer;
  line-height: 1.3;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-top: auto;
  border-top: 1px solid #334155;
  padding-top: 0.5rem;
}

.btn-block {
  width: 100%;
  justify-content: center;
}
</style>
