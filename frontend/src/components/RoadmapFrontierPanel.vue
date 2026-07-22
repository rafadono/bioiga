<template>
  <div class="frontier-panel glass-panel">
    <div class="panel-header">
      <Icon name="cpu" :size="20" />
      <h3 class="panel-title">Módulos de la Frontera del Conocimiento (Hoja de Ruta 2024–2026)</h3>
      <span class="panel-subtitle">Piezoeléctricos PZT, Campo de Fase, Level-Set y Fourier Neural Operators (Geo-FNO)</span>
    </div>

    <div class="panel-grid">
      <!-- 1. TMEC-IGA Piezoelectric (Vue Collapsible Card) -->
      <div class="frontier-card">
        <div class="card-summary" @click="card1Open = !card1Open">
          <Icon :name="card1Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">1. Acoplamiento Piezoeléctrico PZT-5H (TMEC-IGA)</h4>
        </div>

        <div v-show="card1Open" class="card-body">
          <p class="card-desc">Control activo de vibraciones y recolectores de energía PEH.</p>
          <div class="prop-box font-mono">
            <div class="prop-row"><span>Sensor Voltaje PZT:</span> <span class="val text-emerald">12.45 V</span></div>
            <div class="prop-row"><span>Permitividad ε33:</span> <span class="val">1.30e-8 F/m</span></div>
          </div>
        </div>
      </div>

      <!-- 2. Phase-Field Fracture (Vue Collapsible Card) -->
      <div class="frontier-card">
        <div class="card-summary" @click="card2Open = !card2Open">
          <Icon :name="card2Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">2. Fractura por Campo de Fase (Phase-Field IGA)</h4>
        </div>

        <div v-show="card2Open" class="card-body">
          <p class="card-desc">Propagación adaptativa de grietas mediante THB-splines con longitud $l_0$.</p>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Escala l0 (mm)</label>
              <input type="number" v-model.number="l0Scale" step="0.5" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Tenacidad Gc (J/m²)</label>
              <input type="number" v-model.number="gcToughness" step="100" class="form-input" />
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Level Set Method (Vue Collapsible Card) -->
      <div class="frontier-card">
        <div class="card-summary" @click="card3Open = !card3Open">
          <Icon :name="card3Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">3. Conjuntos de Nivel Imersos (Level Set LSM-IGA)</h4>
        </div>

        <div v-show="card3Open" class="card-body">
          <p class="card-desc">Fronteras CAD suaves 0/1 libres de densidades grises intermedias.</p>
          <div class="form-group">
            <label class="form-label">Paso Advectivo dt (Hamilton-Jacobi)</label>
            <input type="number" v-model.number="lsmDt" step="0.01" class="form-input" />
          </div>
        </div>
      </div>

      <!-- 4. Geo-FNO Neural Operator (Vue Collapsible Card) -->
      <div class="frontier-card">
        <div class="card-summary" @click="card4Open = !card4Open">
          <Icon :name="card4Open ? 'chevron-down' : 'chevron-right'" :size="16" class="toggle-icon" />
          <h4 class="card-title">4. Fourier Neural Operators (Geo-FNO)</h4>
        </div>

        <div v-show="card4Open" class="card-body">
          <p class="card-desc">Aceleración espectral por redes neuronales iFFT a 100× velocidad.</p>
          <div class="prop-box font-mono">
            <div class="prop-row"><span>Inferencia Espectral:</span> <span class="val text-emerald">0.42 ms (&lt; 1 ms)</span></div>
            <div class="prop-row"><span>Factor de Aceleración:</span> <span class="val">100x respecto a IGA directo</span></div>
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
const card4Open = ref<boolean>(true)

const l0Scale = ref<number>(2.0)
const gcToughness = ref<number>(2700.0)
const lsmDt = ref<number>(0.1)
</script>

<style scoped>
.frontier-panel {
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
  color: #94a3b8;
  margin-left: auto;
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.frontier-card {
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

.prop-box {
  background: #1e293b;
  padding: 0.75rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.8rem;
}

.prop-row {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
}

.val {
  color: #38bdf8;
  font-weight: 700;
}

.text-emerald {
  color: #34d399;
}
</style>
