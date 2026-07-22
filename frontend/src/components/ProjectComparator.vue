<template>
  <div class="project-comparator glass-panel">
    <div class="header">
      <Icon name="layers" :size="20" />
      <h3 class="title">Matriz Comparativa de Resultados entre Proyectos y Casos</h3>
      <span class="subtitle font-mono">Comparación Lado a Lado de Frecuencias, Cargas y Fitness</span>
    </div>

    <!-- Project Selection Checklist -->
    <div class="selector-box">
      <span class="box-label">Seleccionar Proyectos a Comparar:</span>
      <div class="checkbox-group">
        <label v-for="proj in availableProjects" :key="proj.id" class="checkbox-label font-mono">
          <input type="checkbox" :value="proj.id" v-model="selectedProjectIds" />
          <span>{{ proj.name }}</span>
        </label>
      </div>
    </div>

    <!-- Multi-Project Side-by-Side Comparison Table -->
    <div class="table-card font-mono">
      <h4 class="card-title">Matriz de Desempeño Comparativo</h4>
      <div class="table-wrapper">
        <table class="comp-table">
          <thead>
            <tr>
              <th>Métrica de Desempeño</th>
              <th v-for="proj in activeProjectsList" :key="proj.id" class="text-blue">
                {{ proj.name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Algoritmo Usado</td>
              <td v-for="proj in activeProjectsList" :key="proj.id" class="val text-emerald">
                {{ proj.algorithm }}
              </td>
            </tr>
            <tr>
              <td>Frecuencia Fundamental (w_1)</td>
              <td v-for="proj in activeProjectsList" :key="proj.id" class="val">
                {{ proj.w1 }} rad/s
              </td>
            </tr>
            <tr>
              <td>Carga Crítica Pandeo (λ_cr)</td>
              <td v-for="proj in activeProjectsList" :key="proj.id" class="val text-amber">
                {{ proj.lambda_cr }}
              </td>
            </tr>
            <tr>
              <td>Fitness Óptimo (Compliancia)</td>
              <td v-for="proj in activeProjectsList" :key="proj.id" class="val">
                {{ proj.fitness }}
              </td>
            </tr>
            <tr>
              <td>Fracción Volumen (Vtarget)</td>
              <td v-for="proj in activeProjectsList" :key="proj.id" class="val">
                {{ proj.target_vol }}%
              </td>
            </tr>
            <tr>
              <td>Evaluaciones IGA Totales</td>
              <td v-for="proj in activeProjectsList" :key="proj.id" class="val">
                {{ proj.evals }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Icon from './Icon.vue'

const availableProjects = ref([
  { id: 'p1', name: 'Placa_Cantilever_MPMBPSO', algorithm: 'MPMBPSO', w1: '19.739', lambda_cr: '2.845', fitness: '0.00248', target_vol: 50, evals: 1000 },
  { id: 'p2', name: 'Placa_Perforada_MPGA', algorithm: 'MPGA', w1: '20.950', lambda_cr: '3.120', fitness: '0.00215', target_vol: 45, evals: 1200 },
  { id: 'p3', name: 'Disco_Anular_MPBGWO', algorithm: 'MPBGWO', w1: '18.420', lambda_cr: '2.450', fitness: '0.00290', target_vol: 55, evals: 800 },
])

const selectedProjectIds = ref<string[]>(['p1', 'p2', 'p3'])

const activeProjectsList = computed(() => {
  return availableProjects.value.filter(p => selectedProjectIds.value.includes(p.id))
})
</script>

<style scoped>
.project-comparator {
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

.selector-box {
  background: #0f172a;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.box-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #cbd5e1;
}

.checkbox-group {
  display: flex;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: #38bdf8;
  cursor: pointer;
}

.table-card {
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

.comp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
}

.comp-table th, .comp-table td {
  padding: 0.6rem 0.8rem;
  border-bottom: 1px solid #1e293b;
  text-align: left;
}

.comp-table th {
  background: #1e293b;
}

.val {
  font-weight: 700;
  color: #f8fafc;
}

.text-blue { color: #38bdf8; }
.text-emerald { color: #34d399; }
.text-amber { color: #fbbf24; }
</style>
