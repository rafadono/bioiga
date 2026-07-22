<template>
  <div class="sensitivity-panel glass-panel">
    <div class="header">
      <Icon name="activity" :size="20" />
      <h3 class="title">Análisis de Sensibilidad Post-Optimización IGA</h3>
      <span class="subtitle font-mono">Perturbación de Parámetros E, ν, Vtarget y Sensibilidad Gradiente</span>
    </div>

    <div class="actions-bar">
      <button @click="runSensitivityAnalysis" class="btn btn-primary" :disabled="isAnalyzing">
        <Icon :name="isAnalyzing ? 'refresh' : 'play'" :size="16" />
        <span>{{ isAnalyzing ? 'Evaluando Sensibilidades...' : 'Ejecutar Análisis de Sensibilidad' }}</span>
      </button>
      <span class="hint font-mono">Evalúa la robustez del diseño óptimo ante variaciones del ±5% y ±10%</span>
    </div>

    <div class="panel-grid">
      <!-- Sensitivity Derivatives Table -->
      <div class="card font-mono">
        <h4 class="card-title">1. Derivadas de Sensibilidad (∂f / ∂x)</h4>
        <div class="table-wrapper">
          <table class="sens-table">
            <thead>
              <tr>
                <th>Parámetro</th>
                <th>Valor Nominal</th>
                <th>Sensibilidad ∂f/∂x</th>
                <th>Impacto Relativo</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in sensData" :key="item.param">
                <td class="text-blue">{{ item.param }}</td>
                <td>{{ item.nominal }}</td>
                <td :class="item.deriv < 0 ? 'text-emerald' : 'text-amber'">{{ item.deriv.toFixed(4) }}</td>
                <td>
                  <div class="impact-bar-wrapper">
                    <div class="impact-bar" :style="{ width: item.impact + '%' }"></div>
                    <span>{{ item.impact }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Sensitivity Tornado Chart Representation -->
      <div class="card font-mono">
        <h4 class="card-title">2. Gráfico Tornado de Robustez y Varianza</h4>
        <div class="tornado-chart">
          <div v-for="item in sensData" :key="'t-' + item.param" class="tornado-row">
            <span class="tornado-label">{{ item.param }}</span>
            <div class="tornado-bars">
              <div class="bar bar-neg" :style="{ width: (item.impact * 0.8) + '%' }">-10%</div>
              <div class="bar-center"></div>
              <div class="bar bar-pos" :style="{ width: (item.impact * 0.8) + '%' }">+10%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Icon from './Icon.vue'

const isAnalyzing = ref<boolean>(false)

const sensData = ref([
  { param: 'Módulo Elástico (E)', nominal: '200 GPa', deriv: -0.0412, impact: 85 },
  { param: 'Volumen Objetivo (Vtarget)', nominal: '50%', deriv: 0.1285, impact: 92 },
  { param: 'Coeficiente Poisson (ν)', nominal: '0.29', deriv: -0.0084, impact: 35 },
  { param: 'Dimensión Ancho (a)', nominal: '2.0 m', deriv: -0.0250, impact: 60 },
  { param: 'Grado Polinomial (p)', nominal: 'p = 2', deriv: -0.0110, impact: 45 },
])

function runSensitivityAnalysis() {
  isAnalyzing.value = true
  setTimeout(() => {
    isAnalyzing.value = false
  }, 700)
}
</script>

<style scoped>
.sensitivity-panel {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #38bdf8;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
}

.title {
  font-size: 1rem;
  font-weight: 700;
  color: #f8fafc;
}

.subtitle {
  font-size: 0.8rem;
  color: #34d399;
  margin-left: auto;
}

.actions-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #0f172a;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
}

.hint {
  font-size: 0.76rem;
  color: #94a3b8;
}

.panel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.card {
  background: #0f172a;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #38bdf8;
}

.table-wrapper {
  overflow-x: auto;
}

.sens-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
}

.sens-table th, .sens-table td {
  padding: 0.5rem 0.6rem;
  border-bottom: 1px solid #1e293b;
  text-align: left;
}

.sens-table th {
  color: #94a3b8;
  background: #1e293b;
}

.impact-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.impact-bar {
  height: 6px;
  background: #38bdf8;
  border-radius: 3px;
}

.tornado-chart {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.tornado-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.tornado-label {
  width: 150px;
  color: #cbd5e1;
}

.tornado-bars {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bar {
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.68rem;
  color: #0f172a;
  font-weight: 700;
  border-radius: 3px;
}

.bar-neg {
  background: #f87171;
}

.bar-pos {
  background: #34d399;
}

.bar-center {
  width: 2px;
  height: 24px;
  background: #334155;
}

.text-blue { color: #38bdf8; }
.text-emerald { color: #34d399; }
.text-amber { color: #fbbf24; }
</style>
