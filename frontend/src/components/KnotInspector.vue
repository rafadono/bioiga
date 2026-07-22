<template>
  <div class="knot-inspector glass-panel">
    <div class="inspector-header">
      <h3 class="inspector-title">Inspección de Vectores de Nudos y Geometría NURBS</h3>
      <span class="inspector-badge font-mono">p = {{ p }}, q = {{ q }}</span>
    </div>

    <div class="inspector-grid">
      <!-- Knot Vector U -->
      <div class="knot-card">
        <label class="form-label">Vector de Nudos U (Dirección u)</label>
        <div class="knot-chips">
          <span v-for="(val, idx) in knotU" :key="'u-' + idx" class="knot-chip font-mono">
            {{ val.toFixed(2) }}
          </span>
        </div>
        <span class="knot-hint">Multiplicidad en extremos = p + 1 ({{ p + 1 }})</span>
      </div>

      <!-- Knot Vector V -->
      <div class="knot-card">
        <label class="form-label">Vector de Nudos V (Dirección v)</label>
        <div class="knot-chips">
          <span v-for="(val, idx) in knotV" :key="'v-' + idx" class="knot-chip font-mono">
            {{ val.toFixed(2) }}
          </span>
        </div>
        <span class="knot-hint">Multiplicidad en extremos = q + 1 ({{ q + 1 }})</span>
      </div>
    </div>

    <div class="knot-spans-info">
      <h4 class="sub-title">Tramos de Nudos (Knot Spans / Elementos IGA)</h4>
      <p class="span-description">
        En IGA, cada par de nudos continuos <code>[u_i, u_{i+1}] × [v_j, v_{j+1}]</code> define un elemento de integración paramétrico continuo, eliminando errores de malla.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const p = ref<number>(2)
const q = ref<number>(2)
const knotU = ref<number[]>([0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0])
const knotV = ref<number[]>([0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0])
</script>

<style scoped>
.knot-inspector {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.inspector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
}

.inspector-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f8fafc;
}

.inspector-badge {
  font-size: 0.8rem;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.inspector-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.knot-card {
  background: #0f172a;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.knot-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.knot-chip {
  background: #1e293b;
  color: #38bdf8;
  font-weight: 600;
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #334155;
}

.knot-hint {
  font-size: 0.75rem;
  color: #64748b;
}

.knot-spans-info {
  background: rgba(15, 23, 42, 0.6);
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
}

.sub-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 0.35rem;
}

.span-description {
  font-size: 0.8rem;
  color: #94a3b8;
  line-height: 1.4;
}

code {
  font-family: 'JetBrains Mono', monospace;
  color: #38bdf8;
  background: #0f172a;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
}
</style>
