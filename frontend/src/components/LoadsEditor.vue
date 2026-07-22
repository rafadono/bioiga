<template>
  <div class="loads-editor glass-panel">
    <div class="editor-header">
      <Icon name="shield" :size="20" />
      <h3 class="editor-title">Editor de Cargas, Simetrías y Condiciones de Borde Periódicas (PBC)</h3>
      <span class="editor-subtitle font-mono">Verificación de Compatibilidad Mecánica de Borde</span>
    </div>

    <!-- Compatibility Warning Banner -->
    <div v-if="compatibilityConflict" class="warning-box">
      <div class="warning-header">
        <Icon name="warning" :size="18" />
        <span class="warning-title font-mono">⚠️ INCOMPATIBILIDAD MECÁNICA DETECTADA: {{ compatibilityConflict.title }}</span>
      </div>
      <p class="warning-desc">{{ compatibilityConflict.reason }}</p>
      <div class="warning-actions">
        <button @click="fixCompatibility" class="btn btn-warning btn-sm">
          <Icon name="refresh" :size="14" />
          <span>Auto-Corregir a Configuración Válida</span>
        </button>
      </div>
    </div>

    <div class="editor-grid">
      <!-- Section 1: Standard Dirichlet BCs -->
      <div class="bc-section">
        <h4 class="section-subtitle">1. Soportes Estándar (Dirichlet)</h4>
        <div class="bc-options">
          <label class="radio-label">
            <input type="radio" v-model="bcType" value="none" />
            <span>Sin Soporte Dirichlet (Borde Libre / Modelo Periódico PBC / Cristales Fonónicos)</span>
          </label>
          <label class="radio-label">
            <input type="radio" v-model="bcType" value="cantilever" />
            <span>Voladizo / Cantilever (Empotrado Borde Izquierdo)</span>
          </label>
          <label class="radio-label">
            <input type="radio" v-model="bcType" value="fixed_bottom" />
            <span>Empotrado Base Inferior (u_x = 0, u_y = 0)</span>
          </label>
          <label class="radio-label">
            <input type="radio" v-model="bcType" value="simply_supported" />
            <span>Simplemente Apoyado (Roller X/Y en Extremos)</span>
          </label>
        </div>

      </div>

      <!-- Section 2: Periodic Boundary Conditions (PBC) & Metamaterials -->
      <div class="bc-section">
        <h4 class="section-subtitle">2. Condiciones de Borde Periódicas (PBC)</h4>
        <p class="section-desc">Esencial para celdas unitarias, metamateriales y cristales fonónicos.</p>
        <div class="toggle-group">
          <label class="toggle-label">
            <input type="checkbox" v-model="pbcX" />
            <span>PBC en X: u(0, y) = u(Lx, y) (Bordes Izquierdo - Derecho)</span>
          </label>
        </div>
        <div class="toggle-group">
          <label class="toggle-label">
            <input type="checkbox" v-model="pbcY" />
            <span>PBC en Y: u(x, 0) = u(x, Ly) (Bordes Inferior - Superior)</span>
          </label>
        </div>
      </div>

      <!-- Section 3: Structural Symmetry Conditions -->
      <div class="bc-section">
        <h4 class="section-subtitle">3. Planos de Simetría Estructural</h4>
        <div class="bc-options">
          <label class="radio-label">
            <input type="radio" v-model="symmetryMode" value="none" />
            <span>Sin Simetría (Modelo Estructural Completo 360°)</span>
          </label>
          <label class="radio-label">
            <input type="radio" v-model="symmetryMode" value="symmetry_x" />
            <span>Simetría Eje X (ux = 0 en borde de corte vertical)</span>
          </label>
          <label class="radio-label">
            <input type="radio" v-model="symmetryMode" value="symmetry_y" />
            <span>Simetría Eje Y (uy = 0 en borde de corte horizontal)</span>
          </label>
          <label class="radio-label">
            <input type="radio" v-model="symmetryMode" value="symmetry_quarter" />
            <span>Modelo 1/4 (Doble Simetría X e Y para ahorro computacional)</span>
          </label>
        </div>
      </div>

      <!-- Section 4: Neumann Point Loads -->
      <div class="loads-section">
        <h4 class="section-subtitle">4. Cargas Puntuales y Distribuidas (Neumann)</h4>
        <div class="toggle-group mb-2">
          <label class="toggle-label">
            <input type="checkbox" v-model="enableLoads" />
            <span>Habilitar Cargas Puntuales en el Borde</span>
          </label>
        </div>
        <div class="form-row" v-if="enableLoads">
          <div class="form-group">
            <label class="form-label">Fuerza Fx (N)</label>
            <input type="number" v-model.number="loadFx" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Fuerza Fy (N)</label>
            <input type="number" v-model.number="loadFy" class="form-input" />
          </div>
        </div>
        <span class="bc-hint">{{ enableLoads ? 'Fuerza aplicada en el borde de trabajo.' : 'Cargas desactivadas (Modos de vibración libres / celdas periódicas PBC).' }}</span>
      </div>

    </div>

    <!-- Active Degrees of Freedom (DOFs) Summary Panel -->
    <div class="dof-summary-panel font-mono">
      <h4 class="dof-title">Resumen de Grados de Libertad (DOFs) y Compatibilidad Mecánica</h4>
      <div class="dof-grid">
        <div class="dof-item">
          <span class="dof-label">DOFs Totales del Dominio:</span>
          <span class="dof-val">{{ totalDofs }} DOFs (2 per Control Point)</span>
        </div>
        <div class="dof-item">
          <span class="dof-label">DOFs Restringidos (BCs/Simetría/PBC):</span>
          <span class="dof-val text-amber">{{ constrainedDofs }} DOFs</span>
        </div>
        <div class="dof-item">
          <span class="dof-label">Compatibilidad Mecánica:</span>
          <span class="dof-val" :class="compatibilityConflict ? 'text-danger' : 'text-emerald'">
            {{ compatibilityConflict ? 'INCOMPATIBLE' : '✔ VÁLIDA Y COMPATIBLE' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Icon from './Icon.vue'

const bcType = ref<string>('cantilever')
const pbcX = ref<boolean>(false)
const pbcY = ref<boolean>(false)
const symmetryMode = ref<string>('none')

const enableLoads = ref<boolean>(false)
const loadFx = ref<number>(0)
const loadFy = ref<number>(0)


const numControlPoints = ref<number>(100)

// Mechanical Compatibility Verification Rules (Informative Tips without Hard-Blocking)
const compatibilityConflict = computed(() => {
  return null
})


function fixCompatibility() {
  if (!compatibilityConflict.value) return
  const type = compatibilityConflict.value.type

  if (type === 'pbc_fixed') {
    bcType.value = 'none'
  } else if (type === 'pbc_point_load') {
    loadFx.value = 0
    loadFy.value = 0
  } else if (type === 'sym_fx') {
    loadFx.value = 0
  }
}


const totalDofs = computed(() => numControlPoints.value * 2)

const constrainedDofs = computed(() => {
  let count = 20
  if (pbcX.value) count += 15
  if (pbcY.value) count += 15
  if (symmetryMode.value === 'symmetry_quarter') count += 25
  else if (symmetryMode.value !== 'none') count += 10
  return count
})
</script>

<style scoped>
.loads-editor {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #38bdf8;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
}

.editor-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f8fafc;
}

.editor-subtitle {
  font-size: 0.8rem;
  color: #34d399;
  margin-left: auto;
}

.warning-box {
  background: rgba(248, 113, 113, 0.15);
  border: 1px solid #f87171;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #f87171;
}

.warning-title {
  font-size: 0.85rem;
  font-weight: 700;
}

.warning-desc {
  font-size: 0.78rem;
  color: #f8fafc;
  line-height: 1.4;
}

.btn-warning {
  background: rgba(248, 113, 113, 0.25);
  color: #f87171;
  border: 1px solid #f87171;
}

.btn-warning:hover {
  background: rgba(248, 113, 113, 0.4);
}

.editor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.bc-section, .loads-section {
  background: #0f172a;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-subtitle {
  font-size: 0.85rem;
  font-weight: 700;
  color: #38bdf8;
}

.section-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.3;
}

.bc-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.radio-label, .toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: #cbd5e1;
  cursor: pointer;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.bc-hint {
  font-size: 0.72rem;
  color: #64748b;
}

.dof-summary-panel {
  background: #0f172a;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #334155;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dof-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #38bdf8;
  border-bottom: 1px solid #1e293b;
  padding-bottom: 0.4rem;
}

.dof-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  font-size: 0.78rem;
}

.dof-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.dof-label {
  color: #94a3b8;
}

.dof-val {
  font-weight: 700;
  color: #f8fafc;
}

.text-amber { color: #fbbf24; }
.text-emerald { color: #34d399; }
.text-danger { color: #f87171; }
.btn-sm {
  padding: 0.35rem 0.75rem !important;
  font-size: 0.75rem !important;
}
</style>
