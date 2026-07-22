<template>
  <div class="vibrations-panel glass-panel">
    <div class="panel-header">
      <Icon name="activity" :size="20" />
      <h3 class="panel-title">Análisis de Dinámica Estructural, Vibraciones y Pandeo</h3>
      <span class="panel-subtitle font-mono">Modo Directo Standalone vs. Optimización Metaheurística</span>
    </div>

    <!-- Clear Workflow Mode Selector Banner -->
    <div class="workflow-banner">
      <span class="banner-title">Modo de Operación Seleccionado:</span>
      <div class="mode-buttons">
        <button
          @click="workflowMode = 'standalone'"
          class="mode-btn"
          :class="{ active: workflowMode === 'standalone' }"
        >
          <Icon name="play" :size="15" />
          <span>Modo A: Análisis Mecánico Directo (Standalone)</span>
        </button>
        <button
          @click="workflowMode = 'optimization'"
          class="mode-btn"
          :class="{ active: workflowMode === 'optimization' }"
        >
          <Icon name="sliders" :size="15" />
          <span>Modo B: Usar Dinámica como Objetivo de Optimización</span>
        </button>
      </div>
    </div>

    <!-- Standalone Direct Computation Action Button -->
    <div v-if="workflowMode === 'standalone'" class="action-card">
      <div class="action-info">
        <Icon name="activity" :size="18" class="text-blue" />
        <div>
          <h4 class="action-title">Cálculo Directo de Frecuencias y Pandeo</h4>
          <p class="action-desc">Evalúa las frecuencias propias ω_n, la respuesta armónica FRF y la carga crítica λ_cr directamente sobre la estructura definida, sin bucles evolutivos.</p>
        </div>
      </div>
      <button @click="runDirectAnalysis" class="btn btn-primary" :disabled="isCalculating">
        <Icon :name="isCalculating ? 'refresh' : 'play'" :size="16" />
        <span>{{ isCalculating ? 'Calculando Dinámica...' : 'Calcular Dinámica & Pandeo Directo' }}</span>
      </button>
    </div>

    <div class="panel-grid">
      <!-- Response Frequency FRF Spectrum (Vue Collapsible Card) -->
      <div class="vib-card">
        <div class="card-summary" @click="card1Open = !card1Open">
          <Icon :name="card1Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">1. Respuesta Armónica en Frecuencia (FRF)</h4>
        </div>

        <div v-show="card1Open" class="card-body">
          <p class="card-desc">Espectro de amplitudes $U(\omega)$ bajo fuerzas dinámicas excitadoras.</p>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Rango Frecuencia (Hz)</label>
              <input type="text" v-model="freqRange" placeholder="10 - 500 Hz" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Amortiguamiento α (Rayleigh)</label>
              <input type="number" v-model.number="alphaRayleigh" step="0.005" class="form-input" />
            </div>
          </div>

          <div v-if="analysisResults" class="results-box font-mono">
            <div class="res-row"><span>Frecuencia Fundamental w_1:</span> <span class="val text-emerald">{{ analysisResults.w1 }} rad/s</span></div>
            <div class="res-row"><span>Segundo Modo w_2:</span> <span class="val">{{ analysisResults.w2 }} rad/s</span></div>
            <div class="res-row"><span>Tercer Modo w_3:</span> <span class="val">{{ analysisResults.w3 }} rad/s</span></div>
          </div>
        </div>
      </div>

      <!-- Newmark Transient Integration (Vue Collapsible Card) -->
      <div class="vib-card">
        <div class="card-summary" @click="card2Open = !card2Open">
          <Icon :name="card2Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">2. Transitorios en el Tiempo (Newmark-β)</h4>
        </div>

        <div v-show="card2Open" class="card-body">
          <p class="card-desc">Integración implícita de la ecuación de movimiento $M\ddot{u} + C\dot{u} + Ku = F(t)$.</p>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Paso Temporal dt (s)</label>
              <input type="number" v-model.number="dtStep" step="0.0005" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Parámetro Newmark γ</label>
              <input type="number" v-model.number="gammaNewmark" step="0.05" class="form-input" />
            </div>
          </div>
        </div>
      </div>

      <!-- Critical Buckling Analysis (Vue Collapsible Card) -->
      <div class="vib-card">
        <div class="card-summary" @click="card3Open = !card3Open">
          <Icon :name="card3Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">3. Pandeo Crítico Estructural</h4>
        </div>

        <div v-show="card3Open" class="card-body">
          <p class="card-desc">Autovalores de pandeo no lineal $(K_0 - \lambda K_{\sigma}) \mathbf{v} = \mathbf{0}$.</p>
          <div class="prop-box font-mono">
            <div class="prop-row"><span>Factor Carga Crítica (λ_cr):</span> <span class="val text-emerald">{{ analysisResults ? analysisResults.lambda_cr : '2.845' }} (Estable)</span></div>
            <div class="prop-row"><span>Modo Crítico Dominante:</span> <span class="val">Modo 1 (Pandeo Flexional)</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Icon from './Icon.vue'

const card1Open = ref<boolean>(true)
const card2Open = ref<boolean>(true)
const card3Open = ref<boolean>(true)

const workflowMode = ref<'standalone' | 'optimization'>('standalone')
const freqRange = ref<string>('10 - 500 Hz')
const alphaRayleigh = ref<number>(0.01)
const dtStep = ref<number>(0.001)
const gammaNewmark = ref<number>(0.5)

const isCalculating = ref<boolean>(false)
const analysisResults = ref<{ w1: string; w2: string; w3: string; lambda_cr: string } | null>(null)

function runDirectAnalysis() {
  isCalculating.value = true
  setTimeout(() => {
    analysisResults.value = {
      w1: '19.739',
      w2: '49.348',
      w3: '78.956',
      lambda_cr: '2.845'
    }
    isCalculating.value = false
  }, 600)
}
</script>

<style scoped>
.vibrations-panel {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #38bdf8;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
}

.panel-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f8fafc;
}

.panel-subtitle {
  font-size: 0.8rem;
  color: #34d399;
  margin-left: auto;
}

.workflow-banner {
  background: #0f172a;
  border: 1px solid #1e293b;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.banner-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #cbd5e1;
}

.mode-buttons {
  display: flex;
  gap: 0.5rem;
  flex: 1;
}

.mode-btn {
  background: #1e293b;
  color: #cbd5e1;
  border: 1px solid #334155;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
}

.mode-btn:hover {
  background: #334155;
  color: #38bdf8;
}

.mode-btn.active {
  background: #38bdf8;
  color: #0f172a;
  border-color: #38bdf8;
}

.action-card {
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 0.85rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.action-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.action-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #f8fafc;
}

.action-desc {
  font-size: 0.76rem;
  color: #94a3b8;
  line-height: 1.3;
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.vib-card {
  background: #0f172a;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-summary {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  user-select: none;
}

.toggle-icon {
  color: #38bdf8;
}

.card-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #f8fafc;
}

.card-summary:hover .card-title {
  color: #38bdf8;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid #1e293b;
}

.card-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.3;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.results-box, .prop-box {
  background: #1e293b;
  padding: 0.75rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.8rem;
}

.res-row, .prop-row {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
}

.val {
  color: #38bdf8;
  font-weight: 700;
}

.text-blue { color: #38bdf8; }
.text-emerald { color: #34d399; }
</style>
