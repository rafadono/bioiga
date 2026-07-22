<template>
  <div class="advanced-panel glass-panel">
    <div class="panel-header">
      <Icon name="cpu" :size="20" />
      <h3 class="panel-title">Módulos Avanzados de Ciencia y Materiales IGA</h3>
    </div>

    <div class="panel-grid">
      <!-- 1. k-Refinement (Vue Collapsible Card) -->
      <div class="science-card">
        <div class="card-summary" @click="card1Open = !card1Open">
          <Icon :name="card1Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">1. Refinamiento k-Refinement (IGA)</h4>
        </div>

        <div v-show="card1Open" class="card-body">
          <p class="card-desc">Elevación de grado polinomial $p \to p'$ e inserción de nudos $C^{p-1}$ continuos.</p>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nuevo Grado p</label>
              <input type="number" v-model.number="kDegreeP" min="2" max="5" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Nuevo Grado q</label>
              <input type="number" v-model.number="kDegreeQ" min="2" max="5" class="form-input" />
            </div>
          </div>
        </div>
      </div>

      <!-- 2. FGM & Laminated Composites (Vue Collapsible Card) -->
      <div class="science-card">
        <div class="card-summary" @click="card2Open = !card2Open">
          <Icon :name="card2Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">2. Placas Compuestas Laminadas & FGM</h4>
        </div>

        <div v-show="card2Open" class="card-body">
          <p class="card-desc">Materiales de Gradiente Funcional y matrices constitucionales ABD.</p>
          <div class="form-group">
            <label class="form-label">Secuencia de Apilamiento</label>
            <select v-model="stacking" class="form-select">
              <option value="cross">[0° / 90° / 0°] Cross-ply</option>
              <option value="angle">[45° / -45° / 45°] Angle-ply</option>
              <option value="quasi">[0° / 45° / 90° / -45°] Quasi-isotrópico</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Índice de Ley de Potencia FGM (k)</label>
            <div class="range-number-pair">
              <input type="range" v-model.number="fgmIndex" min="0.1" max="10.0" step="0.1" class="range-input" />
              <input type="number" v-model.number="fgmIndex" min="0.0" max="20.0" step="0.1" class="form-input num-box" />
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Memetic & RL Options (Vue Collapsible Card) -->
      <div class="science-card">
        <div class="card-summary" @click="card3Open = !card3Open">
          <Icon :name="card3Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">3. Algoritmo Memético & RL</h4>
        </div>

        <div v-show="card3Open" class="card-body">
          <p class="card-desc">Búsqueda local por sensibilidad (OC / MMA) y agente Q-Learning de topología.</p>
          <div class="toggle-group">
            <label class="toggle-label">
              <input type="checkbox" v-model="enableMemetic" />
              <span>Hibridación Memética (Gradiente local OC)</span>
            </label>
          </div>
          <div class="toggle-group">
            <label class="toggle-label">
              <input type="checkbox" v-model="enableRL" />
              <span>Agente RL Q-Learning de Topología</span>
            </label>
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

const kDegreeP = ref<number>(3)
const kDegreeQ = ref<number>(3)
const stacking = ref<string>('cross')
const fgmIndex = ref<number>(1.0)
const enableMemetic = ref<boolean>(true)
const enableRL = ref<boolean>(false)
</script>

<style scoped>
.advanced-panel {
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

.panel-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.science-card {
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
  transition: transform 0.2s ease;
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
  margin-top: 0.2rem;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: #cbd5e1;
  cursor: pointer;
}
</style>
