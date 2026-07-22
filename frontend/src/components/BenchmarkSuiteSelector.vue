<template>
  <div class="benchmark-selector glass-panel">
    <div class="header">
      <Icon name="layers" :size="20" />
      <h3 class="title">Biblioteca Completa de Benchmarks y Casos de Verificación Académica</h3>
      <span class="subtitle">12 Pruebas de literatura con parámetros autocompletados para todos los modos de trabajo</span>
    </div>

    <!-- Category Filter Tabs -->
    <div class="category-tabs">
      <button
        @click="selectedCategory = 'all'"
        class="cat-btn"
        :class="{ active: selectedCategory === 'all' }"
      >
        Todas (12)
      </button>
      <button
        @click="selectedCategory = 'direct'"
        class="cat-btn"
        :class="{ active: selectedCategory === 'direct' }"
      >
        1. IGA Directo & Frecuencias
      </button>
      <button
        @click="selectedCategory = 'vibrations'"
        class="cat-btn"
        :class="{ active: selectedCategory === 'vibrations' }"
      >
        2. Dinámica & Pandeo
      </button>
      <button
        @click="selectedCategory = 'materials'"
        class="cat-btn"
        :class="{ active: selectedCategory === 'materials' }"
      >
        3. Compuestos & FGM
      </button>
      <button
        @click="selectedCategory = 'frontier'"
        class="cat-btn"
        :class="{ active: selectedCategory === 'frontier' }"
      >
        4. Vanguardia & Pareto
      </button>
    </div>

    <div class="cards-grid">
      <!-- 1. Leissa Analytical -->
      <div v-if="matchCategory('direct')" class="bench-card" @click="selectBenchmark('leissa_analytical')">
        <div class="card-badge font-mono">Leissa (1969) — Analítico</div>
        <h4 class="card-name">1. Verificación Analítica de Frecuencias (SSSS)</h4>
        <p class="card-desc">Frecuencia propia fundamental exacta en placa simplemente apoyada sin orificios.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Modo 11 Teórico:</span> <span class="val">w_bar = 19.7392</span></div>
          <div class="prop-row"><span>Modo 12 Teórico:</span> <span class="val">w_bar = 49.3480</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-blue">IGA Directo</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 2. Shufrin L-Plate -->
      <div v-if="matchCategory('direct')" class="bench-card" @click="selectBenchmark('shufrin')">
        <div class="card-badge font-mono">Shufrin & Eisenberger (2005)</div>
        <h4 class="card-name">2. Placa en Forma de L (Esquina 270°)</h4>
        <p class="card-desc">Evaluación de singularidades de tensión y frecuencias en dominio en L.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Frecuencia Teórica:</span> <span class="val">w_bar = 13.52</span></div>
          <div class="prop-row"><span>Geometría:</span> <span class="val">Esquina 270°</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-blue">IGA Directo</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 3. Cho & Roh Perforated -->
      <div v-if="matchCategory('direct')" class="bench-card" @click="selectBenchmark('cho_roh')">
        <div class="card-badge font-mono">Cho & Roh (2003)</div>
        <h4 class="card-name">3. Placa Perforada con Orificio Circular</h4>
        <p class="card-desc">Concentración de tensiones K_t=3.0 y frecuencia fundamental con d/a = 0.3.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Frecuencia Teórica:</span> <span class="val">w_bar = 20.95</span></div>
          <div class="prop-row"><span>Orificio:</span> <span class="val">d/a = 0.30</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-blue">IGA Directo</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 4. Leissa Buckling -->
      <div v-if="matchCategory('vibrations')" class="bench-card" @click="selectBenchmark('leissa_buckling')">
        <div class="card-badge font-mono">Leissa & Ayoub (1988)</div>
        <h4 class="card-name">4. Pandeo Crítico por Carga Concentrada</h4>
        <p class="card-desc">Autovalores de rigidez geométrica (K0 - lambda*Ksigma) v = 0.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Carga Crítica λ_cr:</span> <span class="val">5.0 (Estable)</span></div>
          <div class="prop-row"><span>Tipo Carga:</span> <span class="val">Neumann Concentrada</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-amber">Vibraciones & Pandeo</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 5. Dynamic FRF Spectrum -->
      <div v-if="matchCategory('vibrations')" class="bench-card" @click="selectBenchmark('frf_spectrum')">
        <div class="card-badge font-mono">Dynamic Mechanics</div>
        <h4 class="card-name">5. Respuesta Armónica FRF & Newmark-β</h4>
        <p class="card-desc">Espectro dinámico de amplitud con amortiguamiento de Rayleigh (alpha, beta).</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Rango Frecuencia:</span> <span class="val">10 - 500 Hz</span></div>
          <div class="prop-row"><span>Integración:</span> <span class="val">Newmark Implícito</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-amber">Vibraciones & Dynamic</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 6. Laminated Composite ABD -->
      <div v-if="matchCategory('materials')" class="bench-card" @click="selectBenchmark('laminated_abd')">
        <div class="card-badge font-mono">Thai et al. (2012)</div>
        <h4 class="card-name">6. Placa Laminada Compuesta [0°/90°]s</h4>
        <p class="card-desc">Tensor constitutivo ABD con acoplamiento flexión-torsión nulo (Bij = 0).</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Apilamiento:</span> <span class="val">[0° / 90° / 0°] Cross-ply</span></div>
          <div class="prop-row"><span>Acoplamiento Bij:</span> <span class="val">0.0 (Simétrico)</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-purple">Materiales & Sizing</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 7. FGM Power-Law Gradient -->
      <div v-if="matchCategory('materials')" class="bench-card" @click="selectBenchmark('fgm_power_law')">
        <div class="card-badge font-mono">Tornabene (2014)</div>
        <h4 class="card-name">7. Material de Gradiente Funcional (FGM)</h4>
        <p class="card-desc">Variación continua de propiedades E(z) mediante ley de potencia de volumen.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Índice Ley Potencia:</span> <span class="val">k = 1.0</span></div>
          <div class="prop-row"><span>Rigidez Deq:</span> <span class="val">Integral Cerrada</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-purple">Materiales & Combined</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 8. Auxetic Negative Poisson -->
      <div v-if="matchCategory('materials')" class="bench-card" @click="selectBenchmark('auxetic')">
        <div class="card-badge font-mono">Lakes (1987) / Novák (2020)</div>
        <h4 class="card-name">8. Metamaterial Auxético (Poisson ν = -0.5)</h4>
        <p class="card-desc">Rigidez flexional incrementada (+21.3%) debido a deformación lateral invertida.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Poisson nu:</span> <span class="val">-0.50 (Auxético)</span></div>
          <div class="prop-row"><span>Rigidez D_aux:</span> <span class="val">+21.3% Incremento</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-purple">Materiales & Shape</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 9. Sigmund Phononic Bandgap -->
      <div v-if="matchCategory('frontier')" class="bench-card" @click="selectBenchmark('sigmund')">
        <div class="card-badge font-mono">Sigmund (2003)</div>
        <h4 class="card-name">9. Cristal Fonónico de Atenuación Fonónica</h4>
        <p class="card-desc">Maximización del ancho de banda relativo B_rel para bloqueo de ondas de vibración.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Banda Prohibida:</span> <span class="val">B_rel = 40.0%</span></div>
          <div class="prop-row"><span>Estructura:</span> <span class="val">Topología SIMP</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-emerald">Optimización Topológica</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 10. Piezoelectric Harvester -->
      <div v-if="matchCategory('frontier')" class="bench-card" @click="selectBenchmark('piezo_harvester')">
        <div class="card-badge font-mono">TMEC-IGA (2024)</div>
        <h4 class="card-name">10. Recolector Piezoeléctrico (PZT-5H PEH)</h4>
        <p class="card-desc">Generación de voltaje por acoplamiento termo-electro-mecánico.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Voltaje PZT:</span> <span class="val">12.45 V</span></div>
          <div class="prop-row"><span>Permitividad e33:</span> <span class="val">1.30e-8 F/m</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-emerald">Vanguardia 2024</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 11. Phase-Field Fracture -->
      <div v-if="matchCategory('frontier')" class="bench-card" @click="selectBenchmark('phase_field_crack')">
        <div class="card-badge font-mono">Phase-Field IGA (2025)</div>
        <h4 class="card-name">11. Fractura por Campo de Fase de Grieta</h4>
        <p class="card-desc">Evolución continua del campo de daño d en [0, 1] mediante THB-splines adaptativas.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Escala l0:</span> <span class="val">2.0 mm</span></div>
          <div class="prop-row"><span>Tenacidad Gc:</span> <span class="val">2700 J/m²</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-emerald">Vanguardia 2025</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>

      <!-- 12. Geo-FNO Neural Acceleration -->
      <div v-if="matchCategory('frontier')" class="bench-card" @click="selectBenchmark('geo_fno_neural')">
        <div class="card-badge font-mono">Geo-FNO (2025)</div>
        <h4 class="card-name">12. Aceleración Neural Espectral Geo-FNO</h4>
        <p class="card-desc">Inferencia ultrarrápida de ecuaciones diferenciales parciales a 100x velocidad.</p>
        <div class="target-box font-mono">
          <div class="prop-row"><span>Tiempo Inferencia:</span> <span class="val">0.42 ms (&lt; 1 ms)</span></div>
          <div class="prop-row"><span>Factor Velocidad:</span> <span class="val">100x Aceleración</span></div>
          <div class="prop-row"><span>Modo Trabajo:</span> <span class="val text-emerald">Vanguardia 2025</span></div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block">Cargar y Autocompletar</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Icon from './Icon.vue'

const selectedCategory = ref<string>('all')

const emit = defineEmits<{
  (e: 'load-benchmark', benchmarkId: string): void
}>()

function matchCategory(cat: string): boolean {
  if (selectedCategory.value === 'all') return true
  return selectedCategory.value === cat
}

function selectBenchmark(id: string) {
  emit('load-benchmark', id)
}
</script>

<style scoped>
.benchmark-selector {
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
  color: #94a3b8;
  margin-left: auto;
}

.category-tabs {
  display: flex;
  gap: 0.5rem;
}

.cat-btn {
  background: #0f172a;
  color: #cbd5e1;
  border: 1px solid #1e293b;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cat-btn:hover {
  background: #1e293b;
  color: #38bdf8;
}

.cat-btn.active {
  background: #38bdf8;
  color: #0f172a;
  border-color: #38bdf8;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.bench-card {
  background: #0f172a;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #38bdf8;
    transform: translateY(-2px);
  }
}

.card-badge {
  font-size: 0.7rem;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  width: fit-content;
}

.card-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: #f8fafc;
}

.card-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.3;
}

.target-box {
  background: #1e293b;
  padding: 0.6rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.75rem;
}

.prop-row {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
}

.val {
  color: #34d399;
  font-weight: 700;
}

.text-blue { color: #38bdf8; }
.text-amber { color: #fbbf24; }
.text-purple { color: #c084fc; }
.text-emerald { color: #34d399; }

.btn-block {
  width: 100%;
  justify-content: center;
}

.btn-sm {
  padding: 0.35rem 0.75rem !important;
  font-size: 0.75rem !important;
}
</style>
